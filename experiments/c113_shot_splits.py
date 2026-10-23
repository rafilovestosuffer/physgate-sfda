"""C113: corrected SHOT (index-aligned pseudo-labels, shot_patch v2) on the ten C88 splits — the C100 decision rule.

Rule fixed before the runs (PROTOCOL C100, re-used verbatim by C113): the SHOT collapse generalises beyond the two mechanical folds iff the median
split Delta_leak >= 10 pp and the exact sign-flip p < 0.05 over the splits, with the split as the unit. Reported either
way, including a negative. Missing splits are listed, never imputed.

CPU, reads the retained physgate-shot2-k10-* kernel artifacts only (never the withdrawn C100 ones) and refuses any artifact
whose kernel log does not record shot_patch_version >= 2. Writes results/c113/.
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
from c96_clustered_stats import cluster_bootstrap, sign_flip_p  # noqa: E402

OUT = ROOT / "results" / "c113"
KERNEL_GLOB = "physgate-shot2-k10-*"
MIN_PATCH_VERSION = 2
MIN_MEDIAN_PP, MAX_P = 10.0, 0.05


def load():
    """{split: {leaky/clean: {task: acc}}} from the shot2_k10 kernels, after checking the patch version in each kernel log."""
    got = {}
    for kl in glob.glob(str(E.A / KERNEL_GLOB / "**" / "kernel_log_*.json"), recursive=True):
        v = json.load(open(kl, encoding="utf-8")).get("env", {}).get("shot_patch_version", 1)
        if v < MIN_PATCH_VERSION:
            raise SystemExit(f"REFUSED: {kl} records shot_patch_version {v} < {MIN_PATCH_VERSION}")
    for p in glob.glob(str(E.A / KERNEL_GLOB / "**" / "result_PU_M1_shot_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if len(d.get("adapted", {})) != 6:
            continue
        src, tgt = d["src_fold"], d["tgt_fold"]
        got.setdefault(src, {})["clean" if tgt.endswith("c") else "leaky"] = d["adapted"]
    return {s: v for s, v in got.items() if {"leaky", "clean"} <= set(v)}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    got = load()
    sids = [s for s in E.SPLITS if s in got]
    missing = [s for s in E.SPLITS if s not in got]
    if not sids:
        print("no complete SHOT split pairs yet; nothing written")
        return

    clusters = [np.array([got[s]["leaky"][t] - got[s]["clean"][t] for t in sorted(got[s]["leaky"])]) for s in sids]
    diffs = np.array([c.mean() for c in clusters])
    med = float(np.median(diffs))
    mean, lo, hi = cluster_bootstrap(clusters)
    p = sign_flip_p(clusters)
    passed = med >= MIN_MEDIAN_PP and p < MAX_P

    res = {"splits": sids, "missing": missing, "median": med, "mean": mean, "ci": [lo, hi], "p": p,
           "positive": int((diffs > 0).sum()), "decision": "GENERALISES" if passed else "NOT SUPPORTED",
           "leaky_mean": float(np.mean([np.mean(list(got[s]["leaky"].values())) for s in sids])),
           "clean_mean": float(np.mean([np.mean(list(got[s]["clean"].values())) for s in sids])),
           "rows": {s: {"leaky": float(np.mean(list(got[s]["leaky"].values()))),
                        "clean": float(np.mean(list(got[s]["clean"].values())))} for s in sids}}
    json.dump(res, open(OUT / "c113_shot_splits.json", "w", encoding="utf-8"), indent=1)

    L = ["# C113 - corrected SHOT (patch v2) on the C88 splits", "",
         f"Splits with both arms: {len(sids)} ({', '.join(sids)})."
         + (f" Missing: {', '.join(missing)}." if missing else ""), "",
         "| Split | Leaky | Clean | $\\Delta$ |", "|---|---|---|---|"]
    L += [f"| {s} | {res['rows'][s]['leaky']:.1f} | {res['rows'][s]['clean']:.1f} | "
          f"{res['rows'][s]['leaky'] - res['rows'][s]['clean']:.1f} |" for s in sids]
    L += ["", f"Median $\\Delta_{{leak}}$ **{med:.1f} pp**; cluster-bootstrap mean {mean:.1f} pp "
              f"(95% CI {lo:.1f} to {hi:.1f}); exact sign-flip p = {p:.4f}; positive in "
              f"{res['positive']}/{len(sids)}.", "",
          f"Pre-registered rule (median >= {MIN_MEDIAN_PP:.0f} pp and p < {MAX_P}): **{res['decision']}**.", ""]
    (OUT / "C113_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
