# C98 - gate coverage inside the adaptation loop

The hook vetoes a pseudo-label only on a target record whose gate verdict is a fault class. Coverage is
therefore reported over the records of each experiment's own clean target set, at the three adaptation
conditions (N15_M01_F10, N15_M07_F04, N15_M07_F10). Descriptive; no new runs.

## Envelope threshold rule (`pcv_class`)

| Target | Records | Gate speaks | Share of all | Share of faulty | Correct when speaking | Faulty bearings engaged |
|---|---|---|---|---|---|---|
| fold A | 480 | 47 | 9.8% | 15.7% | 97.9% | 2/5 |
| fold B | 540 | 114 | 21.1% | 31.4% | 99.1% | 3/6 |
| S00 | 480 | 42 | 8.8% | 13.7% | 97.6% | 1/5 |
| S01 | 480 | 158 | 32.9% | 52.7% | 100.0% | 4/5 |
| S02 | 480 | 86 | 17.9% | 28.7% | 100.0% | 2/5 |
| S03 | 480 | 2 | 0.4% | 0.7% | 50.0% | 1/5 |
| S04 | 480 | 73 | 15.2% | 24.3% | 100.0% | 2/5 |
| S05 | 480 | 78 | 16.2% | 25.7% | 98.7% | 2/5 |
| S06 | 480 | 73 | 15.2% | 24.3% | 100.0% | 2/5 |
| S07 | 480 | 48 | 10.0% | 15.7% | 95.8% | 2/5 |
| S08 | 480 | 126 | 26.2% | 42.0% | 100.0% | 3/5 |
| S09 | 480 | 47 | 9.8% | 15.7% | 97.9% | 2/5 |

Median over the 12 target sets: gate speaks on 24.3% of faulty target records and engages 40% of faulty target bearings.

## Surrogate-null comb test (`comb_class`)

| Target | Records | Gate speaks | Share of all | Share of faulty | Correct when speaking | Faulty bearings engaged |
|---|---|---|---|---|---|---|
| fold A | 480 | 45 | 9.4% | 14.0% | 88.9% | 1/5 |
| fold B | 540 | 99 | 18.3% | 25.8% | 86.9% | 4/6 |
| S00 | 480 | 25 | 5.2% | 7.7% | 92.0% | 1/5 |
| S01 | 480 | 136 | 28.3% | 43.0% | 89.7% | 4/5 |
| S02 | 480 | 72 | 15.0% | 22.3% | 93.1% | 3/5 |
| S03 | 480 | 11 | 2.3% | 2.0% | 36.4% | 1/5 |
| S04 | 480 | 55 | 11.5% | 16.7% | 78.2% | 2/5 |
| S05 | 480 | 71 | 14.8% | 22.3% | 84.5% | 2/5 |
| S06 | 480 | 55 | 11.5% | 16.7% | 78.2% | 2/5 |
| S07 | 480 | 46 | 9.6% | 14.0% | 87.0% | 1/5 |
| S08 | 480 | 107 | 22.3% | 34.0% | 95.3% | 3/5 |
| S09 | 480 | 51 | 10.6% | 15.3% | 86.3% | 2/5 |

Median over the 12 target sets: gate speaks on 16.7% of faulty target records and engages 40% of faulty target bearings.

## Raw-spectrum band rule (`eagle_class`)

| Target | Records | Gate speaks | Share of all | Share of faulty | Correct when speaking | Faulty bearings engaged |
|---|---|---|---|---|---|---|
| fold A | 480 | 141 | 29.4% | 24.3% | 46.1% | 3/5 |
| fold B | 540 | 279 | 51.7% | 57.2% | 50.9% | 5/6 |
| S00 | 480 | 139 | 29.0% | 30.0% | 60.4% | 4/5 |
| S01 | 480 | 328 | 68.3% | 81.0% | 55.2% | 4/5 |
| S02 | 480 | 223 | 46.5% | 43.7% | 55.2% | 4/5 |
| S03 | 480 | 118 | 24.6% | 11.0% | 22.9% | 5/5 |
| S04 | 480 | 200 | 41.7% | 44.0% | 32.0% | 2/5 |
| S05 | 480 | 208 | 43.3% | 50.0% | 38.5% | 3/5 |
| S06 | 480 | 214 | 44.6% | 48.0% | 37.4% | 3/5 |
| S07 | 480 | 146 | 30.4% | 29.3% | 57.5% | 4/5 |
| S08 | 480 | 257 | 53.5% | 63.0% | 72.0% | 5/5 |
| S09 | 480 | 164 | 34.2% | 24.0% | 39.0% | 4/5 |

Median over the 12 target sets: gate speaks on 43.8% of faulty target records and engages 80% of faulty target bearings.

## Envelope rule: per-bearing engagement at the three adaptation conditions

C95 counted 7 of 11 real-damage bearings engaged over all four operating conditions. Adaptation uses three,
and over those three the count is lower; this is the figure the ceiling argument must use.

| Bearing | Damage mode (first-party profile) | Certified records |
|---|---|---|
| KA04 | fatigue / Pitting | 41/60 |
| KA15 | plastic deformation / particle-caused | 0/60 |
| KA16 | fatigue / Pitting | 40/60 |
| KA22 | fatigue / Pitting | 0/60 |
| KA30 | plastic deformation / particle-caused | 1/60 |
| KI04 | fatigue / Pitting | 0/60 |
| KI14 | fatigue / Pitting | 0/60 |
| KI16 | fatigue / Pitting | 32/60 |
| KI17 | fatigue / Pitting | 0/60 |
| KI18 | fatigue / Pitting | 45/60 |
| KI21 | fatigue / Pitting | 0/60 |

Engaged at the adaptation conditions: 5 of 11 real-damage bearings.

## Coverage predicts the gain

| Split | Gate speaks on faulty target records | Gate gain (pp) | Headroom (oracle - clean, pp) |
|---|---|---|---|
| S00 | 13.7% | +3.15 | 22.50 |
| S01 | 52.7% | +22.62 | 55.27 |
| S02 | 28.7% | +9.35 | 22.34 |
| S03 | 0.7% | -1.45 | 16.93 |
| S04 | 24.3% | +3.58 | 18.09 |
| S05 | 25.7% | +8.98 | 48.66 |
| S06 | 24.3% | +4.74 | 14.70 |
| S07 | 15.7% | +0.67 | 40.44 |
| S08 | 42.0% | +22.33 | 53.44 |
| S09 | 15.7% | +4.29 | 22.38 |

Spearman rho = 0.951, p = 2.3e-05 over 10 splits (the split is the unit).

### Is coverage a proxy for headroom?

Raised in review: a gate can only gain where the oracle shows room to gain, so the correlation above may
be a headroom effect wearing a coverage mask. It is not.

| Relation | Spearman rho | p |
|---|---|---|
| gain ~ coverage | 0.951 | 2.3e-05 |
| gain ~ headroom | 0.527 | 0.12 |
| coverage ~ headroom | 0.543 | 0.11 |
| gain ~ coverage, headroom partialled out | 0.976 | 1.5e-06 |
| gain ~ headroom, coverage partialled out | -0.067 | 0.85 |

Headroom on its own does not predict the gain at this sample size, and once coverage is partialled out it
predicts nothing at all; coverage survives partialling headroom out essentially undiminished.

