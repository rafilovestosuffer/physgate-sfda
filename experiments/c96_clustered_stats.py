"""C96: clustered inference and multiplicity control, raised in review.

Within a fold the 12 tasks share source checkpoints and bearing sets, so a Wilcoxon test that treats them as independent
units over-states evidence. This script reports, for every effect in the paper:
  (a) the task-level test as originally reported,
  (b) a cluster bootstrap that resamples SOURCE FOLDS (the sharing unit) or SPLITS, which is the honest unit,
  (c) a permutation test that only permutes the sign of a whole cluster,
  (d) Benjamini-Hochberg adjusted p-values across the family of primary tests.
Descriptive re-analysis of retained artifacts; no new runs. Writes results/c96/C96_RESULT.md.
"""
from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as E  # noqa: E402
import paired_gating as P  # noqa: E402

OUT = ROOT / "results" / "c96"
OTHER = {"A": "B", "B": "A"}
RNG = np.random.default_rng(20260922)


def cluster_bootstrap(clusters, n=20000):
    """Bootstrap the mean paired difference by resampling whole clusters with replacement."""
    means = []
    for _ in range(n):
        pick = RNG.integers(0, len(clusters), len(clusters))
        means.append(np.concatenate([clusters[i] for i in pick]).mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(np.mean(means)), float(lo), float(hi)


def sign_flip_p(clusters):
    """Exact one-sided permutation test flipping the sign of entire clusters (2^k assignments)."""
    obs = np.concatenate(clusters).mean()
    ge = 0
    for signs in product([1, -1], repeat=len(clusters)):
        stat = np.concatenate([s * c for s, c in zip(signs, clusters)]).mean()
        ge += stat >= obs
    return ge / 2 ** len(clusters)


def by(pvals):
    """Benjamini--Yekutieli: BH scaled by sum(1/i), valid under arbitrary dependence."""
    m = len(pvals)
    return np.minimum(bh(pvals) * sum(1.0 / i for i in range(1, m + 1)), 1.0)


def bh(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    prev = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        val = pvals[idx] * m / (m - rank + 1)
        prev = min(prev, val)
        adj[idx] = prev
    return adj


def fold_clusters_collapse():
    """Per-fold arrays of leaky - clean task differences, both arms from the M1 job."""
    out = []
    for f in "AB":
        import glob, json
        g = lambda pat: json.load(open(glob.glob(str(E.A / pat), recursive=True)[0], encoding="utf-8"))
        lk = g(f"physgate-m1-f{f.lower()}/**/result_PU_M1_final_checkpoint_F{f}to{f}_s2024.json")
        cl = g(f"physgate-m1-f{f.lower()}/**/result_PU_M1_final_checkpoint_F{f}to{OTHER[f]}_s2024.json")
        out.append(np.array([lk["adapted"][t] - cl["adapted"][t] for t in E.TASKS]))
    return out


def gate_clusters(gate="pcv", seed=2024):
    R = P.load()
    out = []
    for f in "AB":
        run = sorted({k[5] for k in R if k[:5] == ("final_checkpoint", "v2", seed, f, OTHER[f])})[0]
        base = P.pick(R, "final_checkpoint", "none", seed, f, OTHER[f], run)
        arm = P.pick(R, "final_checkpoint", gate, seed, f, OTHER[f], run)
        out.append(P.vec(arm) - P.vec(base))
    return out


def extra_split_tests():
    """{name: [per-split cluster of task differences]} for the tests added in the second review round.

    Each entry is split-level, so it carries inference; missing artifacts are skipped rather than faked.
    """
    import glob
    import json
    out = {}

    rf = ROOT / "results" / "c101" / "c101_rf_splits.json"
    if rf.exists():
        d = json.load(open(rf, encoding="utf-8"))
        for fs, label in (("T", "RF (10 time statistics) collapse, ten splits"),
                          ("TFE", "RF (time + spectral + envelope) collapse, ten splits")):
            if fs in d:
                out[label] = [np.array([a - b for a, b in d[fs]["rows"][s]["tasks"]]) for s in d[fs]["splits"]]

    hust = {}
    for p in glob.glob(str(E.A / "**" / "result_HUST_M1_*.json"), recursive=True):
        j = json.load(open(p, encoding="utf-8"))
        if len(j.get("adapted", {})) == 6:
            hust[(j["src_fold"], j["tgt_fold"])] = j["adapted"]
    vs = sorted({s for s, _ in hust})
    cl = [np.array([hust[(v, v)][t] - hust[(v, v + "c")][t] for t in sorted(hust[(v, v)])])
          for v in vs if (v, v) in hust and (v, v + "c") in hust]
    if cl:
        out["HUST collapse, six type-disjoint splits"] = cl

    c104 = ROOT / "results" / "c104" / "c104_same_condition.json"
    if c104.exists():   # review round 4: same-condition, bearing-disjoint control (pre-registered)
        d = json.load(open(c104, encoding="utf-8"))["splits"]
        out["Same-condition RF collapse, ten splits (C104)"] = [
            np.array([v["leaky"] - v["clean"] for v in d[s]["per_condition"].values()]) for s in sorted(d)]

    shot = {}
    for p in glob.glob(str(E.A / "physgate-shot-k10-*" / "**" / "result_PU_M1_shot_*.json"), recursive=True):
        j = json.load(open(p, encoding="utf-8"))
        if len(j.get("adapted", {})) == 6:
            shot[(j["src_fold"], j["tgt_fold"])] = j["adapted"]
    cl = [np.array([shot[(s, s)][t] - shot[(s, s + "c")][t] for t in sorted(shot[(s, s)])])
          for s in E.SPLITS if (s, s) in shot and (s, s + "c") in shot]
    if cl:
        out[f"SHOT collapse, {len(cl)} splits"] = cl
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    L = ["# C96 — clustered inference and multiplicity control", "",
         "Raised in review: within a fold the 12 tasks share source checkpoints and bearing sets, so they are not "
         "independent. Each effect below is reported three ways: the task-level Wilcoxon test as originally stated, a "
         "bootstrap that resamples whole clusters, and an exact permutation test that flips the sign of entire clusters. "
         "The cluster is the source fold (2 clusters) for the fold experiments and the split (10 or 6 clusters) elsewhere.",
         "", "| effect | unit | n clusters | mean effect (pp) | 95% cluster bootstrap | task-level p | cluster p |",
         "|---|---|---|---|---|---|---|"]
    tests = []

    c = fold_clusters_collapse()
    m, lo, hi = cluster_bootstrap(c)
    flat = np.concatenate(c)
    pw = wilcoxon(flat, alternative="greater").pvalue
    pc = sign_flip_p(c)
    tests.append(("collapse, two folds", pw, pc))
    L.append(f"| Collapse (leaky − clean), two folds | source fold | 2 | {flat.mean():.2f} | [{lo:.2f}, {hi:.2f}] | "
             f"{pw:.5f} | {pc:.3f} |")

    R = E.load()
    d_split = np.array([R[(s, s, "none")].mean() - R[(s, s + "c", "none")].mean() for s in E.SPLITS])
    g_split = np.array([R[(s, s + "c", "pcv")].mean() - R[(s, s + "c", "none")].mean() for s in E.SPLITS])
    for name, arr in (("Collapse, ten random splits", d_split), ("Gate gain, ten random splits", g_split)):
        cl = [np.array([v]) for v in arr]
        m, lo, hi = cluster_bootstrap(cl)
        pw = wilcoxon(arr, alternative="greater", zero_method="zsplit").pvalue
        pc = sign_flip_p(cl)
        tests.append((name, pw, pc))
        L.append(f"| {name} | split | {len(arr)} | {arr.mean():.2f} | [{lo:.2f}, {hi:.2f}] | {pw:.5f} | {pc:.4f} |")

    for gate, label in (("v2", "Shaft-alias-guarded comb"), ("pcv", "Envelope threshold rule")):
        c = gate_clusters(gate)
        m, lo, hi = cluster_bootstrap(c)
        flat = np.concatenate(c)
        pw = wilcoxon(flat, alternative="greater", zero_method="zsplit").pvalue
        pc = sign_flip_p(c)
        tests.append((f"{label} gain, two folds (seed 2024)", pw, pc))
        L.append(f"| {label} gain, two folds (seed 2024) | source fold | 2 | {flat.mean():.2f} | [{lo:.2f}, {hi:.2f}] | "
                 f"{pw:.4f} | {pc:.3f} |")

    # Split-level tests added in the second review round (C100/C101 and the HUST replication). They belong in the same
    # family, so the BH adjustment below is recomputed over all of them rather than over the original five.
    for name, clusters in extra_split_tests().items():
        m, lo, hi = cluster_bootstrap(clusters)
        flat = np.concatenate(clusters)
        pw = wilcoxon(flat, alternative="greater", zero_method="zsplit").pvalue
        pc = sign_flip_p(clusters)
        tests.append((name, pw, pc))
        L.append(f"| {name} | split | {len(clusters)} | {flat.mean():.2f} | [{lo:.2f}, {hi:.2f}] | {pw:.5f} | "
                 f"{pc:.4f} |")

    names = [t[0] for t in tests]
    praw = np.array([t[1] for t in tests])
    pcl = np.array([t[2] for t in tests])
    adj = bh(pcl)
    adj_by = by(pcl)
    L += ["", "## Benjamini--Hochberg adjustment across this family of primary tests", "",
          "| effect | cluster p | BH-adjusted | BY-adjusted (any dependence) |", "|---|---|---|---|"]
    for n_, p_, a_, b_ in zip(names, pcl, adj, adj_by):
        L.append(f"| {n_} | {p_:.4f} | {a_:.4f} | {b_:.4f} |")
    L += ["", "## Reading", "",
          "With only two source folds, an exact cluster-level test cannot reach a p-value below 0.25, so the fold "
          "experiments should be read as descriptive: the effect is large and in the same direction in both folds, but two "
          "clusters cannot carry significance on their own. The ten random splits are the inferential backbone: both the "
          "collapse and the gate gain survive cluster-level permutation and Benjamini--Hochberg adjustment. Task-level "
          "p-values reported elsewhere in the paper assume independent tasks and are therefore optimistic; they are "
          "retained only as descriptive statistics and are marked as such."]
    (OUT / "C96_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # machine-readable family, so the manuscript tables read adjusted values instead of hard-coding them
    import json
    json.dump({"family": [{"effect": n_, "task_p": float(r_), "cluster_p": float(p_), "bh": float(a_), "by": float(b_)}
                          for n_, r_, p_, a_, b_ in zip(names, praw, pcl, adj, adj_by)]},
              open(OUT / "c96_family.json", "w", encoding="utf-8"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
