"""Pre-registered decisions C83 (gating across seeds) and C85 (SHOT leakage) from retained artifacts only.

Writes results/C83_RESULT.md, results/C85_RESULT.md and paper/figures/fig_gating.png. Missing seeds or folds are reported
as missing; no decision is declared until every pre-registered run is present.
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
PAIRS = [(f, t) for f in "AB" for t in TASKS]
SEEDS = (2024, 0, 1)


def load(pattern):
    out = {}
    for p in glob.glob(str(A / pattern), recursive=True):
        d = json.load(open(p))
        if d.get("smoke"):
            continue
        out[(d["variant"], d.get("gate", "none"), d["seed"], d["src_fold"], d["tgt_fold"])] = d["adapted"]
    return out


def c83():
    R = {}
    for pat in ("physgate-m2-f*/m2/result_*.json", "physgate-m2seed-*/**/result_*.json"):
        R.update(load(pat))
    have = {(s, f, g): (("final_checkpoint", g, s, f, {"A": "B", "B": "A"}[f]) in R) for s in SEEDS for f in "AB"
            for g in ("none", "v2", "pcv")}
    missing = [k for k, v in have.items() if not v]
    acc = lambda g, s: np.array([R[("final_checkpoint", g, s, f, {"A": "B", "B": "A"}[f])][t] for f, t in PAIRS])
    seeds = [s for s in SEEDS if all(have[(s, f, g)] for f in "AB" for g in ("none", "v2", "pcv"))]
    lines = ["# C83 — gating inside SDALR across seeds", "",
             f"Seeds available: {seeds}; missing runs: {missing or 'none'}.", "",
             "| seed | none | comb_v2 (gain) | PCV-style (gain) |", "|---|---|---|---|"]
    for s in seeds:
        n, v, p = acc("none", s).mean(), acc("v2", s).mean(), acc("pcv", s).mean()
        lines.append(f"| {s} | {n:.2f} | {v:.2f} ({v - n:+.2f}) | {p:.2f} ({p - n:+.2f}) |")
    verdict = {}
    if len(seeds) == 3:
        for g in ("v2", "pcv"):
            m = np.mean([acc(g, s) for s in seeds], axis=0)
            n = np.mean([acc("none", s) for s in seeds], axis=0)
            gain = m.mean() - n.mean()
            p = wilcoxon(m, n, alternative="greater", zero_method="zsplit").pvalue
            per_seed = [acc(g, s).mean() - acc("none", s).mean() for s in seeds]
            robust = bool(gain >= 1 and p < 0.05 and all(x > 0 for x in per_seed))
            verdict[g] = (gain, p, per_seed, robust)
            lines.append(f"\n**{g}:** 3-seed mean gain {gain:+.2f} pp, one-sided Wilcoxon p = {p:.4f}, per-seed gains "
                         f"{', '.join(f'{x:+.2f}' for x in per_seed)} → **{'ROBUST' if robust else 'NOT ROBUST'}** (C83 rule).")
    else:
        lines.append("\n**Decision pending:** not all three seeds are present.")
    (ROOT / "results" / "C83_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if seeds:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(8.5, 3.6), constrained_layout=True)
        x = np.arange(12); w = 0.27
        for i, (g, c, lab) in enumerate((("none", "#7f8c8d", "SDALR, no gate"), ("v2", "#1e8449", "comb_v2 gate"),
                                          ("pcv", "#b9770e", "envelope threshold gate"))):
            vals = np.array([acc(g, s) for s in seeds])
            ax.bar(x + (i - 1) * w, vals.mean(0), w, yerr=vals.std(0) if len(seeds) > 1 else None, color=c, label=lab,
                   capsize=2, error_kw={"lw": 0.8})
        ax.axhline(100 / 3, color="k", ls=":", lw=1)
        ax.set_xticks(x); ax.set_xticklabels([f"{f}:{t.replace('->', '→')}" for f, t in PAIRS], rotation=60, fontsize=7)
        ax.set_ylabel("clean-target accuracy (%)"); ax.legend(fontsize=8, ncol=3, loc="upper right")
        ax.set_title(f"Gating inside SDALR, bearing-wise targets (mean ± sd over seeds {seeds})", fontsize=9, loc="left")
        fig.savefig(ROOT / "paper" / "figures" / "fig_gating.png", dpi=200)
    return verdict, missing


def c85():
    R = load("physgate-shot-f*/**/result_*.json")
    need = [("shot", "none", 2024, f, g) for f in "AB" for g in "AB"]
    missing = [k for k in need if k not in R]
    lines = ["# C85 — SHOT on the M1 paired design", "", f"Missing runs: {missing or 'none'}.", ""]
    if not missing:
        leak = np.array([R[("shot", "none", 2024, f, f)][t] for f, t in PAIRS])
        clean = np.array([R[("shot", "none", 2024, f, {"A": "B", "B": "A"}[f])][t] for f, t in PAIRS])
        p = wilcoxon(leak, clean, alternative="greater", zero_method="zsplit").pvalue
        d = leak.mean() - clean.mean()
        ok = bool(d >= 5 and p < 0.05)
        lines += ["| task | leaky | clean |", "|---|---|---|"]
        lines += [f"| {f} {t.replace('->', '→')} | {a:.2f} | {b:.2f} |" for (f, t), a, b in zip(PAIRS, leak, clean)]
        lines.append(f"\nMean leaky {leak.mean():.2f} %, clean {clean.mean():.2f} %, Δ = {d:.2f} pp, one-sided Wilcoxon p = {p:.4g} "
                     f"→ **the M1 conclusion {'GENERALISES' if ok else 'DOES NOT GENERALISE'} to SHOT** (C85 rule: Δ ≥ 5 pp and p < 0.05).")
    else:
        lines.append("**Decision pending.**")
    (ROOT / "results" / "C85_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return missing


if __name__ == "__main__":
    v, m = c83()
    print("C83 missing:", m)
    print("C83 verdict:", v)
    print("C85 missing:", c85())
