# Gate ROC on Paderborn (C73 iv) — the simple envelope rule dominates the whole curve

Artifacts `roc_pu.json`, `roc_pu.png`, script `experiments/gate_roc.py`. Population = H6-C35 (2,319 records; 480 healthy,
1,839 inner/outer). Every previously reported operating point is reproduced exactly by the sweep (C30 α 0.05: 309 correct /
9 FA; comb_v2: 312 / 0; PCV z 10: 366 / 1; EAGLE z 2: 429 / 214).

| gate (swept parameter) | at 0 healthy FA: best correct (wrong family) | at ≤ 2 % FA (≤ 9/480) | at ~11 % FA |
|---|---|---|---|
| PCV-style SES rule (z) | **351** at z 15 (4); 343 at z 20 (0) | **373** at z 8, FA 8 (18) | 439 at z 5, FA 68 |
| comb_v2 (α) | 312 at α ≤ 0.05 (2–3) | 317 at α 0.2, FA 6 | 325 at α 0.4, FA 11 |
| comb C30 (α) | — (min FA 2 at α 0.004: 305) | 309 at α 0.05, FA 9 (21) | 323 at α 0.1, FA 22 |
| EAGLE-style raw-STFT rule (z) | 0 at z 5 | — | 340 at z 4, FA 55 |

**Reading.** On this dataset the PCV-style rule (strict z threshold on the median-normalised squared envelope spectrum in
kinematic slip windows, no pre-whitening, no statistical null) lies on or above every other gate at every false-acceptance
level; comb_v2 dominates C30; EAGLE-style is dominated everywhere. The comb test's statistical machinery does not buy a better
operating curve here — H7's point result generalises to the full ROC. No gate exceeds 24 % correct verdicts before false
acceptance passes 10 %, which is the coverage ceiling (C65). Records within a bearing are correlated (C56); the curve is
driven by ~6 engaged bearings, so its shape is a statement about this dataset, not about envelope gating in general.
Caveat: PCV-style is evaluated on the raw (none) arm, the comb gates on the cepstrum arm, as pre-registered in C53/C72.

**Correction (2026-09-29).** "No gate exceeds 24 % correct verdicts before false acceptance passes 10 %" is not supported by `roc_pu.json`: the largest correct-verdict count at false acceptance <= 10 % is 373/1839 = 20.3 % (PCV-style, z = 8, FA 8/480). The statement holds at about 20 %. The EAGLE-style rule's first correct verdicts appear at FA 55/480 = 11.5 % (z = 4).
