"""C88 decision rules from retained artifacts (written before any split result existed).

Primary unit = split (mean over its 6 condition-pair tasks), n = 10 splits S00..S09.
  (L) leak generalises iff median split delta_leak >= 10 pp and one-sided Wilcoxon p < 0.01
  (G) PCV gating helps iff median paired split gain >= 1 pp, one-sided Wilcoxon p < 0.05, and gain > 0 in >= 8/10 splits
  (D) decomposition per split: total = leaky - clean; filter-recoverable = oracle - clean; not recoverable = leaky - oracle
The two M1 directions are listed alongside and never pooled into the primary statistics. Writes results/c88/C88_RESULT.md.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "results" / "artifacts"
OUT = ROOT / "results" / "c88"
TASKS = ["A1->A3", "A1->A2", "A3->A1", "A3->A2", "A2->A1", "A2->A3"]
SPLITS = [f"S{i:02d}" for i in range(10)]


def load():
    R = {}
    for p in glob.glob(str(A / "physgate-run-k10-*" / "**" / "result_PU_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("smoke") or len(d["adapted"]) < 6:
            continue
        R[(d["src_fold"], d["tgt_fold"], d.get("gate") or "none")] = np.array([d["adapted"][t] for t in TASKS])
    return R


def m1_rows():
    """Fold rows. Leaky and ungated clean come from the M1 job so that Delta_leak compares two arms of ONE job; the gated
    and oracle arms come from the gating job and are paired against that job's own ungated clean arm, reported in
    m1_gating_reference(). Running the identical configuration in two jobs differs by up to 1.6 pp on a fold (GPU
    non-determinism), which is why arms are never crossed between jobs."""
    rows = []
    for f, o in (("A", "B"), ("B", "A")):
        g = lambda pat: [json.load(open(p, encoding="utf-8")) for p in glob.glob(str(A / pat), recursive=True)]
        lk = g(f"physgate-m1-f{f.lower()}/**/result_PU_M1_final_checkpoint_F{f}to{f}_s2024.json")
        cl = g(f"physgate-m1-f{f.lower()}/**/result_PU_M1_final_checkpoint_F{f}to{o}_s2024.json")
        pc = g(f"physgate-m2-f{f.lower()}/m2/result_PU_M1_final_checkpoint_F{f}to{o}_gatepcv_s2024.json")
        orc = g(f"physgate-m2-f{f.lower()}/m2/result_PU_M1_final_checkpoint_F{f}to{o}_gateoracle_s2024.json")
        if lk and cl and pc and orc:
            v = lambda d: np.mean([d[0]["adapted"][t] for t in TASKS])
            ref = m1_gating_reference().get(f)
            rows.append((f"M1 fold {f}", v(lk), v(cl), v(pc), v(orc), ref))
    return rows


def m1_gating_reference():
    """The gating job's own ungated clean arm per fold: the correct baseline for its gated and oracle arms."""
    out = {}
    for f, o in (("A", "B"), ("B", "A")):
        hits = glob.glob(str(A / f"physgate-m2-f{f.lower()}" / "m2" / f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024.json"))
        if hits:
            d = json.load(open(hits[0], encoding="utf-8"))
            out[f] = float(np.mean([d["adapted"][t] for t in TASKS]))
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    R = load()
    L = ["# C88 — K-split leakage evaluation (PROTOCOL C88)", "",
         "Seed 2024, final_checkpoint, Track R, PU real damage. Split = mean over 6 condition-pair tasks.", "",
         "| split | leaky | clean | clean + PCV gate | clean + oracle | Δ_leak | PCV gain | filter-recoverable | not recoverable |",
         "|---|---|---|---|---|---|---|---|---|"]
    have, rows = [], []
    for s in SPLITS:
        k = [(s, s, "none"), (s, s + "c", "none"), (s, s + "c", "pcv"), (s, s + "c", "oracle")]
        if all(x in R for x in k):
            lk, cl, pc, orc = (R[x].mean() for x in k)
            have.append(s)
            rows.append((s, lk, cl, pc, orc))
        else:
            L.append(f"| {s} | missing: {[x[1] + '/' + x[2] for x in k if x not in R]} | | | | | | | |")
    def fmt(r):
        base = r[5] if len(r) > 5 and r[5] is not None else r[2]     # gate arms are paired against their own job's clean arm
        return (f"| {r[0]} | {r[1]:.2f} | {r[2]:.2f} | {r[3]:.2f} | {r[4]:.2f} | {r[1] - r[2]:.2f} | {r[3] - base:+.2f} | "
                f"{r[4] - base:.2f} ({100 * (r[4] - base) / (r[1] - r[2]):.0f} %) | {r[1] - r[4]:.2f} "
                f"({100 * (r[1] - r[4]) / (r[1] - r[2]):.0f} %) |")
    L += [fmt(r) for r in rows]
    ref = m1_gating_reference()
    L += ["", "M1 directions (reported alongside, not in the primary statistics). Leaky and clean are both from the M1 job; "
          "the gated and oracle arms come from the gating job, whose own ungated clean arm was "
          f"{', '.join(f'fold {k} {v:.2f}' for k, v in ref.items())}, and gains are computed against that arm.", ""]
    L += [fmt(r) for r in m1_rows()]
    if len(have) == 10:
        a = np.array([r[1:] for r in rows])
        d_leak, gain = a[:, 0] - a[:, 1], a[:, 2] - a[:, 1]
        pL = wilcoxon(a[:, 0], a[:, 1], alternative="greater").pvalue
        pG = wilcoxon(a[:, 2], a[:, 1], alternative="greater", zero_method="zsplit").pvalue
        okL = bool(np.median(d_leak) >= 10 and pL < 0.01)
        okG = bool(np.median(gain) >= 1 and pG < 0.05 and (gain > 0).sum() >= 8)
        rec = (a[:, 3] - a[:, 1]) / d_leak
        L += ["", f"**(L)** median Δ_leak {np.median(d_leak):.2f} pp [range {d_leak.min():.2f}, {d_leak.max():.2f}], one-sided Wilcoxon "
                  f"p = {pL:.5f} → **{'LEAK GENERALISES' if okL else 'NOT SUPPORTED'}**.",
              f"**(G)** median PCV gain {np.median(gain):+.2f} pp [range {gain.min():+.2f}, {gain.max():+.2f}], positive in "
              f"{int((gain > 0).sum())}/10, p = {pG:.4f} → **{'HELPS' if okG else 'NOT SUPPORTED'}**.",
              f"**(D)** filter-recoverable share of the collapse: median {100 * np.median(rec):.0f} % "
              f"[range {100 * rec.min():.0f}, {100 * rec.max():.0f} %]; PCV closes a median "
              f"{100 * np.median(gain / (a[:, 3] - a[:, 1])):.0f} % of the oracle gap."]
    else:
        L.append(f"\n**Decision pending:** {len(have)}/10 splits present.")
    # C92: random-forest (time statistics) clean accuracy per split vs ungated SDALR clean
    rf = {}
    for p in glob.glob(str(A / "physgate-run-c92-*" / "**" / "c92_result.json"), recursive=True):
        rf.update({k: v["T"]["clean_mean"] for k, v in json.load(open(p, encoding="utf-8")).items()})
    both = [(r[0], rf[r[0]], r[2]) for r in rows if r[0] in rf]
    if both:
        L += ["", "## C92 — random forest (time statistics) vs SDALR on clean targets", "",
              "| split | RF-T clean | SDALR clean | difference |", "|---|---|---|---|"]
        L += [f"| {s_} | {a_:.2f} | {b_:.2f} | {a_ - b_:+.2f} |" for s_, a_, b_ in both]
        d = np.array([a_ - b_ for _, a_, b_ in both])
        L.append("\n" + f"Median difference {np.median(d):+.2f} pp over {len(d)} splits" +
                 (f" → **{'shallow baseline exceeds SDALR (≥ 5 pp)' if np.median(d) >= 5 else 'C91 flag is fold-specific (< 5 pp)'}** (C92)."
                  if len(d) == 10 else " (C92 decision needs all 10 splits)."))
    (OUT / "C88_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
