# C79 — target-informed band selection (band search inside the null): NOT ADOPTED

Artifacts `c79_records.csv`, `c79_summary.json`. Cepstrum arm; `kurtogram` = frozen C30 pipeline, `iesfo` = `physics/iesfo_gate.py`.

| dataset | ball: kurt → iesfo | healthy FA: kurt → iesfo | I/O correct: kurt → iesfo | wrong family |
|---|---|---|---|---|
| CWRU DE | 0/16 → 0/16 | 0/4 → 0/4 | 17 → 17 /44 | 0 → 0 |
| CWRU FE | 0/12 → 0/12 | — | 10 → **25** /33 | 0 → 0 |
| UORED logged | 0/10 → 0/10 | 0/20 → **5/20** | 10 → 12 /20 | 1 → 4 |
| UORED FTF-speed | 0/4 → 0/4 | 0/5 → **4/5** | 4 → 3 /5 | 0 → 0 |
| PU healthy | — | 9/480 → 5/480 | — | — |

Rule: (i) ball +≥3 — **fails** (0 → 0); (ii) healthy FA not higher anywhere — **fails** (UORED 0 → 5/20 and 0 → 4/5); (iii) holds.

Reading:
- **Ball-fault misses are not a band-selection problem (this test) and not a sideband problem (C77).** 0/42 ball records are
  detected by either variant with pre-whitening. Stated as a limitation of envelope kinematic gating on these datasets.
- **Band search inside the surrogate null does not control false acceptance on UORED.** Taking the max over ~22 bands for the
  surrogates is not enough when records carry strong discrete combs (C71/C74): some band always aligns a family. Selection by
  the tested statistic stays unsafe even with this correction — a methodological result worth one sentence.
- Exploratory only: on CWRU FE it recovers 15 inner/outer detections with no wrong-family calls. Not adopted (rule is global).
