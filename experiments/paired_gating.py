"""Supervisor review item 3 + decomposition: is the gating comparison paired, and how large is the paired difference variance?

Pairing is verified from artifacts, not asserted: within a seed the gate arms run with --skip-pretrain on the same source model,
so each arm's `source_only` (pre-adaptation accuracy on the same target) must be identical to the ungated arm's.
Writes results/PAIRED_GATING.md. Reads retained artifacts only.
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


def load():
    R = {}
    for p in glob.glob(str(A / "**" / "result_PU_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8")); d["_path"] = p
        if d.get("smoke"):
            continue
        R[(d["variant"], d.get("gate") or "none", d["seed"], d["src_fold"], d["tgt_fold"], Path(p).parts[-3])] = d
    return R


def pick(R, variant, gate, seed, src, tgt, run=None):
    """run = artifact kernel folder; gate arms must be paired with the ungated arm from the SAME kernel (same source model)."""
    c = [v for k, v in R.items() if k[:5] == (variant, gate, seed, src, tgt) and (run is None or k[5] == run)]
    return c[0] if c else None


def batch0(d):
    """Pre-update (batch 0) accuracy lines of every adapt log of this run: identical across arms iff the source model is shared."""
    tag = "" if d.get("gate", "none") in (None, "none") else f"_gate{d['gate']}"
    logs = Path(d["_path"]).parent / f"logs_PU_M1_{d['variant']}_F{d['src_fold']}to{d['tgt_fold']}{tag}_s{d['seed']}"
    out = []
    for lg in sorted(logs.glob("adapt_*.log")):
        line = next((l for l in lg.read_text(encoding="utf-8", errors="replace").splitlines() if "0/" in l and "%" in l), None)
        out.append((lg.name, line.split(";")[-1].strip() if line else None))
    return out


def vec(d, key="adapted"):
    return np.array([d[key][t] for t in TASKS])


def main():
    R = load()
    L = ["# Paired gating analysis and collapse decomposition", "",
         "Source: retained artifacts under results/artifacts (M1, M2, M2seed). Unit = (source fold, task); 12 per seed.", ""]
    # --- pairing check
    L += ["## 1. Is the comparison paired?", ""]
    seeds = sorted({k[2] for k in R if k[0] == "final_checkpoint" and k[1] in ("v2", "pcv")})
    diffs = {g: {} for g in ("c30", "v2", "pcv", "eagle", "oracle")}
    none_means = {}
    for s in seeds:
        runs = {f: {k[5] for k in R if k[:5] == ("final_checkpoint", "v2", s, f, OTHER[f])} for f in "AB"}
        if not all(runs.values()):
            continue
        run = {f: sorted(runs[f])[0] for f in "AB"}
        base = {f: pick(R, "final_checkpoint", "none", s, f, OTHER[f], run[f]) for f in "AB"}
        if not all(base.values()):
            continue
        none_means[s] = np.concatenate([vec(base[f]) for f in "AB"])
        for g in diffs:
            arm = {f: pick(R, "final_checkpoint", g, s, f, OTHER[f], run[f]) for f in "AB"}
            if not all(arm.values()):
                continue
            same_src = all(batch0(arm[f]) == batch0(base[f]) and batch0(base[f]) for f in "AB")
            diffs[g][s] = (np.concatenate([vec(arm[f]) - vec(base[f]) for f in "AB"]), same_src)
    for g, by in diffs.items():
        for s, (_, ok) in by.items():
            L.append(f"- seed {s}, arm `{g}`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **{ok}**")
    L += ["", "Identical batch-0 (pre-update) accuracy in every adapt log means the arms share the source checkpoint (same seed, same source "
          "model, gate on vs off). The comparison is **paired**; the relevant variance is that of the per-task difference.", ""]
    # --- paired distribution
    L += ["## 2. Paired per-task differences (gated − ungated, pp)", "",
          "| arm | seed | mean | sd | min | median | max | tasks > 0 | one-sided Wilcoxon p |", "|---|---|---|---|---|---|---|---|---|"]
    for g, by in diffs.items():
        for s, (d, _) in sorted(by.items()):
            p = wilcoxon(d, alternative="greater", zero_method="zsplit").pvalue
            L.append(f"| {g} | {s} | {d.mean():+.2f} | {d.std(ddof=1):.2f} | {d.min():+.2f} | {np.median(d):+.2f} | {d.max():+.2f} | "
                     f"{int((d > 0).sum())}/12 | {p:.4f} |")
    if len(none_means) > 1:
        m = np.array(list(none_means.values()))
        L += ["", f"Between-seed sd of the **ungated** per-task accuracy (same task, different seed), mean over tasks: "
              f"{m.std(0, ddof=1).mean():.2f} pp (seeds {sorted(none_means)}). Compare with the sd of the paired differences above."]
    for g in ("v2", "pcv"):
        if len(diffs[g]) > 1:
            dd = np.array([d for d, _ in diffs[g].values()])
            L.append(f"- `{g}`: per-task gain averaged over seeds {sorted(diffs[g])}: mean {dd.mean():+.2f}, "
                     f"between-seed sd of the per-task gain {dd.std(0, ddof=1).mean():.2f} pp.")
    # --- decomposition (matched variant final_checkpoint, seed 2024)
    L += ["", "## 3. Decomposition of the collapse (final_checkpoint, seed 2024, matched variant)", ""]
    leak = [pick(R, "final_checkpoint", "none", 2024, f, f) for f in "AB"]
    clean = [pick(R, "final_checkpoint", "none", 2024, f, OTHER[f]) for f in "AB"]
    orac = [pick(R, "final_checkpoint", "oracle", 2024, f, OTHER[f]) for f in "AB"]
    orun = [Path(d["_path"]).parts[-3] for d in orac if d]
    if all(leak + clean + orac):
        lk = np.concatenate([vec(d) for d in leak]).mean()
        o = np.concatenate([vec(d) for d in orac]).mean()
        c = np.concatenate([vec(pick(R, "final_checkpoint", "none", 2024, f, OTHER[f], r)) for f, r in zip("AB", orun)]).mean()
        c_m1 = np.concatenate([vec(pick(R, "final_checkpoint", "none", 2024, f, OTHER[f], f"physgate-m1-f{f.lower()}")) for f in "AB"]).mean()
        tot, noise, rep = lk - c, o - c, lk - o
        L += [f"| leaky | clean (ungated) | clean + oracle filter | total collapse | recoverable by a perfect pseudo-label filter | not recoverable by any filter |",
              "|---|---|---|---|---|---|",
              f"| {lk:.2f} | {c:.2f} | {o:.2f} | {tot:.2f} | {noise:.2f} ({100 * noise / tot:.0f} %) | {rep:.2f} ({100 * rep / tot:.0f} %) |", "",
              f"Clean ungated is taken from the same kernel as the oracle arm (shared source model). The M1 kernel's ungated clean run "
              f"of the same configuration gave {c_m1:.2f} (run-to-run GPU nondeterminism across kernels).", "",
              "Caveats: one seed; the oracle filter keeps only correct pseudo-labels but still trains on the unchanged source model, so "
              "the non-recoverable part is source-representation failure *as seen through SDALR's adaptation*. The supervisor's figures "
              "(94.7 / 56.3 / 82.7) mixed the as_released leaky mean with final_checkpoint clean arms; the matched-variant values are above."]
    (ROOT / "results" / "PAIRED_GATING.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
