# Supplementary S7 - REFORMS reporting checklist and leakage statement

Date: 22 October 2026. This supplement maps the 32 items of the REFORMS checklist for machine-learning-based science (Kapoor et al., Science Advances 10(18), eadk3452, 2024, doi:10.1126/sciadv.adk3452) to the places in the manuscript, the supplements and the repository where each is addressed, and states the three leakage arguments of Kapoor and Narayanan (Patterns 4(9), 100804, 2023). "Main" refers to a manuscript section, "S" to a supplement and "repo" to the experimental release named under Data availability.

## S7.1 REFORMS items

| Item | Content | Where |
|---|---|---|
| 1a | Population or distribution about which the scientific claim is made | Main 1 and 4.1: unseen physical bearings of the same rig at a shifted operating condition; 4.5: inference conditional on the 17-bearing Paderborn pool |
| 1b | Motivation for choosing this population or distribution | Main 1: a replaced or previously unseen bearing is the deployment case of interest; Main 3: Paderborn is the public set with several bearings per class and several conditions per bearing |
| 1c | Motivation for the use of ML methods | Main 1: the claims under evaluation are published ML (source-free adaptation) results; no new ML method is proposed |
| 2a | Dataset: source, version, access | Main 3 and Table 2; Data availability (Paderborn, HUST, CWRU, UORED-VAFCLS, JNU); S3 per-bearing geometry and checksums |
| 2b | Code: exact version | Data availability: GitHub repository and Zenodo version DOI; S4 commit per artifact; S6.2 upstream SDALR revision fb9c379 (fetched by script, not redistributed) |
| 2c | Computing infrastructure | Main 4.6 and S6: Kaggle Tesla T4 kernels for adaptation, Kaggle CPU kernels and local CPU for analysis; kernel identifiers in the ledger (S4) |
| 2d | Documentation for reproduction | repo README and PROTOCOL.md; S4 traceability |
| 2e | Reproduction script | repo: experiments/*.py regenerate every result file; paper/make_tables.py regenerates every table; paper/check_manuscript.py verifies the headline numbers |
| 3a | Data sources | Main 3, Table 2 |
| 3b | Sampling frame | Main 3.1: all 6 healthy, 5 real outer-race and 6 real inner-race Paderborn bearings; HUST types 6204-6208; Main 4.2: splits drawn uniformly from the 4,000 possible 3/3/3 source sets |
| 3c | Why the dataset is useful for the task | Main 3: several physical bearings per class and several conditions per bearing, as the paired design requires |
| 3d | Outcome variable and descriptive statistics | Main 3: label space {normal, inner race, outer race}; Main 4.1: 2,000 windows per class, so window accuracy equals balanced accuracy |
| 3e | Sample size and outcome frequencies | Main 4.1 (windows per class and per recording), Table 2 (recordings), Table 7 (480 healthy recordings, 1,839 single-fault recordings) |
| 3f | Missing data | None: every recording used is complete; excluded bearings are listed under 4a |
| 3g | Evaluation set representative of the population of interest | Main 4.5 and 9: the pool is fixed; the ten-split summaries describe sensitivity to the source draw, not a population of new bearings |
| 4a | Excluded data and rationale | Main 3: artificial-damage bearings and KB24/KB27 excluded from adaptation (no rolling-element class can be formed); HUST ball recordings excluded for label-space comparability; the N09 condition enters only the gate analyses |
| 4b | Impossible or corrupt samples | Main 3.1: no gate is computed for a bearing whose geometry its own rig does not publish (HUST); S5: slips outside the search window are reported |
| 4c | Transformations from raw data | Main 4.1 (2,048-sample windows, evenly spaced, no boundary crossing, z-score per loader, S6.2); Main 5 (gate preprocessing); S2 |
| 5a | Model description | S6.2 (SDALR backbone, head, optimiser, schedule); Main 4.3 (SHOT objective); Main 6.3 and PROTOCOL C91/C112 (forests) |
| 5b | Justification for model types | Main 4.3: SDALR has a Paderborn benchmark and released code; SHOT is SDALR's ablated base and the generic comparator in this literature; forests are the non-adaptive control |
| 5c | Evaluation method and splits | Main 4.1-4.2 and Table 3: paired leaky/clean targets, two mechanical folds, ten pre-specified random splits, six HUST splits |
| 5d | Model selection | Main 4.3: final checkpoint, no target labels; the released target-label rule reported once as a diagnostic |
| 5e | Hyper-parameter tuning | Main 4.3 and S6.2: released SDALR values unchanged; no tuning on any target; forest and gate settings fixed in the protocol before the runs |
| 5f | Appropriate baselines | Main 6.3 and Table 6: source-only arm, random forests on three feature sets, same-condition control, kinematic-feature forest |
| 6a | Train-test separation | Main 4.1-4.2: bearing-disjoint clean targets; repo tests/test_splits.py fails when a bearing crosses a split; the leaky arm is the deliberate control |
| 6b | Dependencies between training and test data | Main 4.2 and 4.5: the leaky target reuses the source bearings by design; clean targets share no bearing with the source; splits share bearings with one another and the inference is conditional on the pool |
| 6c | Feature legitimacy | Main 5 and 6.6: gate verdicts use the measured shaft speed and per-bearing geometry only, never labels; the as_released checkpoint rule that consults target labels is excluded from every headline number |
| 7a | Metrics | Main 4.1 (window accuracy equals balanced accuracy under class balance), 6.3 and Table 6 (balanced accuracy where classes are unbalanced), Table 7 (false acceptance and correct verdicts) |
| 7b | Uncertainty estimates | Main 4.5: medians with order-statistic intervals over splits (C115; the percentile bootstrap intervals they replace are in S6.11); S6.9 zero-event bounds; S6 bearing-bootstrap and record-binomial intervals |
| 7c | Statistical tests and assumption checks | Main 4.5 and S6: exact one-sided sign-flip tests with BH and BY adjustment; sign symmetry holds only conditionally because splits share bearings |
| 8a | External validity | Main 6.3 (HUST replication, with bearing size changing together with specimen); 6.6 (off-rig gate calibration on UORED and CWRU) |
| 8b | Contexts where results are not expected to hold | Main 9: no cross-machine claim; one rig carries the full analysis; small-damage specimens are not certified by the gates; six healthy bearings |

## S7.2 Leakage statement (Kapoor and Narayanan, 2023)

1. Clean separation. In every clean target no physical bearing appears in both the source and the target; the split definitions are in Table 3 and are checked by a unit test that fails when a bearing crosses the split. The leaky target places the same bearings on both sides on purpose, as the control.
2. Feature legitimacy. The adaptation networks see 2,048-sample vibration windows and no metadata. The gates see the measured shaft speed and the bearing's own geometry; neither is a label. The checkpoint rule of the released SDALR code consults target labels and is therefore reported only as a diagnostic.
3. Test distribution. The clean targets are unseen bearings of the same rig at a shifted operating condition. This matches the claim made (unseen-bearing accuracy within a rig) and not a cross-machine claim, which the manuscript does not make.
