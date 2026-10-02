# C104 - same-condition, bearing-disjoint control

Random forest, ten time statistics, trained on half of the source bearings' recordings at one condition and
tested at the SAME condition. Balanced accuracy (%), mean over the three conditions.

| Split | Leaky (same bearings, held-out recordings) | Clean (other bearings) | Delta same-condition | Delta cross-condition (C101) |
|---|---|---|---|---|
| S00 | 94.2 | 75.5 | 18.7 | 16.4 |
| S01 | 91.1 | 60.0 | 31.1 | 20.7 |
| S02 | 96.5 | 71.2 | 25.3 | 23.9 |
| S03 | 99.1 | 55.3 | 43.7 | 32.4 |
| S04 | 91.0 | 75.9 | 15.1 | 2.5 |
| S05 | 93.9 | 52.0 | 42.0 | 38.5 |
| S06 | 93.9 | 77.3 | 16.5 | 15.0 |
| S07 | 98.2 | 70.0 | 28.2 | 21.4 |
| S08 | 91.9 | 51.5 | 40.5 | 35.9 |
| S09 | 95.9 | 58.9 | 37.0 | 26.7 |
| fold A | 96.4 | 66.3 | 30.1 | -- |
| fold B | 99.7 | 57.6 | 42.1 | -- |

Ten splits: median Delta_same **29.7 pp**, positive in 10/10, exact sign-flip p = 0.0010. Cross-condition RF (C101, same features): median 22.7 pp.

Pre-registered rule (median >= 10 pp and p < 0.05): **IDENTITY ALONE PRODUCES THE COLLAPSE**.

## Secondary (descriptive): outer-race recall on clean targets, by damage mechanism

- fatigue pitting (KA04, KA16, KA22): median 64 % over 10 target sets
- plastic deformation (KA15, KA30): median 23 % over 8 target sets

