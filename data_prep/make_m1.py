"""Build M1 data (PROTOCOL C32): PU, L3, one file per (bearing fold, condition), SDALR Track R windowing.

Folds come from configs/splits.yaml (mechanical rule) for the healthy / real_outer / real_inner groups.
Each file holds 2000 windows per class spread evenly across that fold's bearings and their 20 records at
that condition, so leaky (F -> F) and clean (F -> F') targets differ ONLY in physical-bearing overlap.

Output: data/m1/PU_M1_fold{A,B}_{condition}.npz with X, y (0 normal, 1 inner, 2 outer), bearing_id,
record_id, start, class_names, overlap. Every window is traceable to its bearing.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pu  # noqa: E402
import split  # noqa: E402
from make_m0 import W, PER_CLASS, PU_DOMAINS, windows_from_records, _overlap  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "m1"
CLASSES = ["normal", "inner_race", "outer_race"]
GROUP_OF_CLASS = {"normal": "healthy", "inner_race": "real_inner", "outer_race": "real_outer"}


def fold_bearings(fold: str) -> dict[str, list[str]]:
    cfg = split.load_cfg()
    split.verify_folds_follow_rule(cfg)
    return {c: cfg["pu"][GROUP_OF_CLASS[c]][fold] for c in CLASSES}


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fa, fb = fold_bearings("A"), fold_bearings("B")
    all_a = {b for v in fa.values() for b in v}
    all_b = {b for v in fb.values() for b in v}
    split.assert_no_leak(all_a, all_b, "M1 folds")      # the folds themselves must be disjoint
    for fold, bearings in (("A", fa), ("B", fb)):
        for cond in PU_DOMAINS:
            Xs, ys, bids, rids, sts, ovs = [], [], [], [], [], []
            for ci, c in enumerate(CLASSES):
                recs = pu.load(bearings=bearings[c], conditions=[cond])
                if len(recs) != 20 * len(bearings[c]):
                    raise RuntimeError(f"fold {fold} {c} {cond}: expected {20 * len(bearings[c])} records, got {len(recs)}")
                X, rid, bid, st = windows_from_records(recs, PER_CLASS)
                Xs.append(X); ys += [ci] * len(X); bids += bid; rids += rid; sts.append(st)
                ovs.append(_overlap(recs, PER_CLASS))
                del recs
            p = OUT / f"PU_M1_fold{fold}_{cond}.npz"
            np.savez(p, X=np.concatenate(Xs), y=np.asarray(ys, np.int64), bearing_id=np.asarray(bids),
                     record_id=np.asarray(rids), start=np.concatenate(sts), class_names=np.asarray(CLASSES),
                     overlap=np.asarray(ovs, np.float32))
            print(f"{p.name}: {sum(len(x) for x in Xs)} windows, bearings "
                  f"{sorted(set(bids))}, max overlap {max(ovs):.1%}", flush=True)


if __name__ == "__main__":
    build()
