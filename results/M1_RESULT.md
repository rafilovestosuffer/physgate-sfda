# M1 — leakage delta for SDALR on Paderborn (PROTOCOL C32): MATERIAL

Artifacts `results/artifacts/physgate-m1-fa/`, `physgate-m1-fb/`; ledger rows `m1-*`. PU real-damage bearings, L3, Track R
(2048 samples, 2,000 windows/class, balanced), seed 2024, released hyperparameters. Source-only = SDALR's own batch-0 accuracy
on the same target before any update.

## Decision (pre-registered): leak is MATERIAL

| variant | leaky mean | clean mean | Δ_leak mean [min, max] over 12 paired tasks | one-sided Wilcoxon |
|---|---|---|---|---|
| as_released | 94.71 | 57.84 | **36.87** [3.30, 51.18] | p = 0.00024 |
| final_checkpoint | 94.12 | 56.84 | **37.28** [1.34, 52.82] | p = 0.00024 |

## By source fold

| source fold → target | source-only | SDALR as released | SDALR final |
|---|---|---|---|
| A → A (leaky) | 87.58 | 89.48 | 88.33 |
| A → B (clean) | 54.93 | 60.37 | 58.36 |
| B → B (leaky) | 98.92 | **99.94** | 99.91 |
| B → A (clean) | 53.10 | **55.31** (every task 55.27–55.33) | 55.31 |

## Checks (rule 9, both directions)

- **99.9 % on B→B is the leak itself**: the same 9 physical bearings on both sides, condition changed.
- **55.3 % on all six B→A tasks is not noise and not collapse.** Confusion (every task): healthy 100 % correct; inner 33.0 % correct;
  outer 33.0 % correct with a 67.0 % single-class share. The A target has exactly 3 healthy, 3 inner, 3 outer bearings with windows
  spread evenly, so exact thirds is what per-bearing, all-or-nothing labelling produces: the model assigns each **physical bearing**
  one label, right for one of three. This is bearing-identity classification (Vieira's memorisation mechanism) observed directly.
  **Not verified at bearing level** — SDALR does not save per-window predictions; the M2 runner will dump them.
- **Adaptation cannot create signal that is absent**: clean source-only 53–55 %; SDALR adds +5.4 (fold A) and +2.2 (fold B) pp;
  target-label checkpoint selection adds +1.0–2.0 pp; the bearing-wise split costs **≈ 37 pp**.
- Design asymmetry disclosed: fold B has 2 outer-race bearings, fold A has 3 (5 real outer bearings in PU).
- One seed, one split per direction. C61 (≥ 10 bearing-level splits) applies to every later table; this M1 is the pre-registered
  two-fold design and is reported as such.
