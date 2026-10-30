# Supplementary S1 — protocol: what was fixed in advance and what changed

The study followed a dated, version-controlled protocol, PROTOCOL.md, archived with the code and results (release v1.6, https://doi.org/10.5281/zenodo.23105809). An entry is called pre-specified when it was committed before the runs it governs; the study was not registered with an external registry (main text, Section 4.6). This supplement summarises the entries that bear on the reported results; PROTOCOL.md gives the full text, date and reason of every entry, including implementation details not listed here.

## S1.1 Fixed before the corresponding runs

| Entry | What was fixed | Reported in |
|---|---|---|
| C30 | Comb-test gate with a record-specific surrogate-order null and a two-line multiplicity rule. | Section 5 |
| C32 | Paired design: one source model adapted to a seen-bearing and an unseen-bearing target at the same condition, with SDALR's released code, windows and seed. | Section 4.1 |
| C72 | Shaft-alias-guarded comb (comb_v2). | Section 5 |
| C81 | Gates inside SDALR's adaptation loop, run in the same job and from the same source checkpoint as the ungated arm. | Sections 4.4, 6.6 |
| C83 | Three seeds on the two mechanical folds. | Sections 4.5, 6.6 |
| C88 | Ten random 3/3/3 source draws from the 17 bearings, and the decision rule for the gap. | Sections 4.2, 6.2 |
| C90 | Slip measured on the recordings. | Supplementary S5 |
| C91, C92 | Random forests on the folds and on the ten splits. | Section 6.3 |
| C94 | The same design on a second rig (HUST), with its decision rule. | Section 6.3, S6.12 |
| C104 | Same-condition, bearing-disjoint control without adaptation, with its decision rule. | Section 6.3 |
| C113 | Corrected SHOT implementation on the ten splits. | Section 6.3 |
| C110, C111, C112 | Exploratory follow-ups: source-diversity curve, identity-probe ablations, kinematic-feature forest. | Section 6.4 |

## S1.2 Departures, withdrawals and corrections

| Entry | What changed | Reported in |
|---|---|---|
| C117 | The protocol asked for five seeds per configuration. SDALR's released seed (2024) was adopted before the first paired run, and split-level variance replaced seed-level variance. | Section 4.5 |
| C85, C100, C113 | The first SHOT implementation returned pseudo-labels in the order of a shuffled loader pass. Its outputs are withdrawn, and the corrected implementation was run on the ten splits. | Section 4.3, S6.1 |
| C87, C93 | A planned bearing-identity remedy was withdrawn before any run, and its replacement was not run to a decision; no remedy result is reported. | Section 9 |
| C70 | UORED shaft speed could not be resolved from the recordings, so no UORED arm is primary. | Supplementaries S2, S3 |
| C103, C103b | The explanation of the accuracy difference between two jobs was revised from the retained logs and code. | Section 4.6 |
| C118-C121, C123 | Reporting corrections made before submission (wording, interval labels, citations, code-line evidence); no new run and no changed result. | Supplementary S6 |

## S1.3 Analyses added after results were seen

These analyses are post hoc and descriptive; none has a decision rule.

| Entry | Analysis | Reported in |
|---|---|---|
| C56 | Physical bearing as the statistical unit for real-data intervals. | Supplementary S6 |
| C95 | Which bearings the gates can act on. | Section 6.6 |
| C96 | Cluster-level inference and the Benjamini-Hochberg family (S1.4). | Section 4.5, S6 |
| C97 | Identity probe on handcrafted statistics. | Section 6.4 |
| C98 | In-loop gate coverage and its association with the gain. | Section 6.6 |
| C99 | Off-rig calibration of the gate operating point. | Section 6.6 |
| C102 | Repeated executions of one configuration (A/A floor). | Section 4.6 |
| C104b | Per-class breakdown of the same-condition control. | Section 6.3 |
| C105 | Source-only arm. | Section 6.2 |
| C106 | Within-bearing seen-versus-unseen contrast. | Section 6.2 |
| C107 | Gate gain by window group. | Section 6.6 |
| C108 | Block labelling on seen and unseen bearings. | Section 6.4 |
| C109, C115 | Order-statistic intervals for every reported median; leave-one-bearing-out check. | Sections 4.5, 6.2; S6.11 |
| C114 | Labels given to seen and unseen bearings; KI04/KI14 sensitivity. | Section 6.4, S6.10 |
| C116 | Gate override and gain by certifiable bearings. | Section 6.6 |
| C122 | Outer-race composition of the two targets. | Section 6.2, S6.11 |

## S1.4 Multiplicity family at each stage of revision

Benjamini--Hochberg adjustment of the exact cluster-level sign-flip p-values, over every primary cluster-level
test in the paper at that stage. Generated from the version history of `results/c96/C96_RESULT.md`; a dash
means the test was not yet a member. The historical family is retained unchanged, including the withdrawn SHOT test (S6). Its inclusion preserves the audit trail, not valid SHOT evidence. All p-values are nominal and do not establish population-level error control.

| member | stage 1 (2026-09-22, `24be642`) p / p_BH | stage 2 (2026-09-22, `4bf21f1`) p / p_BH | stage 3 (2026-09-22, `3564cfa`) p / p_BH | stage 4 (2026-09-29, `bfd4166`) p / p_BH | stage 5 (2026-09-29, `0044c6b`) p / p_BH |
|---|---|---|---|---|---|
| Collapse, two folds | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 |
| Collapse, ten random splits | 0.0010 / 0.0049 | 0.0010 / 0.0026 | 0.0010 / 0.0029 | 0.0010 / 0.0022 | 0.0010 / 0.0020 |
| Gate gain, ten random splits | 0.0029 / 0.0073 | 0.0029 / 0.0059 | 0.0029 / 0.0066 | 0.0029 / 0.0053 | 0.0029 / 0.0049 |
| Shaft-alias-guarded comb gain, two folds (seed 2024) | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 |
| Envelope threshold rule gain, two folds (seed 2024) | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 | 0.2500 / 0.2500 |
| RF (10 time statistics) collapse, ten splits | -- | 0.0010 / 0.0026 | 0.0010 / 0.0029 | 0.0010 / 0.0022 | 0.0010 / 0.0020 |
| RF (time + spectral + envelope) collapse, ten splits | -- | 0.0010 / 0.0026 | 0.0010 / 0.0029 | 0.0010 / 0.0022 | 0.0010 / 0.0020 |
| HUST collapse, six type-disjoint splits | -- | 0.0156 / 0.0250 | 0.0156 / 0.0281 | 0.0156 / 0.0234 | 0.0156 / 0.0223 |
| SHOT collapse, splits | -- | -- | 0.2500 (n = 2) / 0.2500 | 0.0010 (n = 10) / 0.0022 | 0.0010 (n = 10) / 0.0020 |
| Same-condition RF collapse, ten splits (C104) | -- | -- | -- | -- | 0.0010 / 0.0020 |
