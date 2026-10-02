# H6 — pre-whitening and the 6203 shaft-harmonic lock (Paderborn, out-of-sample)

Pre-registered: C28, re-specified C31 (comb detector), C33 (band <= 15 kHz), C34 (3.9 s crop, 1 unreadable file
excluded) — all committed before any verdict. 2,319 records, 29 bearings, 4 conditions, L3, alpha = 0.05.
**No version of the detector had touched Paderborn data before this run.**

## Pre-registered decision: NOT SUPPORTED

H6 required the `none` arm to be AT CHANCE. It is not.

| Arm | Outer precision | 95 % CI | Prevalence | At chance | Materially above |
|---|---|---|---|---|---|
| none | 0.690 (176/255) | 0.631–0.744 | 0.414 | **no** | yes |
| cepstrum | 0.955 (149/156) | 0.910–0.978 | 0.414 | no | **yes** |

The lock degrades a frequency-position-sensitive gate but does not reduce it to chance.

## What the data does show (reported regardless of the decision)

- **Pre-whitening removes the confusion the lock predicts.** Inner-race records called outer: **79 → 7** (−91 %).
  Outer precision 0.69 → 0.955. Inner precision 0.87 → 0.88 (unchanged).
- **Real-data false-acceptance (claim 3).** Healthy records called faulty: none 18/480 = 3.7 % [2.4, 5.8];
  **cepstrum 15/480 = 3.1 % [1.9, 5.1]**, below nominal alpha = 0.05. All false acceptances are "inner race";
  none are "outer race".
- **Coverage is low.** The gate admits a fault class for 15 % (cepstrum) of records; 80–85 % are called normal.
  Consistent with M4b: a conservative screen that abstains rather than mislabels.

Confusion (true → gate), cepstrum: normal {465 normal, 15 inner, 0 outer}; inner {705 normal, 168 inner,
7 outer}; outer {802 normal, 8 inner, 149 outer}.

## Interpretation limits

- Precision per class is pooled over artificial and real damage and four conditions; the per-bearing and
  per-condition breakdown is in `h6_records.csv` and has not yet been analysed.
- The CWRU M4b result (all 17 fault verdicts correct) and this one are consistent in direction; Paderborn is
  harder (outer precision 0.955, not 1.0; inner precision 0.88).
