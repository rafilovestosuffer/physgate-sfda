# C94 — HUST bearing: second-rig replication of the leakage design (PROTOCOL C94)

SDALR final_checkpoint, seed 2024, L3 {normal, inner, outer}, domains = loads 0 / 200 / 400 W, Track R windows.
Source = 3 bearing types, clean target = the other 2. A type-disjoint target changes bearing size as well as identity,
so this is a stronger shift than Paderborn's and is reported as bearing identity **and** geometry.

| split | source types (62xx) | leaky | clean | Δ_leak |
|---|---|---|---|---|
| H0 | 6204, 6207, 6208 | 98.15 | 63.66 | 34.49 |
| H1 | 6204, 6205, 6207 | 100.00 | 69.08 | 30.92 |
| H2 | 6204, 6205, 6206 | 99.82 | 49.94 | 49.88 |
| H3 | 6205, 6206, 6207 | 100.00 | 67.50 | 32.50 |
| H4 | 6206, 6207, 6208 | 94.32 | 68.54 | 25.78 |
| H5 | 6205, 6206, 6208 | 99.98 | 38.86 | 61.12 |

**Decision:** median Δ_leak 33.50 pp [range 25.78, 61.12] over 6 splits, one-sided Wilcoxon p = 0.0156 → **the Paderborn conclusion REPLICATES on HUST** (C94 rule: median ≥ 10 pp and p < 0.05).
Mean leaky 98.71 %, mean clean 59.60 %.
