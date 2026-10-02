"""C111 - What the identity probe keys on (PROTOCOL C111, pre-registered before this run; local CPU, seconds).

Same probe as C97: within one class, logistic regression on standardised features, record-disjoint halves by CRC32 parity
of record_id, record-level majority vote. On the ten C91 time statistics of the M1 windows, six source models' data
(folds A and B x conditions A1/A2/A3), pooled:
  (a) all ten statistics, per class (healthy included) with window-level accuracy;
  (b) without the mean (the statistic most tied to sensor/amplifier offset);
  (c) each statistic alone;
  (d) within-bearing control: each bearing's recordings at one condition split into two pseudo-bearings by recording
      index (1-10 vs 11-20); the same probe asked to separate them.
Writes results/c111/c111_probe_ablations.json.
"""
from __future__ import annotations

import json
import re
import zlib
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from c97_probe_baseline import feats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "m1"
OUT = ROOT / "results" / "c111"
CONDS = ["N15_M01_F10", "N15_M07_F04", "N15_M07_F10"]
NAMES = {0: "normal", 1: "inner race", 2: "outer race"}
STATS = ["mean", "std", "rms", "peak", "peak-to-peak", "skewness", "kurtosis", "crest", "shape", "impulse"]


def probe(F, groups, records, mask):
    """Record-level identification of `groups` among records in `mask`; returns (correct, records, chance, window_acc)."""
    te = np.array([zlib.crc32(r.encode()) % 2 for r in records]) == 1
    mtr, mte = mask & ~te, mask & te
    ng = len(set(groups[mask]))
    if ng < 2 or mtr.sum() < 5 or mte.sum() < 5:
        return 0, 0, 0.0, float("nan")
    sc = StandardScaler().fit(F[mtr])
    clf = LogisticRegression(max_iter=3000).fit(sc.transform(F[mtr]), groups[mtr])
    pred = clf.predict(sc.transform(F[mte]))
    votes = {}
    for r, g, p in zip(records[mte], groups[mte], pred):
        votes.setdefault(r, [g, Counter()])[1][p] += 1
    k = sum(v[0] == v[1].most_common(1)[0][0] for v in votes.values())
    return k, len(votes), 1.0 / ng, float((pred == groups[mte]).mean())


def rec_index(record_id):
    return int(re.search(r"_(\d+)$", record_id).group(1))


def run(feature_cols, per_class=False):
    tot_k = tot_n = 0
    chance_w = 0.0
    win = []
    by_class = {c: [0, 0, 0.0] for c in NAMES.values()}
    for fold in "AB":
        for cond in CONDS:
            d = np.load(DATA / f"PU_M1_fold{fold}_{cond}.npz", allow_pickle=False)
            F = feats(d["X"])[:, feature_cols]
            y, b, r = d["y"], d["bearing_id"].astype(str), d["record_id"].astype(str)
            for c in sorted(set(y.tolist())):
                k, n, ch, wa = probe(F, b, r, y == c)
                tot_k += k
                tot_n += n
                chance_w += ch * n
                if n:
                    win.append(wa)
                    by_class[NAMES[c]][0] += k
                    by_class[NAMES[c]][1] += n
                    by_class[NAMES[c]][2] += ch * n
    out = {"correct": tot_k, "records": tot_n, "chance": chance_w / max(tot_n, 1), "median_window_acc": float(np.median(win))}
    if per_class:
        out["per_class"] = {c: {"correct": v[0], "records": v[1], "chance": v[2] / max(v[1], 1)} for c, v in by_class.items()}
    return out


def within_bearing_control():
    tot_k = tot_n = 0
    for fold in "AB":
        for cond in CONDS:
            d = np.load(DATA / f"PU_M1_fold{fold}_{cond}.npz", allow_pickle=False)
            F = feats(d["X"])
            b, r = d["bearing_id"].astype(str), d["record_id"].astype(str)
            half = np.array(["early" if rec_index(x) <= 10 else "late" for x in r])
            for bb in np.unique(b):
                k, n, _, _ = probe(F, half, r, b == bb)
                tot_k += k
                tot_n += n
    return {"correct": tot_k, "records": tot_n, "chance": 0.5}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"entry": "C111", "status": "pre-registered (2026-10-02), descriptive",
           "a_all_ten": run(list(range(10)), per_class=True),
           "b_without_mean": run(list(range(1, 10))),
           "c_single_statistic": {s: run([i]) for i, s in enumerate(STATS)},
           "d_within_bearing_early_vs_late": within_bearing_control()}
    (OUT / "c111_probe_ablations.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    a = res["a_all_ten"]
    print("a all ten:", a["correct"], "/", a["records"], "chance", round(a["chance"], 3), "window acc", round(a["median_window_acc"], 3))
    print("  per class:", a["per_class"])
    b = res["b_without_mean"]
    print("b without mean:", b["correct"], "/", b["records"], "window", round(b["median_window_acc"], 3))
    for s, v in res["c_single_statistic"].items():
        print(f"c {s:<13} {v['correct']}/{v['records']} window {v['median_window_acc']:.3f}")
    print("d within-bearing early vs late:", res["d_within_bearing_early_vs_late"])


if __name__ == "__main__":
    main()
