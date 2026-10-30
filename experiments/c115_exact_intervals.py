"""C115 - Order-statistic intervals for every reported median, and leave-one-bearing-out influence (post-hoc reporting).

A percentile-bootstrap interval of a median over n = 10 splits has no exact coverage guarantee (C118 corrects the
earlier statement that it equals the 3rd and 8th order statistics; 89.1 % is the coverage of [x(3), x(8)]). This
script gives, for every median the manuscript reports with an interval, the
narrowest symmetric order-statistic interval [x(r), x(n+1-r)] with coverage >= 95 % under the sign model
(n = 10: x(2)..x(9), 97.9 %; n = 6: x(1)..x(6), 96.9 %; n = 17: x(5)..x(13), 95.1 %), from the same saved per-split
values, beside the bootstrap interval it replaces. Like the bootstrap intervals, these are conditional on the fixed bearing
pool: splits share bearings, so they describe sensitivity to the source-set draw, not a population of new bearings.

Also: the median SDALR split gap with each bearing's windows dropped from both targets (leave-one-bearing-out), recomputed
from the retained per-window predictions with SDALR's metric (mean per-class recall over the remaining windows).
Retained artifacts only; no training. Output: results/c115/c115_intervals.json
"""
from __future__ import annotations

import json
from math import comb

import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, boot_median_ci, dump, load

R = ROOT / "results"


def order_ci(x, conf=0.95):
    x = np.sort(np.asarray(x, float))
    n = len(x)
    best = None
    for r in range(1, n // 2 + 1):
        cov = sum(comb(n, k) for k in range(r, n + 1 - r)) / 2 ** n
        if cov >= conf:
            best = (r, cov)
    r, cov = best
    return {"lo": float(x[r - 1]), "hi": float(x[n - r]), "order_stats": [r, n + 1 - r], "coverage": cov}


def bacc(pred, lab):
    return 100 * float(np.mean([np.mean(pred[lab == c] == c) for c in np.unique(lab)]))


def lobo():
    K = load()["k10"]
    bearings = sorted({bearing_of(r) for s in SPLITS for t in TASKS for r in K[(s, s, "none")]["preds"][t]["rec"]}
                      | {bearing_of(r) for s in SPLITS for t in TASKS for r in K[(s, s + "c", "none")]["preds"][t]["rec"]})

    def gaps(drop):
        out = []
        for s in SPLITS:
            acc = []
            for arm in ((s, s, "none"), (s, s + "c", "none")):
                per = []
                for t in TASKS:
                    p = K[arm]["preds"][t]
                    keep = np.array([bearing_of(r) != drop for r in p["rec"]])
                    per.append(bacc(p["pred"][keep], p["label"][keep]))
                acc.append(np.mean(per))
            out.append(acc[0] - acc[1])
        return out

    rows = {}
    for b in bearings:
        g = gaps(b)
        rows[b] = {"median_pp": float(np.median(g)), "positive": int(sum(v > 0 for v in g))}
    meds = [v["median_pp"] for v in rows.values()]
    return {"all_bearings_median_pp": float(np.median(gaps(None))), "per_bearing": rows,
            "min_median_pp": min(meds), "min_bearing": min(rows, key=lambda b: rows[b]["median_pp"]),
            "max_median_pp": max(meds), "max_bearing": max(rows, key=lambda b: rows[b]["median_pp"]),
            "min_positive": min(v["positive"] for v in rows.values())}


def main():
    c109 = json.loads((R / "c109" / "c109_intervals.json").read_text(encoding="utf-8"))["effects"]
    c105 = json.loads((R / "c105" / "c105_source_only.json").read_text(encoding="utf-8"))
    c106 = json.loads((R / "c106" / "c106_within_bearing.json").read_text(encoding="utf-8"))
    c112 = json.loads((R / "c112" / "c112_result.json").read_text(encoding="utf-8"))
    rep = json.loads((R / "reporting_2026_10_09" / "reporting_corrections.json").read_text(encoding="utf-8"))
    sources = {   # effect -> (values, bootstrap interval reported until now, source)
        "sdalr_collapse_ten_splits": (c109["sdalr_collapse_ten_splits"]["values"],
                                      c109["sdalr_collapse_ten_splits"]["ci95_median"], "results/c109"),
        "source_only_collapse_ten_splits": ([r["pre_delta"] for r in c105["sdalr_ten_splits"]["rows"]],
                                            c105["sdalr_ten_splits"]["summary"]["ci_pre_delta"], "results/c105"),
        "shot_corrected_collapse_ten_splits": ([r["adapted_delta"] for r in c105["shot2_ten_splits"]["rows"]],
                                               boot_median_ci([r["adapted_delta"] for r in c105["shot2_ten_splits"]["rows"]]),
                                               "results/c105 (shot2, C113); bootstrap recomputed with rev6_load"),
        "within_bearing_difference_17": ([r["diff"] for r in c106["rows"]], c106["summary"]["ci_median_diff"],
                                         "results/c106"),
        "kinematic_ordinary_ten_splits": ([c112["per_split"][s]["delta"] for s in SPLITS],
                                          c112["summary"]["ci95_median"], "results/c112"),
        "kinematic_balanced_ten_splits": ([r["gap"] for r in rep["kinematic_balanced"]["rows"]],
                                          rep["kinematic_balanced"]["ci95_conditional"], "results/reporting_2026_10_09"),
    }
    for k in ("envelope_gate_gain_ten_splits", "recoverable_share_pct_ten_splits",
              "gate_closure_of_oracle_gap_pct_ten_splits", "rf_time_stats_collapse_ten_splits",
              "rf_all_features_collapse_ten_splits", "rf_time_stats_clean_minus_sdalr_clean",
              "same_condition_rf_collapse_ten_splits", "hust_collapse_six_splits"):
        sources[k] = (c109[k]["values"], c109[k]["ci95_median"], "results/c109")
    effects = {}
    for k, (vals, boot, src) in sources.items():
        effects[k] = {"n": len(vals), "median": float(np.median(vals)), "positive": int(sum(v > 0 for v in vals)),
                      "order_statistic_interval": order_ci(vals), "bootstrap_interval_replaced": boot, "source": src}
    out = {"entry": "C115", "status": "post-hoc reporting change; no new test", "effects": effects,
           "leave_one_bearing_out_sdalr_gap": lobo()}
    dump(out, R / "c115" / "c115_intervals.json")
    for k, e in effects.items():
        o = e["order_statistic_interval"]
        b = e["bootstrap_interval_replaced"]
        print(f"{k:45s} n={e['n']:2d} median {e['median']:7.2f}  order [{o['lo']:7.2f}, {o['hi']:7.2f}] "
              f"({o['coverage']:.3f})  bootstrap {['%.2f' % v for v in b] if b else '--'}")
    lb = out["leave_one_bearing_out_sdalr_gap"]
    print("LOBO:", {k: v for k, v in lb.items() if k != "per_bearing"})


if __name__ == "__main__":
    main()
