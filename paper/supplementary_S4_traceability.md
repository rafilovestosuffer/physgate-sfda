# Supplementary S4 — traceability of every reported number

Each row is a result file cited by the manuscript, what it establishes, the Kaggle account that produced the runs behind it, and the SHA-256 (first 16 hex digits) of the file as submitted. The experiment ledger (`results/ledger/*.csv`, 1248 rows) lists every individual run with its kernel URL, git commit and retained artifact path; the artifacts themselves accompany this submission.

| result file | establishes | runs | sha256 |
|---|---|---|---|
| `results/M0_PU_RESULT.md` | Reproduction of the published method on its own tasks (Section 6.1) | 24 ledger rows (rafiurrahman01) | `fc46cc5069873403` |
| `results/M1_RESULT.md` | Collapse on the two mechanical folds (Section 6.2) | 48 ledger rows (rafiurrahman01) | `51c898427e02bc23` |
| `results/c88/C88_RESULT.md` | Ten pre-registered random bearing splits: collapse, gating, decomposition | 240 ledger rows (rafiurrahman01, rhrhrhrhrh) | `31a3848e1920a72b` |
| `results/c94/C94_RESULT.md` | Second rig (HUST): six type-disjoint splits | 72 ledger rows (rhrhrhrhrh) | `354e1933d0e07a7f` |
| `results/C85_RESULT.md` | SHOT under the same paired design, two folds | 24 ledger rows (rhrhrhrhrh) | `f90484797bc2e972` |
| `results/c100/C100_RESULT.md` | SHOT on the ten pre-registered splits (Section 6.3) | 120 ledger rows (rafiurrahman01, rhrhrhrhrh) | `9bcf9e99e96d0daa` |
| `results/c101/C101_RESULT.md` | Random forests on the ten splits, both arms (Section 6.3) | 240 ledger rows (rafiurrahman01, rhrhrhrhrh) | `7e2f300835822250` |
| `results/c96/C96_RESULT.md` | Cluster-level inference and the Benjamini--Hochberg family (Section 4, S1) | deterministic analysis of retained data or artifacts; script in experiments/ | `f5255985d62170ba` |
| `results/c97/C97_RESULT.md` | Identity probe on ten handcrafted time statistics (Section 6.7) | deterministic analysis of retained data or artifacts; script in experiments/ | `4a1b8a3bd809556f` |
| `results/c98/C98_RESULT.md` | In-loop gate coverage and the coverage-gain correlation (Section 6.6) | deterministic analysis of retained data or artifacts; script in experiments/ | `703e45e5d6df70d3` |
| `results/c99/C99_RESULT.md` | Off-rig calibration of the envelope-rule operating point (Section 6.6) | deterministic analysis of retained data or artifacts; script in experiments/ | `ab352d55664b30ae` |
| `results/c102/C102_RESULT.md` | A/A floor: repeated executions of one configuration (Section 4) | 54 ledger rows (rafiurrahman01) | `99ff25ec75b3f0f8` |
| `results/c103/C103_RESULT.md` | Cross-job gap: pretraining-state test and code diagnosis (Section 4) | 12 ledger rows (rafiurrahman01) | `c71812aaadf26ee3` |
| `results/c104/C104_RESULT.md` | Same-condition, bearing-disjoint control (Section 6.3) | deterministic analysis of retained data or artifacts; script in experiments/ | `12553a9433bc2628` |
| `results/c91/C91_RESULT.md` | Non-adaptive random-forest baselines on the two folds | 96 ledger rows (rafiurrahman01) | `992f0750b825c38d` |
| `results/C83_RESULT.md` | Gating inside adaptation across three seeds | 198 ledger rows (rafiurrahman01, rhrhrhrhrh) | `efb31e44a2a92f75` |
| `results/PAIRED_GATING.md` | Pairing proof and the collapse decomposition | 198 ledger rows (rafiurrahman01, rhrhrhrhrh) | `0a80efe5348680c4` |
| `results/c87/N1_RESULT.md` | Within-class bearing-identity probe | kernel artifact retained; probe outputs, not per-task accuracy rows | `504e0d8e374623e4` |
| `results/roc/ROC_RESULT.md` | Gate operating curves on Paderborn | deterministic analysis of retained data or artifacts; script in experiments/ | `97d0a59ecd22445e` |
| `results/h7/H7_RESULT.md` | Gate false acceptance at the pre-registered operating points | deterministic analysis of retained data or artifacts; script in experiments/ | `4831ae489e77cfc5` |
| `results/comb_v2/COMB_V2_RESULT.md` | Shaft-alias-guarded comb beside the frozen comb test | deterministic analysis of retained data or artifacts; script in experiments/ | `c8f3b2e0baf42669` |
| `results/c90/C90_RESULT.md` | Measured cage slip and the shaft-order lock | deterministic analysis of retained data or artifacts; script in experiments/ | `12bd22125e105b1c` |
| `results/b6a/B6A_RESULT.md` | CWRU cross-end contamination (Supplementary S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `e5dd75b25fb743ff` |
| `results/c78/C78_RESULT.md` | Within-CWRU fan-end/drive-end control, null (Supplementary S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `b1c9e4af1f277555` |
| `results/b7_uored/B7_UORED_RESULT.md` | UORED gate behaviour and logged-speed problem (Supplementary S2, S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `c1e708b045977a7c` |

## Figure data

The exact values plotted in each figure are provided as CSV so that any figure can be recomputed or re-plotted independently.

| figure | data file | rows | sha256 |
|---|---|---|---|
| fig2 collapse | `paper/figures/data/fig2_collapse.csv` | 18 | `e0718e337901206c` |
| fig3 bearings | `paper/figures/data/fig3_bearings.csv` | 25 | `e71b51b600d99f0d` |
| fig3 purity | `paper/figures/data/fig3_purity.csv` | 18 | `b0ca869e04bef308` |
| fig4 decomposition | `paper/figures/data/fig4_decomposition.csv` | 10 | `160881e818b2aaa1` |
| fig5 roc | `paper/figures/data/fig5_roc.csv` | 43 | `e187c1883fd137d7` |
| fig6 gains | `paper/figures/data/fig6_gains.csv` | 72 | `4a4118b87a2e9188` |
| fig7 slip | `paper/figures/data/fig7_slip.csv` | 304 | `33d93f5895c00468` |

## Analysis, evaluation, figure and kernel scripts

Every script that computes a reported number, builds a table or figure, or ran on Kaggle, with the SHA-256 (first 16 hex digits) of the file as submitted.

| script | sha256 |
|---|---|
| `experiments/append_ledger.py` | `9ecfefe061f9d8da` |
| `experiments/append_ledger_rf.py` | `404370540ae1b64d` |
| `experiments/b6a_cross_end.py` | `5255ce88829a4736` |
| `experiments/b7_uored.py` | `800ae9a2c818ccaf` |
| `experiments/b7_uored_ftf.py` | `590fe5acc740eb1a` |
| `experiments/c100_shot_splits.py` | `fabd5d775b48368a` |
| `experiments/c101_rf_splits.py` | `e9a21001113c7914` |
| `experiments/c102_aa_floor.py` | `c9ae7d874c56bf10` |
| `experiments/c104_same_condition.py` | `58cb7b6d6fede41e` |
| `experiments/c104b_per_class.py` | `8fdfd15384bf70ba` |
| `experiments/c105_source_only.py` | `ce7f4f5bc9cebce2` |
| `experiments/c106_within_bearing.py` | `be2141fd6fb1140b` |
| `experiments/c107_gate_spillover.py` | `8f63cf0c0f9ea999` |
| `experiments/c108_purity.py` | `da7f8bdc43809f0d` |
| `experiments/c109_intervals.py` | `b07de55dbc5e26bd` |
| `experiments/c111_probe_ablations.py` | `2ce2db872e2f683c` |
| `experiments/c112_kinematic_rf.py` | `7966e786bb7dd9e9` |
| `experiments/c77_ball_sidebands.py` | `c3bc867c93d888c8` |
| `experiments/c78_fe_de_control.py` | `d72453819d41b136` |
| `experiments/c79_iesfo_eval.py` | `d141cd4bf3f6a78c` |
| `experiments/c87_eval.py` | `3d163ebe4bc40f6c` |
| `experiments/c88_eval.py` | `3b79f8be9f3a8dc2` |
| `experiments/c90_slip.py` | `d4402279fc8de7a6` |
| `experiments/c90_synthetic.py` | `8ddede18642e8170` |
| `experiments/c94_eval.py` | `f12e53f285d1bca0` |
| `experiments/c95_gate_population.py` | `2f58303c83e02330` |
| `experiments/c96_clustered_stats.py` | `c1fd5f51ed37576c` |
| `experiments/c97_probe_baseline.py` | `6159cc589f4f8e8e` |
| `experiments/c98_inloop_coverage.py` | `35ef8842ad55869c` |
| `experiments/c99_crossrig_calibration.py` | `7b4db92bca319748` |
| `experiments/comb_v2_eval.py` | `698135b8231b8f90` |
| `experiments/final_decisions.py` | `92e27b4bbac7e041` |
| `experiments/gate_roc.py` | `b5864226d363064e` |
| `experiments/h6_cluster_bootstrap.py` | `334b23c034d07005` |
| `experiments/h6_prewhitening.py` | `73a91a6ffe195b73` |
| `experiments/h7_rules.py` | `45b510d1e8929b45` |
| `experiments/ladder_input_dims.py` | `f88d50bdb031efa2` |
| `experiments/m4_stratification.py` | `5cc296f5122b3e54` |
| `experiments/null_calibration_drs.py` | `393a69c45732234e` |
| `experiments/paired_gating.py` | `b488ee4559eec52c` |
| `experiments/rev6_load.py` | `539b8e59671823ca` |
| `experiments/window_contract.py` | `a4b73e6696d84ac0` |
| `kaggle/kernels/_make_k10.py` | `9bd6e334266fe744` |
| `kaggle/kernels/_make_shot_k10.py` | `1e8ddb49fae9d037` |
| `kaggle/kernels/bistw_FA.py` | `9fa807a596dd5565` |
| `kaggle/kernels/bistw_FB.py` | `58e3d7120b8b15bb` |
| `kaggle/kernels/build_pdf.py` | `84c3bce294bd51e3` |
| `kaggle/kernels/c103_pretrain_state.py` | `ec5f871615c6cff1` |
| `kaggle/kernels/c110_diversity_cpu.py` | `18745718926b6cf6` |
| `kaggle/kernels/c86_bist.py` | `6453ae22fdd3a9a0` |
| `kaggle/kernels/c86_bist_FA.py` | `6453ae22fdd3a9a0` |
| `kaggle/kernels/c86_bist_FB.py` | `ccfc1cf0d2f236ad` |
| `kaggle/kernels/c91_shallow_cpu.py` | `3c222bdfd256977c` |
| `kaggle/kernels/c92_rf_splits_cpu.py` | `46af5eff45795a2a` |
| `kaggle/kernels/hust_k6.py` | `faca3fd4f577698a` |
| `kaggle/kernels/k10_g1.py` | `093da1745350296d` |
| `kaggle/kernels/k10_g2.py` | `46258ab7a040096e` |
| `kaggle/kernels/k10_g3.py` | `2ecd4e76a4656d03` |
| `kaggle/kernels/k10_g4.py` | `5b54984ab083fe90` |
| `kaggle/kernels/m0_pu_diag.py` | `92b6b49f4d7cafe1` |
| `kaggle/kernels/m0_sdalr.py` | `487b43092fece2bc` |
| `kaggle/kernels/m0_sdalr_pu.py` | `c17f956ef755374f` |
| `kaggle/kernels/m1_sdalr.py` | `dfc97f4ea3fea9a0` |
| `kaggle/kernels/m1_sdalr_FA.py` | `dfc97f4ea3fea9a0` |
| `kaggle/kernels/m1_sdalr_FB.py` | `c2ea37f58d43481f` |
| `kaggle/kernels/m2_gate.py` | `ad10792ccb6084c9` |
| `kaggle/kernels/m2_gate_FA.py` | `718c2931ba8e74cc` |
| `kaggle/kernels/m2_gate_FB.py` | `9b1cf2bbf4fb3d7d` |
| `kaggle/kernels/m2_repeat.py` | `ba4798b78657ed26` |
| `kaggle/kernels/m2rep_FA_r1.py` | `ba4798b78657ed26` |
| `kaggle/kernels/m2rep_FA_r2.py` | `ab7b5141c265a62a` |
| `kaggle/kernels/m2rep_FB_r1.py` | `a0e65e3c4c1b09e4` |
| `kaggle/kernels/m2rep_FB_r2.py` | `32e9822c798a7ec2` |
| `kaggle/kernels/m2seed_FA_s0.py` | `053f7caae6a344cc` |
| `kaggle/kernels/m2seed_FA_s1.py` | `9e8b70c67f81fe8b` |
| `kaggle/kernels/m2seed_FB_s0.py` | `54f2dac26168c96e` |
| `kaggle/kernels/m2seed_FB_s1.py` | `348abc169e9b0c53` |
| `kaggle/kernels/n1_probe.py` | `c290e3bb4ba42e8f` |
| `kaggle/kernels/shot_FA.py` | `1f6796b36929c56d` |
| `kaggle/kernels/shot_FB.py` | `32410f94ff3fe736` |
| `kaggle/kernels/shot_k10_g1.py` | `b4b37194c83f5114` |
| `kaggle/kernels/shot_k10_g2.py` | `aa90d9ab41db6a85` |
| `kaggle/kernels/shot_k10_g3.py` | `7987e12c8456bcb9` |
| `kaggle/kernels/shot_k10_g4.py` | `aba9d796ad465ac7` |
| `paper/check_manuscript.py` | `65bfe2e38566da19` |
| `paper/figures/build_figures.py` | `08ae7350014e0119` |
| `paper/figures/build_schematics.py` | `85add8952be90e3f` |
| `paper/figures/fig_6203_lock.py` | `391c66d5cfc50244` |
| `paper/figures/fig_m1_leakage.py` | `64aeab3af6cee0b9` |
| `paper/figures/fig_splits.py` | `895c752b05fd7d6a` |
| `paper/figures/qa_layout.py` | `a1368d014982ba1f` |
| `paper/figures/style.py` | `1fb214879875a584` |
| `paper/figures/validate_figures.py` | `c583c898cbc5f17f` |
| `paper/make_s1.py` | `54b25aecd36052cf` |
| `paper/make_s3_table.py` | `f2553d13064ce12f` |
| `paper/make_s4.py` | `8631a7512d45685d` |
| `paper/make_submission.py` | `e7d7dd997444d880` |
| `paper/make_tables.py` | `58dc8f12cf9933c2` |
| `runners/bist.py` | `7a0608d3ad353c8a` |
| `runners/sdalr_runner.py` | `7da58ad865c2b0eb` |
| `runners/shot_patch.py` | `166bc6bf5aa5b465` |

## Regenerating everything

```
python experiments/c88_eval.py        # ten-split decisions
python experiments/c94_eval.py        # second-rig replication
python experiments/c100_shot_splits.py # SHOT on the ten splits
python experiments/c101_rf_splits.py  # random forests on the ten splits
python experiments/append_ledger.py; python experiments/append_ledger_rf.py  # ledger (idempotent)
python experiments/c102_aa_floor.py   # A/A floor
python experiments/c96_clustered_stats.py # cluster-level tests and BH family
python paper/make_s1.py               # S1, including the BH family by stage
python experiments/final_decisions.py # seed robustness and SHOT
python experiments/paired_gating.py   # pairing proof and decomposition
python paper/make_tables.py           # all LaTeX tables
python paper/figures/build_figures.py && python paper/figures/build_schematics.py
python paper/figures/validate_figures.py && python paper/figures/qa_layout.py
```

