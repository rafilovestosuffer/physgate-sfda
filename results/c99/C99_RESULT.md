# C99 - operating point fixed off-rig, then applied to Paderborn

Calibration set: 24 healthy recordings from CWRU, UORED -- rigs that appear nowhere in the adaptation experiments.

## False acceptance on the calibration set as the threshold is swept

| z | healthy calibration records accepted as faulty |
|---|---|
| 2.0 | 14/24 |
| 2.5 | 14/24 |
| 3.0 | 15/24 |
| 3.5 | 10/24 |
| 4.0 | 10/24 |
| 4.5 | 10/24 |
| 5.0 | 8/24 |
| 5.5 | 10/24 |
| 6.0 | 8/24 |
| 6.5 | 6/24 |
| 7.0 | 6/24 |
| 7.5 | 6/24 |
| 8.0 | 6/24 |
| 8.5 | 6/24 |
| 9.0 | 7/24 |
| 9.5 | 6/24 |
| 10.0 | 4/24 |
| 10.5 | 4/24 |
| 11.0 | 4/24 |
| 11.5 | 4/24 |
| 12.0 | 4/24 |
| 12.5 | 4/24 |
| 13.0 | 3/24 |
| 13.5 | 3/24 |
| 14.0 | 3/24 |
| 14.5 | 3/24 |
| 15.0 | 3/24 |
| 15.5 | 3/24 |
| 16.0 | 3/24 |
| 16.5 | 3/24 |
| 17.0 | 3/24 |
| 17.5 | 3/24 |
| 18.0 | 3/24 |
| 18.5 | 3/24 |
| 19.0 | 2/24 |
| 19.5 | 2/24 |
| 20.0 | 2/24 |
| 20.5 | 2/24 |
| 21.0 | 2/24 |
| 21.5 | 2/24 |
| 22.0 | 2/24 |
| 22.5 | 1/24 |
| 23.0 | 1/24 |
| 23.5 | 1/24 |
| 24.0 | 1/24 |
| 24.5 | 1/24 |
| 25.0 | 1/24 |
| 25.5 | 1/24 |
| 26.0 | 1/24 |
| 26.5 | 1/24 |
| 27.0 | 1/24 |
| 27.5 | 1/24 |
| 28.0 | 1/24 |
| 28.5 | 1/24 |
| 29.0 | 1/24 |
| 29.5 | 1/24 |
| 30.0 | 1/24 |
| 30.5 | 1/24 |
| 31.0 | 1/24 |
| 31.5 | 1/24 |
| 32.0 | 1/24 |
| 32.5 | 1/24 |
| 33.0 | 1/24 |
| 33.5 | 1/24 |
| 34.0 | 1/24 |
| 34.5 | 1/24 |
| 35.0 | 1/24 |
| 35.5 | 1/24 |
| 36.0 | 0/24 |
| 36.5 | 0/24 |
| 37.0 | 0/24 |
| 37.5 | 0/24 |
| 38.0 | 0/24 |

Smallest z with zero false acceptance off-rig: **z* = 36.0**. The pre-registered Paderborn operating point is z = 10.

The off-rig operating point is stricter than the pre-registered one, so a gate calibrated with no target-rig data would fire at most as often as the gate reported in the paper.

## Transfer to Paderborn (envelope-rule operating curve, `results/roc/roc_pu.json`)

The sweep has no point at z* = 36.0; the nearest point at or above it is z = 40.

| z | correct fault verdicts | healthy false acceptance |
|---|---|---|
| 10 (pre-registered) | 366/1839 | 1/480 |
| 40 (off-rig, nearest sweep point >= z*) | 333/1839 | 0/480 |

The off-rig point keeps 91 % of the pre-registered point's correct fault verdicts. Adaptation was not re-run at the off-rig point.

Per-record Paderborn harmonic peaks are not retained in `h7_records.csv` (only the verdict at z = 10), so the Paderborn side of the transfer is recomputed by `c99_pu_apply.py` if needed; the calibration result above stands on its own.
