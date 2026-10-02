# C77 — ball family with J = 0 vs frozen J = 2: NOT a fix; characterised limitation

Artifacts `c77_records.csv`, `c77_summary.json`. Cepstrum arm, same band selection, only the BPFB family changed.

| population | ball detected J2 → J0 | false ball calls on non-ball J2 → J0 | healthy FA J2 → J0 |
|---|---|---|---|
| CWRU DE (ball n = 16) | 0 → 0 | 0 → 1 | 0/4 → 0/4 |
| UORED logged (ball n = 10) | 0 → 0 | 1 → 5 | 0/20 → 0/20 |
| UORED FTF-speed (ball n = 4) | 0 → 0 | 0 → 0 | 0/5 → 0/5 |

Rule (two-sided): ball detections did not increase → J = 0 is **not** adopted. The B_11_1 mechanism (cage-comb
contamination of the surrogate null for FTF-sideband families) is real for that record (p 0.038 → 0.002) but does not
translate into admissions and J = 0 adds wrong ball calls. **Ball faults are undetected by the frozen gate on both datasets
(0/26)**; consistent with Smith & Randall's finding that ball faults are the hardest CWRU category and with PLAN's
pre-registered expectation. Reported as a limitation, not hidden; H5 (sidebands help) is not supported for the ball family.
