# comb_v2 (PROTOCOL C72) beside frozen C30 — same spectra, cepstrum arm

Artifacts `v2_records.csv`, `v2_summary.json`; synthetic null `results/calibration/null_drs_v2_2026-09-13.json` (FAR 0 in all 12 cells × 3 α).

| population | gate | healthy FA | outer says/TP/prec [bearings] | inner says/TP/prec [bearings] | ball | I→O | O→I |
|---|---|---|---|---|---|---|---|
| PU (2,319) | C30 | 9/480 | 155/148/0.955 [3/12] | 184/161/0.875 [7/11] | — | 7 | 14 |
| PU (2,319) | **v2** | **0/480** | 148/148/**1.000** [3/12] | 167/164/**0.982** [6/11] | — | **0** | **3** |
| CWRU (64) | C30 = v2 | 0/4 | 10/10/1.00 [4/7] | 7/7/1.00 [3/4] | 0 [0/4] | 0 | 0 |
| UORED logged | C30 = v2 | 0/20 | 5/5/1.00 [3/5] | 5/5/1.00 [4/5] | 1 call, 0 TP | 0 | 0 |
| UORED spectral | C30 | 0/20 | 10/4/0.40 [3/5] | 0 [0/5] | 1/1 | 6 | 0 |
| UORED spectral | v2 | 0/20 | 5/3/0.60 [3/5] | 0 [0/5] | 1/1 | 2 | 0 |

(PU bearing counts include artificial-damage bearings, as in the H6 population.)

**C72 rule:** v2 PU healthy FA 0 ≤ C30's 9 → **v2 retained as a co-reported gate arm.** No decision rule elevates it.

Reading:
- The shaft-alias guard + line-fraction arbitration removes every PU healthy false acceptance and nearly all cross-family
  confusion (21 → 3) with no loss of true detections (outer 148 = 148; inner 164 vs 161). Consistent with C71's mechanism.
- It does not restore inner detection on UORED's spectral-speed arm: guarding stops the wrong call but cannot find a family
  that is not aligned at that speed. UORED speed remains unresolved (C70).
- Against the PCV-style rule (H7: FA 1/480, outer TP 180, inner TP 186), v2 trades ~15 % fewer detections for zero false
  alarms. Neither dominates; both stay in the gate comparison (C65).
- These are post-hoc-designed (after C71's diagnosis) and pre-registered before running; they are labelled as a second
  generation everywhere, never merged with C30's pre-registered results.
