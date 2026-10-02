"""C94 decision (written before any HUST result existed): does the PU leakage conclusion replicate on a second rig?

Unit = split (mean over its 6 load-pair tasks). Rule: replicates iff median split delta_leak >= 10 pp and one-sided
Wilcoxon p < 0.05 over the K splits. Reported either way. Writes results/c94/C94_RESULT.md.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "results" / "artifacts" / "physgate-run-hust-k6"
OUT = ROOT / "results" / "c94"
TASKS = ["H1->H3", "H1->H2", "H3->H1", "H3->H2", "H2->H1", "H2->H3"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    R = {}
    for p in glob.glob(str(A / "**" / "result_HUST_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("smoke") or len(d.get("adapted", {})) < 6:
            continue
        R[(d["src_fold"], d["tgt_fold"])] = np.array([d["adapted"][t] for t in TASKS])
    types = {}
    kl = list(A.rglob("kernel_log_hust.json"))
    if kl:
        k = json.load(open(kl[0], encoding="utf-8"))
        types = {f"H{i}": s for i, s in enumerate(k.get("splits", []))}
    views = sorted({s for s, _ in R} | {t.rstrip("c") for _, t in R})
    L = ["# C94 — HUST bearing: second-rig replication of the leakage design (PROTOCOL C94)", "",
         "SDALR final_checkpoint, seed 2024, L3 {normal, inner, outer}, domains = loads 0 / 200 / 400 W, Track R windows.",
         "Source = 3 bearing types, clean target = the other 2. A type-disjoint target changes bearing size as well as identity,",
         "so this is a stronger shift than Paderborn's and is reported as bearing identity **and** geometry.", "",
         "| split | source types (62xx) | leaky | clean | Δ_leak |", "|---|---|---|---|---|"]
    rows = []
    for v in views:
        if (v, v) in R and (v, v + "c") in R:
            lk, cl = R[(v, v)].mean(), R[(v, v + "c")].mean()
            rows.append((v, lk, cl))
            L.append(f"| {v} | {', '.join('620' + t for t in types.get(v, []))} | {lk:.2f} | {cl:.2f} | {lk - cl:.2f} |")
        else:
            L.append(f"| {v} | {', '.join('620' + t for t in types.get(v, []))} | missing | | |")
    if len(rows) >= 4:
        lk = np.array([r[1] for r in rows]); cl = np.array([r[2] for r in rows]); d = lk - cl
        p = wilcoxon(lk, cl, alternative="greater", zero_method="zsplit").pvalue
        ok = bool(np.median(d) >= 10 and p < 0.05)
        L += ["", f"**Decision:** median Δ_leak {np.median(d):.2f} pp [range {d.min():.2f}, {d.max():.2f}] over {len(rows)} splits, "
                  f"one-sided Wilcoxon p = {p:.4f} → **the Paderborn conclusion {'REPLICATES' if ok else 'DOES NOT REPLICATE'} on HUST** "
                  f"(C94 rule: median ≥ 10 pp and p < 0.05).",
              f"Mean leaky {lk.mean():.2f} %, mean clean {cl.mean():.2f} %."]
    else:
        L.append(f"\n**Decision pending:** {len(rows)} splits complete.")
    (OUT / "C94_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
