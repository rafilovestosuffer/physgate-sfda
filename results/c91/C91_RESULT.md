# C91 — shallow non-adaptive baseline on the M1 paired design (Kaggle CPU)

Artifact: `results/artifacts/physgate-c91-shallow-cpu/c91/c91_result.json`. Random forest, 500 trees, seed 0, no tuning, no
adaptation. 12 paired tasks per feature set; purity = mean per-bearing label purity on clean targets.

| features | leaky | clean | Δ_leak | Wilcoxon p | clean purity |
|---|---|---|---|---|---|
| T (10 time statistics) | 88.80 | **63.58** | 25.22 | 0.0017 | 0.95 |
| F (64 log FFT bands) | 93.23 | 52.58 | 40.65 | 0.0002 | 0.92 |
| E (64 SES bins, 0–2 kHz) | 76.65 | 43.14 | 33.52 | 0.0002 | 0.76 |
| T+F+E | 95.42 | 60.31 | 35.11 | 0.0002 | 0.92 |
| *SDALR final_checkpoint (M1)* | *94.12* | *56.84* | *37.28* | *0.0002* | *1.000* |

## Reading (pre-registered rules)

1. **Every feature set has Δ_leak ≥ 10 pp**, so the collapse is attributed to the data and split, not to SDALR. A
   source-trained classifier with no deep features and no adaptation collapses by 25–41 points and also labels bearings
   nearly as wholes (purity 0.76–0.95).
2. **Flag:** time-statistics RF clean accuracy (63.58 %) exceeds SDALR final_checkpoint clean (56.84 %) by 6.7 pp, which is
   ≥ 5 pp. **The manuscript must report this stronger clean baseline.** SDALR with the envelope threshold gate
   (three-seed mean 63.2 %, C83) only reaches the level of a 10-feature random forest without adaptation.

## Implications

- Strengthens the leakage thread: memorisation is generic to source-trained classifiers on this rig.
- Weakens any framing of gated SDALR as a strong clean-target method. Report it as "recovers part of the collapse", with the
  shallow baseline beside it.
- Descriptive only: one seed, two folds. Candidate to add to the C88 splits (CPU, cheap).
