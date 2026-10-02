"""C88 data: one view per (split, side, condition), built exactly like make_m1 (same windowing, 2000 windows/class).

Views: PU_M1_fold{Sxx}_{cond}.npz (source bearings) and PU_M1_fold{Sxx}c_{cond}.npz (complement). Output data/k10/<group>/.
Groups (one Kaggle dataset + one kernel each): g1 S00-S02, g2 S03-S05, g3 S06-S07, g4 S08-S09.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pu  # noqa: E402
import split  # noqa: E402
from make_m0 import PER_CLASS, PU_DOMAINS, windows_from_records, _overlap  # noqa: E402
from make_m1 import CLASSES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GROUPS = {"g1": ["S00", "S01", "S02"], "g2": ["S03", "S04", "S05"], "g3": ["S06", "S07"], "g4": ["S08", "S09"]}


def build(groups):
    cfg = yaml.safe_load((ROOT / "configs" / "splits_k10.yaml").read_text(encoding="utf-8"))["splits"]
    for g in groups:
        out = ROOT / "data" / "k10" / g
        out.mkdir(parents=True, exist_ok=True)
        for sid in GROUPS[g]:
            src, tgt = cfg[sid]["source"], cfg[sid]["target"]
            split.assert_no_leak({b for v in src.values() for b in v}, {b for v in tgt.values() for b in v}, f"C88 {sid}")
            for view, bearings in ((sid, src), (sid + "c", tgt)):
                for cond in PU_DOMAINS:
                    p = out / f"PU_M1_fold{view}_{cond}.npz"
                    if p.exists():
                        continue
                    Xs, ys, bids, rids, sts, ovs = [], [], [], [], [], []
                    for ci, c in enumerate(CLASSES):
                        recs = pu.load(bearings=bearings[c], conditions=[cond])
                        if len(recs) != 20 * len(bearings[c]):
                            raise RuntimeError(f"{view} {c} {cond}: expected {20 * len(bearings[c])} records, got {len(recs)}")
                        X, rid, bid, st = windows_from_records(recs, PER_CLASS)
                        Xs.append(X); ys += [ci] * len(X); bids += bid; rids += rid; sts.append(st)
                        ovs.append(_overlap(recs, PER_CLASS))
                        del recs
                    np.savez(p, X=np.concatenate(Xs), y=np.asarray(ys, np.int64), bearing_id=np.asarray(bids),
                             record_id=np.asarray(rids), start=np.concatenate(sts), class_names=np.asarray(CLASSES),
                             overlap=np.asarray(ovs, np.float32))
                    print(f"{g} {p.name}: {sum(len(x) for x in Xs)} windows, {sorted(set(bids))}", flush=True)


if __name__ == "__main__":
    build(sys.argv[1:] or list(GROUPS))
