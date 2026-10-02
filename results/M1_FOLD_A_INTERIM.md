# M1 fold A (source bearing fold A) — INTERIM, not the C32 decision (needs fold B)

Artifacts `results/artifacts/physgate-m1-fa/`. PU real-damage subset, L3, 2,000 windows per class per target (balanced),
seed 2024, SDALR released hyperparameters. **Source-only = the source model's accuracy on the same target at adaptation
batch 0** (logged by SDALR before any update).

| task | leaky: src-only / SDALR rel / SDALR final | clean: src-only / SDALR rel / SDALR final |
|---|---|---|
| A1→A3 | 98.32 / 99.88 / 99.88 | 63.23 / 76.63 / 76.30 |
| A1→A2 | 75.93 / 80.38 / 78.42 | 68.47 / 77.08 / 77.08 |
| A3→A1 | 99.73 / 99.98 / 99.97 | 57.53 / 66.60 / 66.60 |
| A3→A2 | 83.80 / 86.62 / 85.78 | 67.82 / 73.53 / 69.48 |
| A2→A1 | 82.97 / 84.50 / 83.02 | **36.33 / 34.03 / 30.20** |
| A2→A3 | 84.70 / 85.55 / 82.92 | **36.18 / 34.37 / 30.52** |
| **mean** | 87.58 / 89.49 / 88.33 | **54.93 / 60.37 / 58.36** |

## Decomposition (fold A only)

| effect | pp |
|---|---|
| bearing-wise split, source-only (87.58 → 54.93) | **−32.7** |
| bearing-wise split, SDALR as released (89.49 → 60.37) | **−29.1** |
| SDALR adaptation gain, leaky / clean (final checkpoint) | +0.8 / +3.4 |
| target-label checkpoint selection (as_released − final), leaky / clean | +1.2 / +2.0 |

## Sanity checks (rule 9 applied to a suspiciously low number)

- **No class collapse.** Final confusion on A2→A1 (as released): normal → 33 % normal / 67 % inner; inner → 22 % inner /
  78 % outer; outer → 47 % outer / 53 % inner. A systematic class *shift*, not a single-class output.
- **Targets balanced** (2,000 per class) — 1/3 is chance; 34 % twice is at chance, not below it.
- **The source model is already at chance before adaptation** on both A2-source clean tasks (36.3 %, 36.2 %). SDALR does not
  destroy transferable signal that existed; it removes a little more (−2 to −6 pp, more with the final checkpoint). Where
  source-only has signal (A1-, A3-source: 57–68 %), SDALR adds +6 to +13 pp on clean targets. **Adaptation is mildly harmful
  only where there is nothing to adapt.**
- A2 = N15_M07_F04 (400 N radial load). A source trained only on that condition does not transfer across bearings at all —
  consistent with bearing-identity memorisation (Vieira) under the lowest-load condition; to be tested on fold B.
