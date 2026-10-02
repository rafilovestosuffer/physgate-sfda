# C78 — CWRU fan-end (6203) vs drive-end (6205) control for the slip–lock proposition: NOT SUPPORTED

Artifacts `c78_records.csv`, `c78_summary.json`. 45 FE-fault files (FE channel, SKF 6203) vs 60 DE-fault 12 kHz files
(DE channel, 6205); 5 s; per-file RPM; frozen C30 gate, L4, α 0.05; comb_v2 on the same spectra.

| arm · gate | FE 6203: I↔O confusions | DE 6205: I↔O confusions | Fisher (one-sided) | admitted & shaft-aliased FE / DE | correct I/O FE / DE |
|---|---|---|---|---|---|
| **none · C30 (primary)** | 6/33 (18.2 %) | 3/44 (6.8 %) | **p = 0.12** | 3/29 (10 %) / 0/30 | 23/33 / 17/44 |
| none · comb_v2 | 5/33 | 3/44 | 0.21 | — | 24/33 / 17/44 |
| cepstrum · C30 | 0/33 | 0/44 | 1.0 | 0/10 / 0/17 | 10/33 / 17/44 |
| cepstrum · comb_v2 | 0/33 | 0/44 | 1.0 | — | 10/33 / 17/44 |

Rule (a) fails (p = 0.12); (b) holds (10 % vs 0 %). **NOT SUPPORTED.**

Reading, without rescue:
- Both measures move in the predicted direction, but the difference is not significant at this n.
- **5 of the 6 FE confusions are not shaft-aliased** (only file 278 is); they are outer → inner calls without the lock
  signature. The proposition does not explain most FE errors. The 3 shaft-aliased admissions on FE (278 wrong; 299, 307
  correct) show the lock is present on this rig but rarely decisive.
- The FE 6203 is detected *better* than the DE 6205 without pre-whitening (23/33 vs 17/44), the opposite of what a
  damaging lock would produce. Plausible reason: actual CWRU slip is not near s* = 1.74 % (not measured here).
- Pre-whitening removes all I↔O confusions on both ends.

Consequence for the paper: the proposition (C75) remains an analytic statement with UORED/PU case evidence (C71, KI16);
**the CWRU within-rig control does not provide population-level support and is reported as such.**
Also noted: without pre-whitening, DE ball faults are detected in 3/16 records (C77 reported 0/16 for the cepstrum arm only).
