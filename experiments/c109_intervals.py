"""C109 - Intervals the paper promised but did not print (post-hoc reporting; no new test, no change to the C96 family).

C96 states that every primary effect is reported with a cluster bootstrap. The retained C96/C100/C101 intervals are for
the mean; the paper reports medians. This script computes, from retained artifacts only:
  * percentile cluster-bootstrap 95 % intervals (20,000 resamples, seed 0) for the MEDIAN of every split-level effect,
    the split being the cluster;
  * bearing-cluster bootstrap 95 % intervals for the healthy false-acceptance rate of each gate (480 healthy records
    from 6 physical bearings; the bearing is the cluster, since records of one bearing are not independent);
  * exact Clopper-Pearson 95 % intervals treating records as independent (needed where the count is 0, for which the
    bootstrap interval is degenerate);
  * the interquartile range of the recoverable share under numpy's default (linear) quantile rule.
Output: results/c109/c109_intervals.json
"""
from __future__ import annotations

import glob
import json

import numpy as np
from scipy.stats import beta

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, boot_median_ci, dump, load, mean6

HUST_TASKS = ["H1->H3", "H1->H2", "H3->H1", "H3->H2", "H2->H1", "H2->H3"]


def entry(x):
    x = np.asarray(x, float)
    return {"values": x.round(4).tolist(), "median": float(np.median(x)), "ci95_median": boot_median_ci(x),
            "positive": int((x > 0).sum()), "n": int(len(x))}


def main():
    K = load()["k10"]
    lk = np.array([mean6(K[(s, s, "none")], "adapted") for s in SPLITS])
    cl = np.array([mean6(K[(s, s + "c", "none")], "adapted") for s in SPLITS])
    gt = np.array([mean6(K[(s, s + "c", "pcv")], "adapted") for s in SPLITS])
    orc = np.array([mean6(K[(s, s + "c", "oracle")], "adapted") for s in SPLITS])
    rec = 100 * (orc - cl) / (lk - cl)
    closure = 100 * (gt - cl) / (orc - cl)
    shot = json.loads((ROOT / "results" / "c100" / "c100_shot_splits.json").read_text(encoding="utf-8"))["rows"]
    rf = json.loads((ROOT / "results" / "c101" / "c101_rf_splits.json").read_text(encoding="utf-8"))
    same = json.loads((ROOT / "results" / "c104" / "c104_same_condition.json").read_text(encoding="utf-8"))["splits"]
    hust = {}
    for p in glob.glob(str(ROOT / "results" / "artifacts" / "physgate-run-hust-k6" / "**" / "result_HUST_M1_*.json"),
                       recursive=True):
        d = json.loads(open(p, encoding="utf-8").read())
        if not d.get("smoke") and len(d.get("adapted", {})) == 6:
            hust[(d["src_fold"], d["tgt_fold"])] = np.mean([d["adapted"][t] for t in HUST_TASKS])
    hv = sorted({s for s, _ in hust})
    effects = {
        "sdalr_collapse_ten_splits": entry(lk - cl),
        "envelope_gate_gain_ten_splits": entry(gt - cl),
        "recoverable_share_pct_ten_splits": entry(rec),
        "gate_closure_of_oracle_gap_pct_ten_splits": entry(closure),
        "shot_collapse_ten_splits": entry([shot[s]["leaky"] - shot[s]["clean"] for s in SPLITS]),
        "rf_time_stats_collapse_ten_splits": entry([rf["T"]["rows"][s]["leaky"] - rf["T"]["rows"][s]["clean"] for s in SPLITS]),
        "rf_all_features_collapse_ten_splits": entry([rf["TFE"]["rows"][s]["leaky"] - rf["TFE"]["rows"][s]["clean"] for s in SPLITS]),
        "rf_time_stats_clean_minus_sdalr_clean": entry([rf["T"]["rows"][s]["clean"] - c for s, c in zip(SPLITS, cl)]),
        "same_condition_rf_collapse_ten_splits": entry([same[s]["delta"] for s in SPLITS]),
        "hust_collapse_six_splits": entry([hust[(v, v)] - hust[(v, v + "c")] for v in hv]),
    }
    q = np.percentile(rec, [25, 75])
    effects["recoverable_share_pct_ten_splits"]["iqr_numpy_linear"] = [float(q[0]), float(q[1])]
    ver = json.loads((ROOT / "results" / "m2" / "gate_verdicts.json").read_text(encoding="utf-8"))
    healthy = [r for r in ver["pcv"] if bearing_of(r).startswith("K0")]
    bears = sorted({bearing_of(r) for r in healthy})
    rng = np.random.default_rng(0)
    fa = {}
    for g, name in (("pcv", "envelope threshold rule"), ("v2", "shaft-alias-guarded comb"), ("c30", "surrogate-null comb"),
                    ("eagle", "raw-spectrum band rule")):
        per = {b: [ver[g][r] != "normal" for r in healthy if bearing_of(r) == b] for b in bears}
        k = sum(sum(v) for v in per.values())
        n = sum(len(v) for v in per.values())
        boots = []
        for _ in range(20000):
            pick = rng.integers(0, len(bears), len(bears))
            kk = sum(sum(per[bears[i]]) for i in pick)
            nn = sum(len(per[bears[i]]) for i in pick)
            boots.append(kk / nn)
        lo, hi = np.percentile(boots, [2.5, 97.5])
        cp = beta.ppf([0.025, 0.975], [k, k + 1], [n - k + 1, n - k])
        fa[name] = {"false_accepts": int(k), "healthy_records": int(n), "rate": k / n,
                    "ci95_bearing_cluster": [float(lo), float(hi)],
                    "ci95_clopper_pearson_records": [0.0 if k == 0 else float(cp[0]), 1.0 if k == n else float(cp[1])],
                    "per_bearing": {b: int(sum(v)) for b, v in per.items()}}
    out = {"entry": "C109", "status": "post-hoc reporting", "effects": effects, "healthy_false_acceptance": fa}
    dump(out, ROOT / "results" / "c109" / "c109_intervals.json")
    for k, v in effects.items():
        print(f"{k}: median {v['median']:.2f} CI {np.round(v['ci95_median'], 2).tolist()} pos {v['positive']}/{v['n']}")
    print("recoverable IQR numpy:", effects["recoverable_share_pct_ten_splits"]["iqr_numpy_linear"])
    for k, v in fa.items():
        print(k, v["false_accepts"], "/", v["healthy_records"], np.round(np.array(v["ci95_bearing_cluster"]) * 100, 2),
              np.round(np.array(v["ci95_clopper_pearson_records"]) * 100, 2), v["per_bearing"])


if __name__ == "__main__":
    main()
