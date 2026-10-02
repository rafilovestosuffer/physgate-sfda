# H7 — frequency-position rules vs the comb gate (PROTOCOL C53): NOT SUPPORTED

Artifacts: `h7_records.csv`, `h7_summary.json`. Population = H6 C35 (2,319 PU records, 29 bearings, C35 geometry).
PCV-style and EAGLE-style are **our reimplementations** from PCTL Alg. 1 and Bio-SFDA §4.2 with constants fixed in C53.

## Pre-registered outcome

| classifier | outer precision [Wilson] | says outer | outer TP | inner TP | healthy false acceptance | I→O | O→I |
|---|---|---|---|---|---|---|---|
| comb gate (cepstrum, C30) | 0.955 [0.910, 0.978] | 155 | 148 | 161 | 9/480 (1.9 %) | 7 | 14 |
| **PCV-style rule** (raw SES, z > 10 in ≥ 2 of 3 harmonics) | **0.994 [0.969, 0.999]** | 181 | **180** | **186** | **1/480 (0.2 %)** | 1 | 7 |
| EAGLE-style rule (raw STFT ROI, robust z > 2) | 0.630 [0.584, 0.673] | 451 | 284 | 145 | **214/480 (44.6 %)** | 95 | 52 |

Outer prevalence 0.414. H7 required both rules at chance; neither is. **NOT SUPPORTED.**

## Per bearing (records n/i/o out of 80)

Substantive detections by the two envelope methods fall on the same bearings: KA01, KA04, KA16 (outer);
KI01, KI16, KI18 (inner). The other 17 fault bearings are "normal" for both in ≥ 72/80 records. The EAGLE-style
rule instead fires on healthy K001/K003/K006 (≥ 50/80 false calls each) and on KA09 (80/80 outer, where both
envelope methods see nothing).

## What this establishes, stated without softening

1. **The statistical machinery of the comb gate (surrogate-order null, common-δ alignment) buys nothing over
   a strict envelope position rule on Paderborn.** The rule is at least as precise, detects more, and false-alarms
   less. The claim that a cyclostationarity-order test is what makes physics gating work where position rules
   fail is **refuted on this dataset**.
2. **What matters is the domain, not the test.** Both envelope-domain kinematic screens are highly precise
   (0.955–0.994) with ≤ 2 % healthy false acceptance; a raw-spectrum ROI rule with activation-rate-adaptive
   thresholds false-accepts 45 % of healthy records. This is a measured, mechanism-level result about the
   *published* style of physics gating in SFDA.
3. **Coverage is a data ceiling.** Any envelope screen engages on ~6 of 23 fault bearings. Pseudo-label
   supply from physics gating on PU is therefore bounded by diagnosability, not by detector design — the PU
   analogue of Smith & Randall's CWRU finding.
4. Cluster caveat (C56): records within a bearing are correlated; comparisons above are driven by ~6 bearings.
   The EAGLE-style false-acceptance result is spread over all 6 healthy bearings and is the most robust number here.
