# C87 N1 — is physical bearing identity linearly decodable from un-remediated source features? (PASS)

Artifact: `results/artifacts/physgate-run-n1-probe/` (Kaggle T4, co-author account). SDALR released source training, seed 2024,
M1 source folds A and B, one probe per source condition (6 probes). Record-disjoint halves by CRC32 parity of record_id.
Unit: record-level majority vote.

| source fold | condition | all-bearing record acc (class-only ceiling) | within-class record acc (pooled chance) |
|---|---|---|---|
| A | 1 | 92/92 (0.33) | 92/92 = 1.000 (0.333) |
| A | 2 | 91/91 (0.33) | 91/91 = 1.000 (0.333) |
| A | 3 | 87/88 (0.33) | 87/88 = 0.989 (0.333) |
| B | 1 | 81/81 (0.39) | 81/81 = 1.000 (0.374) |
| B | 2 | 77/77 (0.39) | 77/77 = 1.000 (0.377) |
| B | 3 | 79/79 (0.39) | 79/79 = 1.000 (0.376) |
| **pooled** | | | **507/508 = 0.998 vs chance ≈ 0.35** (binomial p < 1e-200) |

Window-level within-class accuracy is 0.97–0.99.

**Premise rule (C87): PASS.** Identity exceeds chance by about 65 pp, far beyond the 15 pp threshold. The source
representation encodes which physical bearing a window came from, even among bearings of the same class, almost perfectly.
Step 2 (BIST-W) therefore runs (`kaggle/kernels/bistw_F{A,B}.py`).
