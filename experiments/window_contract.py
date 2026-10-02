"""S2.0 (external audit, 2026-09-13): certify the Track A WINDOW CONTRACT, not only spectral separation.

C21 derived T_A = 3.0 s from resolution alone. This adds the sample-count constraint the derivation
lacked and sweeps T_A x within-record overlap. Output: results/feasibility/T_A_sweep.csv.

est_train_windows_per_class uses the smallest L3 class on PU (healthy, 6 bearings) under the
bearing-wise two-fold split actually in use (configs/splits.yaml: 3 healthy bearings per fold),
4 conditions x 20 records per bearing. Windows never cross a record boundary.
"""
from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "physics"))
from feasibility import assess, _cases, LABEL_SPACE_FAMILIES  # noqa: E402

RECORD_S = {"CWRU": 10.0, "PU": 4.0}
TRAIN_MIN = 250
PU_TRAIN_RECORDS_SMALLEST_CLASS = 3 * 4 * 20      # healthy: 3 bearings/fold x 4 conditions x 20 records


def windows_per_record(rec_s: float, T: float, overlap: float) -> int:
    if T > rec_s:
        return 0
    hop = T * (1.0 - overlap)
    return 1 + int(math.floor((rec_s - T) / hop + 1e-9))


def main() -> Path:
    out = ROOT / "results" / "feasibility" / "T_A_sweep.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for T in (2.0, 2.5, 3.0, 3.5, 4.0):
        for ov in (0.0, 0.5, 0.667, 0.75):
            for c in _cases():
                v = assess(track="A", T_s=T, **c)
                wpr = windows_per_record(RECORD_S[c["dataset"]], T, ov)
                deciding = LABEL_SPACE_FAMILIES[c["label_space"]]
                est_train = wpr * PU_TRAIN_RECORDS_SMALLEST_CLASS if c["dataset"] == "PU" else None
                sep = min(v.separations[f] for f in deciding)
                fails = list(v.failures)
                if wpr < 1:
                    fails.append("no window fits in a record")
                if est_train is not None and est_train < TRAIN_MIN:
                    fails.append(f"est_train_windows_per_class {est_train} < {TRAIN_MIN}")
                rows.append(dict(dataset=c["dataset"], bearing=c["bearing"], condition=c["condition"],
                                 T_A=T, overlap_frac=ov, record_length_s=RECORD_S[c["dataset"]],
                                 windows_per_record=wpr, est_train_windows_per_class=est_train,
                                 delta_f_hz=round(1 / T, 4), bpfo_hz=round(getattr(__import__("kinematics").kinematics(c["bearing"]), "BPFO") * c["rpm"] / 60, 3),
                                 sep_from_nearest_shaft_harmonic_bins=round(sep, 2),
                                 pooled_family_bins_N=min(v.family_bins[f] for f in deciding),
                                 revolutions_per_window=round(v.revolutions, 1),
                                 raw_input_samples_per_window=int(round(T * c["fs_hz"])),
                                 certified=not fails, failures="; ".join(fails)))
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    by = {}
    for r in rows:
        by.setdefault((r["T_A"], r["overlap_frac"]), []).append(r["certified"])
    print("T_A  overlap  all_certified  PU windows/record")
    for (T, ov), oks in by.items():
        wpr = windows_per_record(4.0, T, ov)
        print(f"{T:3.1f}  {ov:5.3f}    {all(oks)!s:5s}          {wpr}")
    return out


if __name__ == "__main__":
    print("wrote", main())
