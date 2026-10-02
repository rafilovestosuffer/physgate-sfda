# notes/vieira_2026.md — Vieira, Bauler, Rosa & Silva, MSSP 258:114640 (2026)

**Status: [VERIFIED — open preprint arXiv 2509.22267 v2 read; journal version exists, PII
S0888327026007971]** 2026-09-13. Numbers below are from the preprint; re-check against the journal
version before quoting a figure.

## What they do

- **Bearing-wise partitioning**, argued as the only leakage-free split within one test bench.
- **CWRU:** healthy signals for training from one sensor location and test healthy from the opposite
  end (DE ↔ FE); fault size selected at random per location–type; 3-fold CV for tuning, 50 further
  2:1 splits for evaluation.
- **PU:** 4:2 bearings for healthy and inner, 3:2 for outer; combined-damage bearings excluded.
- **UORED-VAFCLS:** 3:2 bearings per fault mode; 5 splits for tuning, 100 disjoint for evaluation;
  severity levels of one bearing are the **same physical bearing** (a severity split leaks).
- **CVM-CV:** cross-validated hyperparameter search, then re-evaluation on fresh disjoint splits.
- **Multi-label formulation**: each fault mode is an independent binary problem; metric **macro-AUROC**
  (prevalence-independent, threshold-free).
- **Controlled leakage experiment:** same model, leaked vs clean test set (synthetic toy + UORED with
  varying train/test bearing ratios).
- **Scope, explicitly:** cross-domain / inter-testbench work is named as the alternative they do
  **not** pursue; they study train and test within a single test bench. No SFDA.

## What we adopt, what we differ on, and why (goes into §Evaluation Protocol)

| Topic | Adopt | Differ | Why |
|---|---|---|---|
| Bearing-wise splits | yes — cited as methodology source | — | it is correct and published |
| PU fold sizes | our mechanical two-fold rule (splits.yaml) | not 4:2 / 3:2 | M1 needs *paired* leaky/clean targets on the same source model (C32); two disjoint folds are the paired design |
| UORED | 3:2 per fault mode, by `bearing_id`, never by severity (asserted) | — | directly comparable numbers |
| CWRU healthy | implement their DE↔FE construction as a named split, alongside ours | we **measure** the contamination they conservatively assume (B6a, C64) | they exclude opposite-end-faulted healthy signals because they "may contain artifacts"; our gate can quantify it and, if absent, recover that data |
| Metric | macro-AUROC as a **secondary** table | headline stays oracle-gap closure + Δ_leak (frozen) | frozen metrics cannot be replaced; AUROC makes tables comparable |
| Hyperparameters | tuning on source splits only | no CVM-CV on target | SFDA forbids target labels; CVM-CV assumes labelled evaluation folds |
| Setting | — | cross-machine, source-free | their stated out-of-scope region is our claim 3 |

## Evaluation numbers (verified in v2 raw HTML, 2026-09-13; re-check journal version before quoting)

All macro-AUROC, WDCNN unless stated.

| Dataset (their protocol) | splits | time | frequency | envelope | best shallow |
|---|---|---|---|---|---|
| UORED, Table 8 | 100 eval | 90.69 ± 5.43 | 93.12 ± 4.26 | 89.57 ± 5.34 | RF 85.58 ± 4.74 |
| PU real-damage subset, Table 9 (WDCNN + dropout) | 100 eval | 59.51 ± 14.14 | 61.89 ± 13.65 | **80.16 ± 14.48** | RF 69.67 ± 15.73 |
| CWRU, Table 10 | 100 eval | 63.22 ± 10.24 | 70.90 ± 8.95 | 74.51 ± 9.43 | **RF 84.40 ± 9.31** |
| UORED tuning, Table 7 (5 tuning splits, best config — optimistic by construction) | 5 | RESNET1D 76.05; WDCNN 91.47 | RESNET1D 87.60; WDCNN 93.24 | — | — |

Controlled leakage (model fixed, test set varied):

| | clean | bearing-level leak | segmentation leak |
|---|---|---|---|
| UORED Table 11 (time / freq) | 91.80 / 74.81 | 94.18 / 81.22 (+2.4 / +6.4) | 99.15 / 90.11 (+7.3 / +15.3) |
| PU Table 12 (time / freq) | 53.2 / 53.3 | condition-wise 85.9 / 92.4; repetition-wise 98.3 / 99.9 | 98.2 / 100.0 |
| CWRU (time / freq) | 66.4 / 62.4 | condition-wise 99.9 / 100.0 | 99.8 / 99.9 |

No envelope-spectrum column exists in the leakage tables. Their PU discussion: with time/frequency input
bearing identity dominates; envelope input suggests specialised features reduce memorisation.

**What this means for us.** An honest *within-dataset, supervised* PU number is ~80 ± 14 macro-AUROC with
the best input. Cross-machine source-free numbers on PU should be expected below that. Every accuracy table
prints the matching Vieira row beside ours (C57).
