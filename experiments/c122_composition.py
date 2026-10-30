"""C122 - Outer-race composition of the two targets and the ten-split gap (post-hoc, descriptive).

Every clean target holds two outer-race bearings and every leaky target three (five real outer-race bearings in the pool).
Two re-scorings of the retained ungated SDALR predictions (final checkpoint, seed 2024) test whether that asymmetry moves
the split-level gap:
(a) the leaky arm re-scored with one of its three outer-race bearings dropped, averaged over the three choices, so both
    targets are scored on two outer-race bearings;
(b) both arms scored by per-bearing weighting, the mean of the bearings' window accuracies, instead of SDALR's metric.
Limitation: (a) re-scores the predictions of models adapted to three-outer-bearing leaky targets; it does not re-adapt to a
two-outer-bearing target, so it does not test whether adaptation itself (centroids, pseudo-labels) behaves differently.
Reads retained artifacts only (per-window prediction dumps, via rev6_load); no training, no GPU. Accuracy is SDALR's
metric, the mean per-class recall over a task's windows, averaged over the six tasks of a split.
Output: results/c122/c122_composition.json
"""
from __future__ import annotations

import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, dump, load


def bacc(pred, lab):
    return 100 * float(np.mean([np.mean(pred[lab == c] == c) for c in np.unique(lab)]))


def per_bearing(pred, lab, b):
    return 100 * float(np.mean([np.mean(pred[b == x] == lab[b == x]) for x in np.unique(b)]))


def summary(g):
    return {"median_pp": float(np.median(g)), "positive": int(sum(x > 0 for x in g)), "min_pp": float(min(g)),
            "max_pp": float(max(g)), "per_split": dict(zip(SPLITS, map(float, g)))}


def main():
    K = load()["k10"]
    base, two_outer, bearing_w, n_outer = [], [], [], {}
    for s in SPLITS:
        L, C = K[(s, s, "none")], K[(s, s + "c", "none")]
        lb, cb, l2, lw, cw = [], [], [], [], []
        for t in TASKS:
            pl, pc = L["preds"][t], C["preds"][t]
            bl = np.array([bearing_of(r) for r in pl["rec"]])
            bc = np.array([bearing_of(r) for r in pc["rec"]])
            outer = sorted({x for x in bl if x.startswith("KA")})
            n_outer[s] = (len(outer), len({x for x in bc if x.startswith("KA")}))
            lb.append(bacc(pl["pred"], pl["label"]))
            cb.append(bacc(pc["pred"], pc["label"]))
            l2.append(np.mean([bacc(pl["pred"][bl != o], pl["label"][bl != o]) for o in outer]))
            lw.append(per_bearing(pl["pred"], pl["label"], bl))
            cw.append(per_bearing(pc["pred"], pc["label"], bc))
        base.append(np.mean(lb) - np.mean(cb))
        two_outer.append(np.mean(l2) - np.mean(cb))
        bearing_w.append(np.mean(lw) - np.mean(cw))
    out = {"entry": "C122", "status": "post-hoc, descriptive", "arms": "SDALR final_checkpoint, seed 2024, ungated",
           "outer_race_bearings_leaky_clean": n_outer,
           "gap_as_reported": summary(base),
           "gap_leaky_two_outer_bearings": summary(two_outer),
           "gap_per_bearing_weighting": summary(bearing_w),
           "limitation": "re-scores predictions adapted to three-outer-bearing leaky targets; no re-adaptation"}
    dump(out, ROOT / "results" / "c122" / "c122_composition.json")
    for k in ("gap_as_reported", "gap_leaky_two_outer_bearings", "gap_per_bearing_weighting"):
        print(k, {kk: v for kk, v in out[k].items() if kk != "per_split"})


if __name__ == "__main__":
    main()
