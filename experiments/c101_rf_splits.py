"""C101: the shallow baseline's own leakage collapse, reported over the ten splits instead of the two folds.

The C92 artifacts already hold both arms (leaky and clean) per split for every feature set; only the clean arm was
used in the paper, as the comparison against SDALR. With the fold as the cluster a two-fold comparison has a
permutation floor of p = 0.25 (C96), so the "the collapse is not specific to one method" claim needs the splits.

Split-level statistics use the same machinery as C96: cluster bootstrap median, exact sign-flip permutation, BH.
CPU, no new runs. Writes results/c101/.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as E  # noqa: E402
from c96_clustered_stats import bh, cluster_bootstrap, sign_flip_p  # noqa: E402

OUT = ROOT / "results" / "c101"
SETS = ("T", "TFE")


def load():
    """{feature_set: {split: {'leaky': mean, 'clean': mean, 'tasks': [(leaky, clean), ...]}}}"""
    out = {s: {} for s in SETS}
    for p in glob.glob(str(E.A / "physgate-run-c92-rf-*" / "**" / "c92_result.json"), recursive=True):
        for sid, d in json.load(open(p, encoding="utf-8")).items():
            for s in SETS:
                if s in d:
                    out[s][sid] = {"leaky": d[s]["leaky_mean"], "clean": d[s]["clean_mean"],
                                   "tasks": [(r["leaky"], r["clean"]) for r in d[s]["rows"]]}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data, res, L = load(), {}, []
    L += ["# C101 - the shallow baseline over the ten splits", "",
          "Both arms come from the same C92 job and the same windows as the SDALR arms of that split. The split is the",
          "unit; task-level tests are not reported because tasks within a split share a training set.", ""]
    for s in SETS:
        d = dict(sorted(data[s].items()))
        sids = [k for k in d if k in E.SPLITS]
        clusters = [np.array([a - b for a, b in d[k]["tasks"]]) for k in sids]   # one cluster per split
        diffs = np.array([d[k]["leaky"] - d[k]["clean"] for k in sids])
        med, lo, hi = cluster_bootstrap(clusters)
        p = sign_flip_p(clusters)
        res[s] = {"splits": sids, "median": med, "ci": [lo, hi], "p": p,
                  "rows": {k: d[k] for k in sids}}
        L += [f"## Feature set {s}", "", "| Split | Leaky | Clean | $\\Delta$ |", "|---|---|---|---|"]
        L += [f"| {k} | {d[k]['leaky']:.1f} | {d[k]['clean']:.1f} | {d[k]['leaky'] - d[k]['clean']:.1f} |"
              for k in sids]
        L += ["", f"Over {len(sids)} splits: median $\\Delta_{{leak}}$ **{np.median(diffs):.1f} pp**, cluster-bootstrap "
                  f"mean **{med:.1f} pp** (95% CI {lo:.1f} to {hi:.1f}; exact sign-flip p = {p:.4f}, "
                  f"positive in {int((diffs > 0).sum())}/{len(diffs)}).", ""]
    ps = [res[s]["p"] for s in SETS]
    for s, q in zip(SETS, bh(ps)):
        res[s]["p_bh"] = q
    L += ["## Multiplicity", "",
          "BH correction across the two feature sets: " + ", ".join(f"{s} p_BH = {res[s]['p_bh']:.4f}" for s in SETS),
          ""]
    json.dump(res, open(OUT / "c101_rf_splits.json", "w", encoding="utf-8"), indent=1)
    (OUT / "C101_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
