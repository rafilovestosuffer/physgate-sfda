"""Build the Track R / M0 datasets that reproduce SDALR's windowing from RAW public data.

SDALR's own preprocessed archives (Baidu Pan) are not independently available, so we rebuild them.
Exact start positions are unrecorded in SDALR; we use DETERMINISTIC, EVENLY SPACED starts, which is
the most neutral choice and is documented as reproduction risk A6 in notes/sdalr_code_audit.md.

Windowing consequences, computed before building (C19):
  PU  : 20 records x 256,823 samples -> 100 windows/record, stride 2573 -> NO overlap.
  JNU : 1 record x 500,500 (fault)   -> 2000 windows, stride 249 -> 87.8 % OVERLAP (only 244 disjoint
        windows exist); normal 1 x 1,501,500 -> stride 750 -> 63.4 % overlap. Asymmetric by class.

Output: data/m0/<DATASET>_<condition>.npz with
  X (N, 2048) float32, y (N,), bearing_id (N,), record_id (N,), start (N,), class_names, overlap.
Every window carries its bearing and record so leakage can be audited after the fact.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from records import Record  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "m0"
W = 2048
PER_CLASS = 2000

PU_BEARINGS = ["K001", "KA04", "KA15", "KA22", "KA30", "KI14", "KI17", "KI21"]   # classes ARE bearings
PU_DOMAINS = ["N15_M01_F10", "N15_M07_F04", "N15_M07_F10"]                       # paper A1, A2, A3
JNU_CLASSES = ["normal", "inner_race", "outer_race", "ball"]
JNU_DOMAINS = ["600rpm", "800rpm", "1000rpm"]                                    # paper B1, B2, B3


def even_starts(n_samples: int, k: int) -> np.ndarray:
    if n_samples < W:
        raise ValueError(f"record shorter than window ({n_samples} < {W})")
    if k == 1:
        return np.array([0])
    return np.round(np.linspace(0, n_samples - W, k)).astype(np.int64)


def windows_from_records(recs: list[Record], k_total: int) -> tuple[np.ndarray, list, list, np.ndarray]:
    """Split k_total windows as evenly as possible across records, evenly spaced within each."""
    n = len(recs)
    per = [k_total // n + (1 if i < k_total % n else 0) for i in range(n)]
    X, rid, bid, st = [], [], [], []
    for r, k in zip(recs, per):
        s = even_starts(r.signal.size, k)
        X.append(np.stack([r.signal[a:a + W] for a in s]))
        rid += [r.record_id] * k
        bid += [r.bearing_id] * k
        st.append(s)
    return np.concatenate(X).astype(np.float32), rid, bid, np.concatenate(st)


def _overlap(recs: list[Record], k: int) -> float:
    per = k / len(recs)
    L = min(r.signal.size for r in recs)
    stride = (L - W) / max(per - 1, 1)
    return float(max(0.0, 1 - stride / W))


def save(name: str, X, y, bid, rid, st, classes, overlaps) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.npz"
    np.savez(p, X=X, y=np.asarray(y, np.int64), bearing_id=np.asarray(bid), record_id=np.asarray(rid),
             start=st, class_names=np.asarray(classes), overlap=np.asarray(overlaps, np.float32))
    return p


def build_jnu() -> None:
    import jnu
    recs = jnu.load()
    for dom in JNU_DOMAINS:
        Xs, ys, bids, rids, sts, ovs = [], [], [], [], [], []
        for ci, c in enumerate(JNU_CLASSES):
            rr = [r for r in recs if r.condition == dom and r.fault_type == c]
            X, rid, bid, st = windows_from_records(rr, PER_CLASS)
            Xs.append(X); ys += [ci] * len(X); bids += bid; rids += rid; sts.append(st)
            ovs.append(_overlap(rr, PER_CLASS))
        p = save(f"JNU_{dom}", np.concatenate(Xs), ys, bids, rids, np.concatenate(sts), JNU_CLASSES, ovs)
        print(f"{p.name}: {sum(len(x) for x in Xs)} windows, per-class overlap "
              + ", ".join(f"{c}={o:.1%}" for c, o in zip(JNU_CLASSES, ovs)), flush=True)


def build_pu() -> None:
    import pu
    for dom in PU_DOMAINS:
        Xs, ys, bids, rids, sts, ovs = [], [], [], [], [], []
        for ci, b in enumerate(PU_BEARINGS):
            rr = pu.load(bearings=[b], conditions=[dom])
            if len(rr) != 20:
                raise RuntimeError(f"PU {b}/{dom}: expected 20 records, found {len(rr)} (download incomplete?)")
            X, rid, bid, st = windows_from_records(rr, PER_CLASS)
            Xs.append(X); ys += [ci] * len(X); bids += bid; rids += rid; sts.append(st)
            ovs.append(_overlap(rr, PER_CLASS))
        p = save(f"PU_{dom}", np.concatenate(Xs), ys, bids, rids, np.concatenate(sts), PU_BEARINGS, ovs)
        print(f"{p.name}: {sum(len(x) for x in Xs)} windows, max overlap {max(ovs):.1%}", flush=True)


if __name__ == "__main__":
    which = sys.argv[1:] or ["jnu", "pu"]
    if "jnu" in which:
        build_jnu()
    if "pu" in which:
        build_pu()
