# C88 — K-split leakage evaluation (PROTOCOL C88)

Seed 2024, final_checkpoint, Track R, PU real damage. Split = mean over 6 condition-pair tasks.

| split | leaky | clean | clean + PCV gate | clean + oracle | Δ_leak | PCV gain | filter-recoverable | not recoverable |
|---|---|---|---|---|---|---|---|---|
| S00 | 91.52 | 66.51 | 69.65 | 89.00 | 25.02 | +3.15 | 22.50 (90 %) | 2.52 (10 %) |
| S01 | 96.10 | 39.83 | 62.46 | 95.11 | 56.27 | +22.62 | 55.27 (98 %) | 0.99 (2 %) |
| S02 | 88.80 | 51.56 | 60.90 | 73.89 | 37.25 | +9.35 | 22.34 (60 %) | 14.91 (40 %) |
| S03 | 93.77 | 58.61 | 57.16 | 75.54 | 35.16 | -1.45 | 16.93 (48 %) | 18.23 (52 %) |
| S04 | 82.19 | 74.03 | 77.61 | 92.12 | 8.16 | +3.58 | 18.09 (222 %) | -9.93 (-122 %) |
| S05 | 98.03 | 36.42 | 45.40 | 85.08 | 61.61 | +8.98 | 48.66 (79 %) | 12.95 (21 %) |
| S06 | 90.19 | 68.57 | 73.31 | 83.27 | 21.62 | +4.74 | 14.70 (68 %) | 6.92 (32 %) |
| S07 | 99.23 | 51.47 | 52.14 | 91.92 | 47.75 | +0.67 | 40.44 (85 %) | 7.31 (15 %) |
| S08 | 97.07 | 37.64 | 59.97 | 91.08 | 59.42 | +22.33 | 53.44 (90 %) | 5.98 (10 %) |
| S09 | 89.52 | 60.08 | 64.37 | 82.46 | 29.43 | +4.29 | 22.38 (76 %) | 7.05 (24 %) |

M1 directions (reported alongside, not in the primary statistics). Leaky and clean are both from the M1 job; the gated and oracle arms come from the gating job, whose own ungated clean arm was fold A 56.76, fold B 55.31, and gains are computed against that arm.

| M1 fold A | 88.33 | 58.36 | 61.17 | 88.54 | 29.97 | +4.41 | 31.77 (106 %) | -0.21 (-1 %) |
| M1 fold B | 99.91 | 55.31 | 62.30 | 76.81 | 44.60 | +6.99 | 21.50 (48 %) | 23.10 (52 %) |

**(L)** median Δ_leak 36.20 pp [range 8.16, 61.61], one-sided Wilcoxon p = 0.00098 → **LEAK GENERALISES**.
**(G)** median PCV gain +4.51 pp [range -1.45, +22.62], positive in 9/10, p = 0.0029 → **HELPS**.
**(D)** filter-recoverable share of the collapse: median 82 % [range 48, 222 %]; PCV closes a median 19 % of the oracle gap.

## C92 — random forest (time statistics) vs SDALR on clean targets

| split | RF-T clean | SDALR clean | difference |
|---|---|---|---|
| S00 | 71.06 | 66.51 | +4.55 |
| S01 | 63.08 | 39.83 | +23.25 |
| S02 | 64.74 | 51.56 | +13.18 |
| S03 | 58.41 | 58.61 | -0.20 |
| S04 | 74.46 | 74.03 | +0.43 |
| S05 | 52.04 | 36.42 | +15.62 |
| S06 | 73.05 | 68.57 | +4.48 |
| S07 | 68.18 | 51.47 | +16.71 |
| S08 | 53.09 | 37.64 | +15.45 |
| S09 | 58.06 | 60.08 | -2.02 |

Median difference +8.87 pp over 10 splits → **shallow baseline exceeds SDALR (≥ 5 pp)** (C92).
