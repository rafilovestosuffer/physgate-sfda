"""C87 Step 2 decision (written before BIST-W results existed).

For SDALR (final_checkpoint) and SHOT separately, over the 12 M1 clean tasks:
  recovers iff mean(BIST-W clean - baseline clean) >= 5 pp AND one-sided Wilcoxon p < 0.05
  guard: leaky mean must not drop by > 2 pp (otherwise reported as a trade-off)
Mechanism: within-class record probe on BIST-W source features (vs N1 baseline 507/508); per-bearing purity on clean targets.
Baselines: SDALR = physgate-m1-f{a,b} final_checkpoint; SHOT = physgate-shot-f{a,b}. Writes results/c87/C87_RESULT.md.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "results" / "artifacts"
TASKS = ["A1->A3", "A1->A2", "A3->A1", "A3->A2", "A2->A1", "A2->A3"]
OTHER = {"A": "B", "B": "A"}


def one(pattern):
    hits = [p for p in glob.glob(str(A / pattern), recursive=True)]
    if not hits:
        return None
    d = json.load(open(hits[0], encoding="utf-8"))
    return d if len(d.get("adapted", {})) == 6 else None


def vec(d):
    return np.array([d["adapted"][t] for t in TASKS])


def main():
    L = ["# C87 Step 2 — BIST-W (class-conditional bearing adversary)", ""]
    arms = {"SDALR": ("final_checkpoint", "physgate-m1-f{f}/**/result_PU_M1_final_checkpoint_F{F}to{T}_s2024.json"),
            "SHOT": ("shot", "physgate-shot-f{f}/**/result_PU_M1_shot_F{F}to{T}_s2024.json")}
    probes = []
    for name, (variant, base_pat) in arms.items():
        rows, missing = {"leak_b": [], "leak_w": [], "clean_b": [], "clean_w": []}, []
        for F in "AB":
            for T, kind in ((F, "leak"), (OTHER[F], "clean")):
                b = one(base_pat.format(f=F.lower(), F=F, T=T))
                w = one(f"physgate-run-bistw-f{F.lower()}/**/result_PU_M1_{variant}_F{F}to{T}_bist_s2024.json")
                if b is None or w is None:
                    missing.append(f"{F}->{T} {'base' if b is None else 'bistw'}")
                    continue
                rows[kind + "_b"].append(vec(b)); rows[kind + "_w"].append(vec(w))
                if w.get("bist", {}).get("probes"):
                    probes += w["bist"]["probes"]
        L.append(f"## {name}")
        if missing:
            L += [f"Missing: {missing}. **Decision pending.**", ""]
            continue
        cb, cw = np.concatenate(rows["clean_b"]), np.concatenate(rows["clean_w"])
        lb, lw = np.concatenate(rows["leak_b"]), np.concatenate(rows["leak_w"])
        gain = cw - cb
        p = wilcoxon(cw, cb, alternative="greater", zero_method="zsplit").pvalue
        rec = bool(gain.mean() >= 5 and p < 0.05)
        guard = bool(lb.mean() - lw.mean() <= 2)
        L += [f"| | baseline | BIST-W | Δ |", "|---|---|---|---|",
              f"| leaky mean | {lb.mean():.2f} | {lw.mean():.2f} | {lw.mean() - lb.mean():+.2f} |",
              f"| clean mean | {cb.mean():.2f} | {cw.mean():.2f} | {gain.mean():+.2f} |", "",
              f"Clean per-task gain: median {np.median(gain):+.2f}, range [{gain.min():+.2f}, {gain.max():+.2f}], positive {int((gain > 0).sum())}/12, "
              f"one-sided Wilcoxon p = {p:.4f} → **{'RECOVERS' if rec else 'DOES NOT RECOVER'}** (≥ 5 pp, p < 0.05). "
              f"Leaky guard (drop ≤ 2 pp): **{'OK' if guard else 'TRADE-OFF'}**.", ""]
    L.append("## Mechanism: within-class bearing-ID probe on BIST-W source features")
    if probes:
        k = sum(p["within_class"]["record_correct"] for p in probes if "within_class" in p)
        n = sum(p["within_class"]["record_n"] for p in probes if "within_class" in p)
        L.append(f"Within-class record accuracy {k}/{n} = {k / max(n, 1):.3f} (N1 baseline 507/508 = 0.998).")
    else:
        L.append("No BIST-W probe records yet.")
    out = ROOT / "results" / "c87" / "C87_RESULT.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
