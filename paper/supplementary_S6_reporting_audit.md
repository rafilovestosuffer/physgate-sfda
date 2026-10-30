# Supplementary S6 - Reporting audit and implementation details

Revision date: 9 October 2026. No model was fitted, no training job was submitted and no new experiment was conducted for this revision. That statement covers the reporting revision of 9-10 October; the corrected SHOT run of 22-24 October (PROTOCOL C113, S6.1) is the only experiment added after it, and the sections marked as added later analyse retained outputs only. All numerical corrections below use saved outputs. The original PROTOCOL.md, experimental outputs and original ledgers remain unchanged. A separate reporting ledger identifies the derived summaries.

## S6.1 Withdrawn first SHOT implementation and its correction

The first local SHOT implementation (C85 and C100) is withdrawn as evidence about SHOT; the corrected run (C113) below replaces it. In runners/shot_patch.py, obtain_label concatenates features in loader traversal order and returns the resulting pseudo-label array in that order. The shared SDALR tools.args_data_load creates shuffled loaders. train_target later accesses mem_label[tar_idx], where tar_idx is the dataset sample index. The local patch neither restores dataset order nor uses a sequential loader for the pseudo-label pass. Consequently the assigned pseudo-labels need not belong to the samples receiving them.

This is a static code finding. Results in C85 and C100 cannot establish SHOT performance; their code and outputs remain in the experimental archive for audit only. The defect was corrected on 22 October 2026 (shot_patch v2, PROTOCOL C113: pseudo-labels scattered into dataset order, loader pass checked, unit-tested) and SHOT was re-run on the ten splits from the same source checkpoints (kernels physgate-shot2-k10-g1 to g4). Corrected result: median split-level loss 36.6 pp (conditional order-statistic interval 19.7--62.0), positive in 10 of 10; nominal one-sided sign-flip p = 0.0010; pre-specified rule met. The manuscript reports only the corrected run. The historical C96 multiplicity family is retained unchanged, including its withdrawn member, solely for traceability. Adjusted p-values remain nominal, not validation of the withdrawn comparison.

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
| Target adaptation | 20 epochs; batch 64; base learning rate 0.0005; group multipliers 0.1, 0.1, 1; mix 0; threshold 0.4 (a cosine distance to the nearest prototype, the counterpart of the paper's similarity threshold 0.6: tar_adaptation_RES_PU.py at fb9c379 computes cdist with the cosine metric, line 62, marks a window unreliable when that distance exceeds the threshold, line 69, and defaults to --distance cosine and --threshold 0.4, lines 408 and 442); K 0.6 (the paper's beta). In the gated runs SDALR's own criterion marks a median 0.6 % of target windows unreliable per pseudo-labelling round (95th percentile 3.9 %; 2 of 240 rounds above 10 %) [src: results/c116/c116_gate_override.json] |
| Loss coefficients | cls_par, ent_par, gen_par and aad_par all 1 in the retained target configuration |
| Normalisation | z_score: scalar mean and standard deviation computed from the data in each loader subset; no class labels used. Each target loader covers the full target pool, so target normalisation is transductive |
| Noise | No added noise (standard deviation 0 in the retained data loader) |
| Target checkpoint | Fixed final iterate for every headline result; target-label-selected as_released variant shown only as a diagnostic. Released rule (tar_adaptation_RES_PU.py at fb9c379): acc_init = 0 (line 139); at each evaluation point the accuracy on the labelled target loader (line 333, tools.cal_acc) is compared with acc_init and, when higher, becomes acc_init and the networks are saved (lines 347-356); after the last update the saved networks are reloaded and scored on the target (lines 358-366). final_checkpoint replaces the comparison on line 347 by an unconditional save (runners/sdalr_runner.py) |
| Seeds | Mechanical-fold gate runs: 0, 1, 2024; ten-split primary comparison: 2024 (the released default, tar_adaptation_RES_PU.py line 398) |
| SHOT (corrected implementation, runners/shot_patch.py v2, C113) | Loss: 0.3 x unsmoothed cross-entropy on centroid pseudo-labels in dataset order + mean entropy - entropy of the mean prediction (information maximisation); no cohesion-repulsion or unreliable-sample term; same backbone, data, schedule, learning rates, batch size, epochs and seed as SDALR |

Released SDALR code behind these settings, quoted verbatim from tar_adaptation_RES_PU.py at commit fb9c379 (https://github.com/BdLab405/SDALR/blob/fb9c379cf72d87234a260521300c3c6aab2254b2/tar_adaptation_RES_PU.py), with line numbers:

| Line | Code | Role |
|---|---|---|
| 42-43 | `NP_fea_bank = torch.cat((fea_bank, torch.ones(fea_bank.size(0), 1)), 1)`; `NP_fea_bank = (NP_fea_bank.t() / torch.norm(NP_fea_bank, p=2, dim=1)).t()` | features get a constant dimension and are L2-normalised (cosine branch, line 40) |
| 62 | `dd = cdist(NP_fea_bank, initc, args.distance)` | distance of every window to every class prototype; with `--distance cosine` (line 408) scipy returns 1 - cosine similarity |
| 69 | `close_samples_indices = np.where(min_distances > args.threshold)[0]` | a window is unreliable when its distance to the nearest prototype exceeds the threshold |
| 442 | `parser.add_argument('--threshold', type=float, default=0.4)` | the threshold is set once and used only on line 69 |
| 398 | `parser.add_argument("--seed", type=int, default=2024, help="random seed")` | released default seed |
| 139 | `acc_init = 0` | best accuracy so far, initialised to 0 |
| 333 | `acc_t_te, acc_matrix, _ = tools.cal_acc(dset_loaders["val"], networks)` | accuracy on the labelled target loader at each evaluation point |
| 347-349 | `if acc_t_te > acc_init:` ... `acc_init = acc_t_te` | the iterate is kept when it beats the best so far |
| 354, 356 | `torch.save(best_net, ...)`; `torch.save(best_netC, ...)` | the kept iterate is saved |
| 358-361 | `if iter_num == max_iter:` ... `networks[-1].load_state_dict(torch.load(f"{args.output_tar_logpt}/source_C.pt"))` | after the last update the saved iterate is reloaded |
| 366 | `acc_t_te, acc_matrix, _ = tools.cal_acc(dset_loaders["test"], networks)` | and its target accuracy is reported |

Why 0.4 is a distance and not the paper's threshold itself: the preprint (arXiv:2503.08749, Eq. 5) assigns a pseudo-label only when the largest cosine similarity to a prototype exceeds the threshold, and fixes that threshold at 0.6 in its experiments; the README's sweep of the threshold from 0.45 to 0.95 refers to the same similarity. Lines 62 and 69 compare a cosine distance, 1 - similarity, with 0.4, which is the same rule as similarity at least 0.6. The local copy used for every run is byte-identical to this file at fb9c379.

The released short-window input and the full-recording kinematic control have different temporal support and aggregation. Their gap difference does not isolate feature representation. The withdrawn first local SHOT patch (v1; C85 and C100) is not a valid second-method replication of these settings.

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

Reaggregation: paper/revision_reporting.py. Derived output: results/reporting_2026_10_09/reporting_corrections.json. Reporting lineage: results/ledger/reporting_2026_10_09.csv. Source SHA-256 checksums are recorded in that JSON. The original experimental release v1.0-submission is archived at https://doi.org/10.5281/zenodo.23105810. Release v1.1, archived at https://doi.org/10.5281/zenodo.23603189, adds this reporting revision and the corrected SHOT run (C113); the revised tables and figures regenerate from v1.1 directly. Release v1.2, archived at https://doi.org/10.5281/zenodo.23799514, adds the post-hoc analyses C114-C116 (scripts and result summaries) and the reporting changes of 30 October 2026; release v1.3, archived at https://doi.org/10.5281/zenodo.23803399, adds the corrections of the external review of 30 October 2026 (PROTOCOL C118); release v1.4, archived at https://doi.org/10.5281/zenodo.23813279, adds the corrections of its reassessment (PROTOCOL C119); release v1.5, archived at https://doi.org/10.5281/zenodo.23105809, adds the reporting corrections of 31 October 2026 (PROTOCOL C120, C121, C123) and the outer-race composition analysis (PROTOCOL C122). Supplementary S4 and the package manifest enumerate sources.


## S6.8 Historical nominal tests (main-text reporting finalized 10 October 2026)

The following unchanged historical family is preserved for audit, not as population-level evidence. Overlapping splits do not establish joint sign symmetry; multiplicity adjustments do not fix that limitation. The SHOT row is the withdrawn first implementation (C100), kept because the family was fixed on 10 October; it is not evidence for SHOT. The corrected SHOT run (C113, S6.1) has an exact one-sided sign-flip p = 0.001 with 10 of 10 splits positive and is not part of this historical family.

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
| SHOT collapse, 10 splits (withdrawn implementation, C100) | 0.000977 | 0.001953 | 0.005721 |

The source-only gap-change analysis reported a two-sided nominal p = 0.18. The historical coverage-gain correlations reported nominal p = 0.0001 (label-free coverage) and p = 0.0009 (partial correlation controlling for headroom). These descriptive associations reuse the same split pool. HUST met the original nominal replication rule and BH adjustment, but not BY; this historical decision is not a population-level replication guarantee.

Historical healthy false-acceptance intervals: envelope threshold 0.0-1.2%, alias-guarded comb 0.0-0.8% (Clopper-Pearson over records, requiring independence); surrogate-null comb 0.8-2.9% and raw-spectrum rule 26.9-60.8% (bootstrap over six bearings). These intervals cannot establish deployment safety.

The 10 October finalization changes presentation, positioning and statistical interpretation only. No new result, model fit or experimental run was added.

## S6.9 Zero-event bounds for healthy false acceptance (added 22 October 2026)

For a gate with no observed false acceptance, the exact one-sided 95 % upper confidence limit on the acceptance rate is 1 - 0.05^(1/n) (Clopper-Pearson with zero events). Per recording, n = 480 gives 0.62 %; per bearing, n = 6 gives 39.3 %. The per-recording limit assumes independent recordings, which repeated recordings of one specimen are not; the per-bearing limit is the one that bears on a new bearing. Both are arithmetic on the counts reported in Table 7 and were not computed by any experiment.

## S6.10 Labels given to seen and unseen bearings (added 24 October 2026)

Share of each bearing's windows that ungated SDALR (final checkpoint, seed 2024) labels healthy, inner race and outer race,
pooled over every task of the ten splits in which the bearing is unseen (bearing-disjoint target) or seen (leaky target)
[src: results/c114/c114_unseen_labels.json; experiments/c114_unseen_labels.py; PROTOCOL C114, post-hoc and descriptive].

| Bearing | True class | Unseen: healthy / inner / outer (%) | Seen: healthy / inner / outer (%) |
|---|---|---|---|
| K001 | healthy | 90.5 / 0.0 / 9.5 | 100.0 / 0.0 / 0.0 |
| K002 | healthy | 82.3 / 11.0 / 6.7 | 100.0 / 0.0 / 0.0 |
| K003 | healthy | 100.0 / 0.0 / 0.0 | 100.0 / 0.0 / 0.0 |
| K004 | healthy | 100.0 / 0.0 / 0.0 | 100.0 / 0.0 / 0.0 |
| K005 | healthy | 94.3 / 0.2 / 5.5 | 100.0 / 0.0 / 0.0 |
| K006 | healthy | 100.0 / 0.0 / 0.0 | 100.0 / 0.0 / 0.0 |
| KA04 | outer | 0.0 / 75.0 / 25.0 | 0.0 / 12.5 / 87.5 |
| KA15 | outer | 0.0 / 70.6 / 29.4 | 0.0 / 31.7 / 68.3 |
| KA16 | outer | 0.0 / 100.0 / 0.0 | 0.0 / 25.2 / 74.8 |
| KA22 | outer | 0.0 / 44.6 / 55.4 | 0.0 / 0.1 / 99.9 |
| KA30 | outer | 3.6 / 96.4 / 0.0 | 3.3 / 2.8 / 93.9 |
| KI04 | inner | 5.8 / 60.8 / 33.3 | 0.1 / 84.1 / 15.8 |
| KI14 | inner | 0.0 / 42.6 / 57.4 | 0.0 / 86.5 / 13.5 |
| KI16 | inner | 0.0 / 41.4 / 58.6 | 0.0 / 95.1 / 4.9 |
| KI17 | inner | 0.0 / 21.2 / 78.8 | 0.0 / 95.5 / 4.5 |
| KI18 | inner | 0.0 / 31.1 / 68.9 | 0.0 / 96.2 / 3.8 |
| KI21 | inner | 0.0 / 74.4 / 25.6 | 0.0 / 100.0 / 0.0 |

Unseen damaged bearings are labelled healthy on at most 5.84 % of their windows (KI04); KA22, the only damaged
IBU/IBB specimen, on 0 %. The unseen-bearing error is a confusion between the two fault families, a median
69 % of an unseen damaged bearing's windows. KI04 and KI14 carry particle-caused indentations on the outer ring
besides inner-ring pitting (S3.1a). With their windows dropped from both targets, the median split gap is
44.6 pp (10 of 10 positive), against 36.2 pp with all bearings; without KI04 alone 39.5 pp, without KI14 alone
36.9 pp.

## S6.11 Order-statistic intervals and leave-one-bearing-out (added 24 October 2026)

A percentile-bootstrap interval of a median over ten splits has no exact coverage guarantee. (An earlier version of this
section said it equals the 3rd and 8th order statistics, with coverage 89.1 %; that is false. For the ten envelope-gate
gains, exact enumeration of all 92,378 resample multisets gives [2.12, 15.66], against [3.15, 9.35] for the 3rd and 8th
values, and 89.1 % is the sign-model coverage of the latter interval; PROTOCOL C118.) The main text therefore reports, for
every split-level median, the narrowest symmetric order-statistic
interval with at least 95 % coverage under the sign model (for ten splits also at least 97.87 % for the median over the
3,999 eligible source sets, sampled without replacement, with equality when no other set's effect equals that median, which is why the main text labels them conditional
97.8 % intervals), computed from the
same saved values; the bootstrap intervals it replaces are listed here. For the 17 within-bearing contrasts and the six
HUST splits the same order statistics are given as descriptive ranges only: these summaries reuse specimens or come from
ten possible splits, so the sign-model coverage (95.1 % and 96.9 %) is not a sampling guarantee for them. The replaced
bootstrap intervals are the original Monte Carlo estimates (20,000 resamples, seed 0, splits in their listed order),
which can differ from the exact bootstrap percentiles: for the envelope-gate gain the retained estimate is [2.48, 15.66]
pp, printed below as 2.5 to 15.7, whereas exact enumeration gives [2.12, 15.66] pp. Both kinds of interval are
conditional on the fixed bearing pool [src: results/c115/c115_intervals.json;
experiments/c115_exact_intervals.py; PROTOCOL C115].

| Effect | n | Median | Order-statistic interval (coverage) | Bootstrap interval replaced (20,000 resamples, seed 0) |
|---|---|---|---|---|
| SDALR loss, ten splits | 10 | 36.2 | 21.6 to 59.4 (97.9 %) | 25.0 to 56.3 |
| Source-only loss | 10 | 35.1 | 21.2 to 55.0 (97.9 %) | 24.4 to 50.6 |
| SHOT loss (corrected) | 10 | 36.6 | 19.7 to 62.0 (97.9 %) | 22.5 to 59.1 |
| Within-bearing difference (17 bearings; descriptive) | 17 | 38.7 | 9.5 to 62.5 (descriptive range) | 9.5 to 62.5 |
| Kinematic forest gap, ordinary | 10 | 8.4 | 2.4 to 30.8 (97.9 %) | 4.8 to 21.0 |
| Kinematic forest gap, balanced | 10 | 10.4 | 5.6 to 26.7 (97.9 %) | 7.2 to 22.7 |
| Envelope-gate gain | 10 | 4.5 | 0.7 to 22.3 (97.9 %) | 2.5 to 15.7 |
| Oracle recoverable share (%) | 10 | 81.8 | 60.0 to 98.2 (97.9 %) | 68.0 to 94.1 |
| Gate closure of the oracle gap (%) | 10 | 19.5 | 1.6 to 41.8 (97.9 %) | 10.4 to 40.9 |
| Forest loss, time statistics | 10 | 22.7 | 15.0 to 35.9 (97.9 %) | 16.4 to 32.4 |
| Forest loss, all features | 10 | 32.1 | 24.1 to 43.9 (97.9 %) | 25.5 to 43.3 |
| Forest minus SDALR, unseen targets | 10 | 8.9 | -0.2 to 16.7 (97.9 %) | 0.4 to 16.1 |
| Same-condition forest loss | 10 | 29.7 | 16.5 to 42.0 (97.9 %) | 18.7 to 40.5 |
| HUST loss, six splits (descriptive) | 6 | 33.5 | 25.8 to 61.1 (descriptive range) | 28.4 to 55.5 |

Leave-one-bearing-out: with the windows of one bearing dropped from both targets of every split, the median SDALR gap
is 36.2 pp with all bearings and ranges from 29.3 pp (without KA30) to 43.5 pp (without KA22); it is positive in at least 9 of 10 splits for every bearing.

| Bearing dropped | Median gap (pp) | Splits positive |
|---|---|---|
| K001 | 36.2 | 10/10 |
| K002 | 36.2 | 10/10 |
| K003 | 36.2 | 10/10 |
| K004 | 36.2 | 10/10 |
| K005 | 36.2 | 10/10 |
| K006 | 36.2 | 10/10 |
| KA04 | 34.5 | 9/10 |
| KA15 | 41.8 | 10/10 |
| KA16 | 37.5 | 10/10 |
| KA22 | 43.5 | 10/10 |
| KA30 | 29.3 | 10/10 |
| KI04 | 39.5 | 10/10 |
| KI14 | 36.9 | 10/10 |
| KI16 | 36.3 | 10/10 |
| KI17 | 33.0 | 10/10 |
| KI18 | 39.4 | 10/10 |
| KI21 | 36.0 | 10/10 |

**Outer-race composition (post-hoc, PROTOCOL C122, added 31 October 2026).** Every clean target holds two outer-race bearings and every leaky target three, because the pool has five real outer-race bearings. Re-scoring the retained ungated SDALR predictions with one of the leaky target's three outer-race bearings dropped, averaged over the three choices, so that both targets are scored on two outer-race bearings, gives a median gap of 36.2 points (range 8.2 to 61.6, positive in 10 of 10 splits) against 36.2 as reported. Weighting every bearing equally instead of every class, which gives the healthy class three eighths of the clean-target weight, gives a median gap of 32.6 points (range 6.4 to 59.2, positive in 10 of 10). The re-scoring uses predictions of models adapted to the three-outer-bearing leaky targets; it does not re-adapt to a two-outer-bearing target, so it does not test whether adaptation itself (prototypes, pseudo-labels) behaves differently with two outer-race bearings [src: results/c122/c122_composition.json; experiments/c122_composition.py; PROTOCOL C122].

## S6.12 HUST splits and fold gate gains (moved from the main text, 30 October 2026)

Accuracy (%) of SDALR on the six pre-specified type-disjoint HUST bearing splits, as the mean over the six condition pairs of each split; the source is the three listed bearing types and the clean target the other two, at the target load. The same leaky and clean values are plotted in Fig. 2b of the main text [src: results/c94; experiments/c94_eval.py; paper/make_tables.py].

| Split | Source bearings | Leaky | Clean | Delta_leak |
|---|---|---|---|---|
| H0 | 6204, 6207, 6208 | 98.1 | 63.7 | 34.5 |
| H1 | 6204, 6205, 6207 | 100.0 | 69.1 | 30.9 |
| H2 | 6204, 6205, 6206 | 99.8 | 49.9 | 49.9 |
| H3 | 6205, 6206, 6207 | 100.0 | 67.5 | 32.5 |
| H4 | 6206, 6207, 6208 | 94.3 | 68.5 | 25.8 |
| H5 | 6205, 6206, 6208 | 100.0 | 38.9 | 61.1 |

Paired effect of each gate inside SDALR on the 12 bearing-disjoint tasks of the two mechanical folds, gated minus ungated accuracy in percentage points, at one seed per row; both arms of every comparison ran in one job from the same source checkpoint, and the 12 tasks share two source folds, so these summaries are descriptive. The per-task values of the two envelope-based gates are plotted in Fig. 6 of the main text [src: results/PAIRED_GATING.md; experiments/paired_gating.py; paper/make_tables.py].

| Gate | Seed | Mean | Median | Min | Max | Tasks > 0 |
|---|---|---|---|---|---|---|
| Shaft-alias-guarded comb | 0 | +3.79 | +3.33 | -0.08 | +11.01 | 7/12 |
| Shaft-alias-guarded comb | 1 | +4.56 | +3.28 | -0.08 | +15.45 | 8/12 |
| Shaft-alias-guarded comb | 2024 | +3.73 | +3.67 | -0.05 | +8.07 | 8/12 |
| Envelope threshold rule | 0 | +7.44 | +7.57 | -0.01 | +18.02 | 9/12 |
| Envelope threshold rule | 1 | +7.99 | +6.65 | -0.70 | +19.44 | 10/12 |
| Envelope threshold rule | 2024 | +5.70 | +5.59 | -0.05 | +14.52 | 10/12 |
| Raw-spectrum band rule | 2024 | -3.93 | -4.03 | -20.01 | +6.63 | 6/12 |
