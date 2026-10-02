# C83 seed control — INTERIM (seeds 2024 and 0; seed 1 pending quota reset)

Artifacts: `results/artifacts/physgate-m2-f*` (seed 2024), `physgate-m2seed-f*-s0` (seed 0). final_checkpoint, 12 clean tasks.

| task | none 2024 / 0 | v2 2024 / 0 | pcv 2024 / 0 |
|---|---|---|---|
| A A1→A3 | 76.13 / 83.33 | 83.33 / 83.33 | 83.33 / 83.33 |
| A A1→A2 | 76.98 / 77.27 | 76.98 / 77.27 | 78.72 / 78.85 |
| A A3→A1 | 61.12 / 73.48 | 68.88 / 80.23 | 68.88 / 80.23 |
| A A3→A2 | 57.72 / 68.72 | 57.72 / 68.72 | 58.73 / 70.25 |
| A A2→A1 | 34.07 / 27.67 | 38.68 / 38.67 | 38.68 / 38.67 |
| A A2→A3 | 34.55 / 27.67 | 38.68 / 38.68 | 38.70 / 38.68 |
| B A1→A3 | 55.33 / 55.33 | 58.53 / 58.70 | 69.85 / 71.75 |
| B A1→A2 | 55.27 / 55.28 | 55.23 / 55.20 | 55.22 / 55.27 |
| B A3→A1 | 55.33 / 44.32 | 63.40 / 49.05 | 61.90 / 52.70 |
| B A3→A2 | 55.28 / 55.27 | 55.23 / 55.27 | 55.28 / 55.27 |
| B A2→A1 | 55.33 / 55.25 | 62.15 / 60.67 | 63.38 / 69.88 |
| B A2→A3 | 55.33 / 55.33 | 58.43 / 58.62 | 68.18 / 73.35 |

| seed | none mean | v2 mean (gain, p) | pcv mean (gain, p) |
|---|---|---|---|
| 2024 | 56.04 | 59.77 (+3.73, 0.007) | 61.74 (+5.70, 0.001) |
| 0 | 56.58 | 60.37 (+3.79, 0.008) | 64.02 (+7.44, 0.002) |

2-seed mean: v2 gain +3.76 pp, Wilcoxon p = 0.0068; per-seed gains positive: True

2-seed mean: pcv gain +6.57 pp, Wilcoxon p = 0.0010; per-seed gains positive: True

Interim reading: both gates gain on both seeds so far (v2 +3.7/+3.8, pcv +5.7/+7.4). The C83 decision is taken only after seed 1.
