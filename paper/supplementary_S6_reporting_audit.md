# Supplementary S6 - Reporting audit and implementation details

Revision date: 9 October 2026. No model was fitted, no training job was submitted and no new experiment was conducted for this revision. All numerical corrections below use saved outputs. The original PROTOCOL.md, experimental outputs and original ledgers remain unchanged. A separate reporting ledger identifies the derived summaries.

## S6.1 Withdrawn local SHOT comparison

The intended SHOT comparator is withdrawn as evidence about SHOT. In runners/shot_patch.py, obtain_label concatenates features in loader traversal order and returns the resulting pseudo-label array in that order. The shared SDALR tools.args_data_load creates shuffled loaders. train_target later accesses mem_label[tar_idx], where tar_idx is the dataset sample index. The local patch neither restores dataset order nor uses a sequential loader for the pseudo-label pass. Consequently the assigned pseudo-labels need not belong to the samples receiving them.

This is a static code finding, not a corrected performance estimate. Results in C85 and C100 and their source-only/SHOT interpretations cannot establish SHOT performance or agreement across two SFDA methods. They have been removed from the main performance table, title, abstract and conclusions. Original code and outputs remain in the experimental archive for audit. No corrected run is available. The manuscript now evaluates SDALR with non-adaptive controls; generalisation to other SFDA methods is untested. The historical C96 multiplicity family is retained unchanged, including its withdrawn member, solely for traceability. Adjusted p-values remain nominal, not validation of the withdrawn comparison.

## S6.2 Architecture and optimisation

These settings are transcribed from the retained SDALR source and local wrapper, not tuned during this revision. Upstream SDALR revision: fb9c379. Sources: third_party/SDALR/model.py, tools.py, src_pretrain_RES_PU.py and tar_adaptation_RES_PU.py; runners/ and the recorded job configurations. The upstream code is obtained by the repository fetch script and is not redistributed in this reporting overlay.

| Component | Retained setting |
|---|---|
| Backbone | ResNet18_1D; one input channel; four stages with 2 blocks each and widths 64, 128, 256, 512; output feature dimension 512; backbone dropout 0.1 |
| Head | Batch-normalised bottleneck dimension 256; weight-normalised classifier |
| Source split | Window-random 70/10/20 training/validation/test partition within the source pool; this validation is not bearing-disjoint |
| Source training | 10 epochs; batch 64; base learning rate 0.007; parameter-group multipliers 1, 1, 1 |
| Source checkpoint | Highest source-validation accuracy at the two evaluation points (epochs 5 and 10); later ties replace earlier checkpoints |
| Optimiser | SGD; momentum 0.9; weight decay 0.001; Nesterov enabled |
| Learning-rate schedule | Initial group rate multiplied by (1 + 10 i / I)^(-0.75), where i and I are current and maximum update indices |
| Target adaptation | 20 epochs; batch 64; base learning rate 0.0005; group multipliers 0.1, 0.1, 1; mix 0; threshold 0.4; K 0.6 |
| Loss coefficients | cls_par, ent_par, gen_par and aad_par all 1 in the retained target configuration |
| Normalisation | z_score: scalar mean and standard deviation computed from the data in each loader subset; no class labels used. Each target loader covers the full target pool, so target normalisation is transductive |
| Noise | No added noise (standard deviation 0 in the retained data loader) |
| Target checkpoint | Fixed final iterate for every headline result; target-label-selected as_released variant shown only as a diagnostic |
| Seeds | Mechanical-fold gate runs: 0, 1, 2024; ten-split primary comparison: 2024 |

The released short-window input and the full-recording kinematic control have different temporal support and aggregation. Their gap difference does not isolate feature representation. The withdrawn local SHOT patch is not a valid second-method replication of these settings.

## S6.3 Kinematic accuracy sensitivity from saved values

C112 retained ordinary accuracy and clean_balanced for every split. The leaky record pool is class balanced; the clean pool has three healthy, three inner-race and two outer-race bearings. Ordinary and balanced clean accuracy therefore differ. The revised table reports both rather than overwriting the pre-specified ordinary-accuracy result.

| Summary | Original ordinary accuracy | Balanced-accuracy sensitivity |
|---|---|---|
| Median leaky-clean gap (percentage points) | 8.4 | 10.4 |
| Conditional bootstrap 95% interval for gap | 4.8 to 21.0 | 7.2 to 22.7 |
| Positive gaps | 9/10 | 10/10 |
| Median clean accuracy (%) | 56.1 | 54.4 |
| Mean clean accuracy (%) | 54.3 | 52.3 |

The original point-estimate decision rule was a gap below 10 points. The balanced sensitivity crosses that boundary. Neither threshold decision establishes equivalence or robust transfer, and the intervals overlap the boundary. The saved-score reaggregation is post-hoc; its nominal one-sided enumerated sign-flip p-value is 0.0009765625 under joint sign-symmetry assumptions. No population-level significance claim follows from repeatedly using the same bearing pool.

| Split | Leaky balanced (%) | Clean balanced (%) | Gap (pp) |
|---|---|---|---|
| S00 | 74.444 | 47.731 | 26.713 |
| S01 | 58.796 | 57.037 | 1.759 |
| S02 | 66.481 | 60.880 | 5.602 |
| S03 | 84.352 | 42.639 | 41.713 |
| S04 | 63.148 | 55.926 | 7.222 |
| S05 | 61.019 | 50.185 | 10.833 |
| S06 | 65.185 | 55.833 | 9.352 |
| S07 | 64.815 | 54.907 | 9.907 |
| S08 | 66.389 | 43.704 | 22.685 |
| S09 | 69.167 | 53.889 | 15.278 |

## S6.4 Source-expansion reporting correction

C110 increases source diversity and training volume together. Source subsets at successive sizes are separately drawn and are not necessarily nested. Median training-window counts across the saved condition-specific fits are 1043, 2129, 3210 and 4265 for one to four bearings per class (ranges 924-1254, 1848-2452, 2934-3463 and 3945-4461). No fit was repeated to obtain these counts.

The difference between endpoint medians is 28.8 points; the median of the paired endpoint differences is 15.4 points. These are different summaries and are labelled accordingly. The original Monte Carlo sign-flip result records zero exceedances in 100000 draws. The reporting correction is (0 + 1)/(100000 + 1), approximately 0.00001, rather than p = 0. This nominal exploratory calculation remains conditional on sign-flip assumptions and a reused bearing pool. The curve does not isolate a causal diversity effect or rule out identity-associated shortcuts.

## S6.5 False acceptance and statistical scope

The six healthy bearings contribute 80 recordings each. S2 lists their individual false-acceptance counts. Clopper-Pearson intervals over recordings assume independent records and cannot be used as new-bearing safety bounds. Bearing-bootstrap summaries with only six specimens are also limited. Low observed false acceptance is not a guarantee of deployment safety.

Split bootstrap intervals describe sensitivity within these fixed bearing pools. Reused source and target specimens induce dependence. Exact enumeration of sign patterns does not establish joint sign symmetry; BH/BY adjustments do not repair invalid underlying p-values. The original numbers are retained as conditional, assumption-dependent summaries, and the conclusions rely on observed effect sizes and directions rather than population-level significance claims.

## S6.6 Label filtering and pairing

A physical gate keeps an existing pseudo-label when it agrees with the recording verdict, and otherwise withholds that label from the supervised term. It does not overwrite labels. Silent recordings are unchanged. The oracle similarly keeps only already-correct labels; it does not replace incorrect labels by the truth. It is a comparator for this filtering operation, not a proven upper bound for all adaptation strategies.

Paired arms use the same source checkpoint according to job construction. Identical batch-0 accuracy is a consistency check, not cryptographic proof of checkpoint identity. Mechanical-fold leaky/clean and gate/oracle experiments came from different jobs, so Figure 2 omits gate/oracle markers on the fold rows; the main Paderborn accuracy table states each job's own reference. The ten random splits ran all arms in one job.

## S6.7 Revision provenance and availability

Reaggregation: paper/revision_reporting.py. Derived output: results/reporting_2026_10_09/reporting_corrections.json. Reporting lineage: results/ledger/reporting_2026_10_09.csv. Source SHA-256 checksums are recorded in that JSON. The original experimental release v1.0-submission is archived at https://doi.org/10.5281/zenodo.23105810. The local reporting revision has not been represented as an update to that public deposit. The revision overlay accompanying this submission must be applied to the original repository before regenerating revised tables and figures. Supplementary S4 and the package manifest enumerate sources.


## S6.8 Historical nominal tests (main-text reporting finalized 10 October 2026)

The following unchanged historical family is preserved for audit, not as population-level evidence. Overlapping splits do not establish joint sign symmetry; multiplicity adjustments do not fix that limitation. SHOT remains withdrawn.

| Historical effect | Nominal cluster p | BH | BY |
|---|---|---|---|
| collapse, two folds | 0.250000 | 0.250000 | 0.732242 |
| Collapse, ten random splits | 0.000977 | 0.001953 | 0.005721 |
| Gate gain, ten random splits | 0.002930 | 0.004883 | 0.014302 |
| Shaft-alias-guarded comb gain, two folds (seed 2024) | 0.250000 | 0.250000 | 0.732242 |
| Envelope threshold rule gain, two folds (seed 2024) | 0.250000 | 0.250000 | 0.732242 |
| RF (10 time statistics) collapse, ten splits | 0.000977 | 0.001953 | 0.005721 |
| RF (time + spectral + envelope) collapse, ten splits | 0.000977 | 0.001953 | 0.005721 |
| HUST collapse, six type-disjoint splits | 0.015625 | 0.022321 | 0.065379 |
| Same-condition RF collapse, ten splits (C104) | 0.000977 | 0.001953 | 0.005721 |
| SHOT collapse, 10 splits | 0.000977 | 0.001953 | 0.005721 |

The source-only gap-change analysis reported a two-sided nominal p = 0.18. The historical coverage-gain correlations reported nominal p = 0.0001 (label-free coverage) and p = 0.0009 (partial correlation controlling for headroom). These descriptive associations reuse the same split pool. HUST met the original nominal replication rule and BH adjustment, but not BY; this historical decision is not a population-level replication guarantee.

Historical healthy false-acceptance intervals: envelope threshold 0.0-1.2%, alias-guarded comb 0.0-0.8% (Clopper-Pearson over records, requiring independence); surrogate-null comb 0.8-2.9% and raw-spectrum rule 26.9-60.8% (bootstrap over six bearings). These intervals cannot establish deployment safety.

The 10 October finalization changes presentation, positioning and statistical interpretation only. No new result, model fit or experimental run was added.
