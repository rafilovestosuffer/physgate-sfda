# M2/M3 single run (PROTOCOL C81) — pre-registered decisions on record; C82 repeat control pending

Artifacts `results/artifacts/physgate-m2-fa/`, `-fb/` (predictions, gate masks, logs); ledger rows `m2-*`.
12 bearing-wise clean tasks, final_checkpoint, seed 2024, one run per arm.

| task | none | c30 | v2 | pcv | eagle | oracle |
|---|---|---|---|---|---|---|
| A A1→A3 | 76.13 | 83.33 | 83.33 | 83.33 | 82.38 | 86.27 |
| A A1→A2 | 76.98 | 76.93 | 76.98 | 78.72 | 81.27 | 84.20 |
| A A3→A1 | 61.12 | 68.15 | 68.88 | 68.88 | 67.75 | 86.65 |
| A A3→A2 | 57.72 | 57.33 | 57.72 | 58.73 | 60.07 | 86.22 |
| A A2→A1 | 34.07 | 38.70 | 38.68 | 38.68 | 40.12 | 87.90 |
| A A2→A3 | 34.55 | 45.53 | 38.68 | 38.70 | 41.08 | 99.98 |
| B A1→A3 | 55.33 | 58.38 | 58.53 | 69.85 | 38.23 | 75.70 |
| B A1→A2 | 55.27 | 55.23 | 55.23 | 55.22 | 44.87 | 81.22 |
| B A3→A1 | 55.33 | 60.07 | 63.40 | 61.90 | 44.70 | 75.18 |
| B A3→A2 | 55.28 | 55.23 | 55.23 | 55.28 | 44.77 | 81.73 |
| B A2→A1 | 55.33 | 62.62 | 62.15 | 63.38 | 35.32 | 74.12 |
| B A2→A3 | 55.33 | 58.12 | 58.43 | 68.18 | 44.70 | 72.90 |
| **mean** | **56.04** | 59.97 | 59.77 | **61.74** | 52.11 | **82.67** |

## C81 decisions (single run)

| | mean gain | Wilcoxon (1-sided, 12 tasks) | "helps" rule | OGC (12 tasks, G ≥ 2 pp) | P1: A2-target |Δ| < 1 pp |
|---|---|---|---|---|---|
| c30 | +3.93 | 0.010 | yes | 0.18 | holds |
| v2 | +3.73 | 0.007 | yes | 0.19 | holds |
| pcv | **+5.70** | 0.001 | yes | **0.30** | fails (1.74, 1.01 on fold A) |
| eagle | −3.93 | 0.92 | no | −0.17 | fails (−10.4 on fold B) |

- **M3: oracle gap G = 26.6 pp mean** (7–65) ⇒ pseudo-label noise **is** the bottleneck (rule threshold 3 pp).
- **P2 holds:** EAGLE-style gating hurts (−3.9 pp; −10 to −20 pp on every fold-B task).
- Pseudo-label precision of kept labels: c30 0.580 → 0.619, v2 0.576 → 0.619, pcv 0.578 → 0.636, eagle 0.552 → 0.541, oracle → 1.000.

## M1's per-bearing labelling — VERIFIED from dumped predictions

Fold B → A, `none`: per-bearing label purity **1.000** on every task (each physical bearing receives exactly one label:
K001–K003 → normal ✓, KA15 → outer ✓, KI16 → inner ✓, KA04/KA16 → inner ✗, KI04 → normal ✗, KI14 → outer ✗).
The PCV gate breaks the lock exactly on the gate-engaged bearings (KA04 purity 0.56, KA16 0.74; accuracy 55.3 → 69.9 %).

## Why these numbers are not yet the paper's (C82)

`none` here has the same configuration and seed as M1's final_checkpoint clean run, yet differs on fold A by
+0.17, +0.10, −5.48, −11.76, +3.87, +4.03 pp per task (fold B: identical). Single-run gains of 4–6 pp are the same order as
that swing, so the robust decision waits for the pre-registered repeats.
