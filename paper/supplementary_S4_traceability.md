# Supplementary S4 — traceability of every reported number

Each row is a result file cited by the manuscript, what it establishes, the Kaggle account that produced the runs behind it, and the SHA-256 (first 16 hex digits) of the file as submitted. The experiment ledger (`results/ledger/*.csv`, 1259 rows) lists every individual run with its kernel URL, git commit and retained artifact path. Original run artifacts are in the public v1.0-submission archive; reporting-only corrections accompany this submission. Reporting ledger rows are labelled separately and are not new experimental runs.

All SHA-256 values in this supplement are computed on file content with line endings normalised to LF, so they verify identically on any operating system (strip carriage returns before hashing).

| result file | establishes | runs | sha256 |
|---|---|---|---|
| `results/c108/c108_purity.json` | Descriptive window-label purity by specimen | deterministic analysis of retained data or artifacts; script in experiments/ | `d41f83826296fe9e` |
| `results/c111/c111_probe_ablations.json` | Identity probe ablations on retained representations | deterministic analysis of retained data or artifacts; script in experiments/ | `4c39dfae22b1d4c3` |
| `results/c104/C104B_RESULT.md` | Post-hoc class-specific same-condition analysis | deterministic analysis of retained data or artifacts; script in experiments/ | `d3229ef37cc7c36f` |
| `results/c105/c105_source_only.json` | Source-only and post-adaptation contrasts | deterministic analysis of retained data or artifacts; script in experiments/ | `49b0d0a8f1091755` |
| `results/c106/c106_within_bearing.json` | Within-bearing descriptive contrasts | deterministic analysis of retained data or artifacts; script in experiments/ | `8ce0f9dc5b4428f4` |
| `results/c107/c107_gate_spillover.json` | Gate gain accounting | deterministic analysis of retained data or artifacts; script in experiments/ | `707e195b00e2a0f0` |
| `results/c109/c109_intervals.json` | Conditional intervals and healthy false acceptance | deterministic analysis of retained data or artifacts; script in experiments/ | `8160f1db260a9d32` |
| `results/c110/c110_result.json` | Source expansion: diversity and volume change together | deterministic analysis of retained data or artifacts; script in experiments/ | `a9eecff7e2ad4970` |
| `results/c112/c112_result.json` | Original ordinary and saved balanced kinematic outcomes | deterministic analysis of retained data or artifacts; script in experiments/ | `9a6e4dc189507544` |
| `results/reporting_2026_10_09/reporting_corrections.json` | Reporting-only corrections and saved-score sensitivity (S6) | deterministic analysis of retained data or artifacts; script in experiments/ | `2aa642ad46dea497` |
| `results/M0_PU_RESULT.md` | Reproduction of the published method on its own tasks (Section 6.1) | 24 ledger rows (rafiurrahman01) | `d7b14b5c3fb754d2` |
| `results/M1_RESULT.md` | Collapse on the two mechanical folds (Section 6.2) | 48 ledger rows (rafiurrahman01) | `51c898427e02bc23` |
| `results/c88/C88_RESULT.md` | Ten pre-specified random bearing splits: collapse, gating, decomposition | 240 ledger rows (rafiurrahman01, rhrhrhrhrh) | `5adae7364e14bf91` |
| `results/c94/C94_RESULT.md` | Second rig (HUST): six type-disjoint splits | 72 ledger rows (rhrhrhrhrh) | `8b783e08ff147cd5` |
| `results/C85_RESULT.md` | WITHDRAWN: local SHOT outputs, two folds; indexing defect (S6) | 24 ledger rows (rhrhrhrhrh) | `876937dafaf42695` |
| `results/c100/C100_RESULT.md` | WITHDRAWN: local SHOT outputs, ten splits; indexing defect (S6) | 120 ledger rows (rafiurrahman01, rhrhrhrhrh) | `af67a98725aaba6a` |
| `results/c101/C101_RESULT.md` | Random forests on the ten splits, both arms (Section 6.3) | 240 ledger rows (rafiurrahman01, rhrhrhrhrh) | `4eaa10070031bb7f` |
| `results/c96/C96_RESULT.md` | Cluster-level inference and the Benjamini--Hochberg family (Section 4, S1) | deterministic analysis of retained data or artifacts; script in experiments/ | `038147f032201169` |
| `results/c97/C97_RESULT.md` | Identity probe on ten handcrafted time statistics (Section 6.4) | deterministic analysis of retained data or artifacts; script in experiments/ | `41a4e6cb63f2cf04` |
| `results/c98/C98_RESULT.md` | In-loop gate coverage and the coverage-gain correlation (Section 6.6) | deterministic analysis of retained data or artifacts; script in experiments/ | `ec919225fcbcae9b` |
| `results/c99/C99_RESULT.md` | Off-rig calibration of the envelope-rule operating point (Section 6.6) | deterministic analysis of retained data or artifacts; script in experiments/ | `ee65f7201e38d584` |
| `results/c102/C102_RESULT.md` | A/A floor: repeated executions of one configuration (Section 4) | 54 ledger rows (rafiurrahman01) | `233854d98d7336fa` |
| `results/c103/C103_RESULT.md` | Cross-job gap: pretraining-state test and code diagnosis (Section 4) | 12 ledger rows (rafiurrahman01) | `c71812aaadf26ee3` |
| `results/c104/C104_RESULT.md` | Same-condition, bearing-disjoint control (Section 6.3) | deterministic analysis of retained data or artifacts; script in experiments/ | `fad3938a1c9285a0` |
| `results/c91/C91_RESULT.md` | Non-adaptive random-forest baselines on the two folds | 96 ledger rows (rafiurrahman01) | `992f0750b825c38d` |
| `results/C83_RESULT.md` | Gating inside adaptation across three seeds | 198 ledger rows (rafiurrahman01, rhrhrhrhrh) | `43122531adb92c56` |
| `results/PAIRED_GATING.md` | Pairing configuration and the collapse decomposition | 198 ledger rows (rafiurrahman01, rhrhrhrhrh) | `3afb7ef3b31c6d5f` |
| `results/c87/N1_RESULT.md` | Within-class bearing-identity probe | kernel artifact retained; probe outputs, not per-task accuracy rows | `504e0d8e374623e4` |
| `results/roc/ROC_RESULT.md` | Gate operating curves on Paderborn | deterministic analysis of retained data or artifacts; script in experiments/ | `a63cd5e875efb765` |
| `results/h7/H7_RESULT.md` | Gate false acceptance at the pre-specified operating points | deterministic analysis of retained data or artifacts; script in experiments/ | `4831ae489e77cfc5` |
| `results/comb_v2/COMB_V2_RESULT.md` | Shaft-alias-guarded comb beside the frozen comb test | deterministic analysis of retained data or artifacts; script in experiments/ | `c8f3b2e0baf42669` |
| `results/c90/C90_RESULT.md` | Measured cage slip and the shaft-order lock | deterministic analysis of retained data or artifacts; script in experiments/ | `12bd22125e105b1c` |
| `results/b6a/B6A_RESULT.md` | CWRU cross-end contamination (Supplementary S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `e5dd75b25fb743ff` |
| `results/c78/C78_RESULT.md` | Within-CWRU fan-end/drive-end control, null (Supplementary S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `b1c9e4af1f277555` |
| `results/b7_uored/B7_UORED_RESULT.md` | UORED gate behaviour and logged-speed problem (Supplementary S2, S3) | deterministic analysis of retained data or artifacts; script in experiments/ | `c1e708b045977a7c` |

## Figure data

The exact values plotted in each figure are provided as CSV so that any figure can be recomputed or re-plotted independently.

| figure | data file | rows | sha256 |
|---|---|---|---|
| fig1 design | `paper/figures/data/fig1_design.csv` | 5 | `5ac0670db979239e` |
| fig2 collapse | `paper/figures/data/fig2_collapse.csv` | 18 | `b58b11870aa8e5df` |
| fig3 bearings | `paper/figures/data/fig3_bearings.csv` | 25 | `ad3bd2ecc8eb941a` |
| fig3 purity | `paper/figures/data/fig3_purity.csv` | 18 | `c33c4b419bfddeec` |
| fig4 decomposition | `paper/figures/data/fig4_decomposition.csv` | 10 | `4a2862eebfd56c73` |
| fig5 roc | `paper/figures/data/fig5_roc.csv` | 43 | `4ef7464fb495f361` |
| fig6 gains | `paper/figures/data/fig6_gains.csv` | 72 | `2ebbf5d4c99499da` |
| fig7 slip | `paper/figures/data/fig7_slip.csv` | 304 | `7d5d84e6dfbbe2af` |

## Analysis, evaluation, figure and kernel scripts

Every script that computes a reported number, builds a table or figure, or ran on Kaggle, with the SHA-256 (first 16 hex digits) of the file as submitted.

| script | sha256 |
|---|---|
| `experiments/append_ledger.py` | `bb4644d0a351b391` |
| `experiments/append_ledger_rf.py` | `404370540ae1b64d` |
| `experiments/b6a_cross_end.py` | `5255ce88829a4736` |
| `experiments/b7_uored.py` | `800ae9a2c818ccaf` |
| `experiments/b7_uored_ftf.py` | `590fe5acc740eb1a` |
| `experiments/c100_shot_splits.py` | `fabd5d775b48368a` |
| `experiments/c101_rf_splits.py` | `ee809bf119282e9b` |
| `experiments/c102_aa_floor.py` | `e3ba22f66a35f9ab` |
| `experiments/c104_same_condition.py` | `58cb7b6d6fede41e` |
| `experiments/c104b_per_class.py` | `8fdfd15384bf70ba` |
| `experiments/c105_source_only.py` | `df26d1ff4fdb5c31` |
| `experiments/c106_within_bearing.py` | `be2141fd6fb1140b` |
| `experiments/c107_gate_spillover.py` | `8f63cf0c0f9ea999` |
| `experiments/c108_purity.py` | `da7f8bdc43809f0d` |
| `experiments/c109_intervals.py` | `1fd51679cd4867c7` |
| `experiments/c111_probe_ablations.py` | `2ce2db872e2f683c` |
| `experiments/c112_kinematic_rf.py` | `7966e786bb7dd9e9` |
| `experiments/c113_shot_splits.py` | `dfb210b8e0a55dcc` |
| `experiments/c77_ball_sidebands.py` | `c3bc867c93d888c8` |
| `experiments/c78_fe_de_control.py` | `d72453819d41b136` |
| `experiments/c79_iesfo_eval.py` | `d141cd4bf3f6a78c` |
| `experiments/c87_eval.py` | `3d163ebe4bc40f6c` |
| `experiments/c88_eval.py` | `58ea0258800f1ceb` |
| `experiments/c90_slip.py` | `54b86a44359de2d4` |
| `experiments/c90_synthetic.py` | `8ddede18642e8170` |
| `experiments/c94_eval.py` | `f12e53f285d1bca0` |
| `experiments/c95_gate_population.py` | `2f58303c83e02330` |
| `experiments/c96_clustered_stats.py` | `fba48d6db4b63155` |
| `experiments/c97_probe_baseline.py` | `6159cc589f4f8e8e` |
| `experiments/c98_inloop_coverage.py` | `6c6439bd99185969` |
| `experiments/c99_crossrig_calibration.py` | `7b4db92bca319748` |
| `experiments/comb_v2_eval.py` | `698135b8231b8f90` |
| `experiments/final_decisions.py` | `92e27b4bbac7e041` |
| `experiments/gate_roc.py` | `b5864226d363064e` |
| `experiments/h6_cluster_bootstrap.py` | `334b23c034d07005` |
| `experiments/h6_prewhitening.py` | `73a91a6ffe195b73` |
| `experiments/h7_rules.py` | `45b510d1e8929b45` |
| `experiments/ladder_input_dims.py` | `f88d50bdb031efa2` |
| `experiments/m4_stratification.py` | `e21f97d6cf81b177` |
| `experiments/null_calibration_drs.py` | `4d14cfe98bcdee6c` |
| `experiments/paired_gating.py` | `2a29bef79c842852` |
| `experiments/rev6_load.py` | `fc9f6fa8b723d4b0` |
| `experiments/window_contract.py` | `a4b73e6696d84ac0` |
| `kaggle/kernels/_make_k10.py` | `9bd6e334266fe744` |
| `kaggle/kernels/_make_shot_k10.py` | `8780bdb25eabcbd0` |
| `kaggle/kernels/bistw_FA.py` | `9fa807a596dd5565` |
| `kaggle/kernels/bistw_FB.py` | `58e3d7120b8b15bb` |
| `kaggle/kernels/build_pdf.py` | `84c3bce294bd51e3` |
| `kaggle/kernels/c103_pretrain_state.py` | `ec5f871615c6cff1` |
| `kaggle/kernels/c110_diversity_cpu.py` | `18745718926b6cf6` |
| `kaggle/kernels/c86_bist.py` | `6453ae22fdd3a9a0` |
| `kaggle/kernels/c86_bist_FA.py` | `6453ae22fdd3a9a0` |
| `kaggle/kernels/c86_bist_FB.py` | `ccfc1cf0d2f236ad` |
| `kaggle/kernels/c91_shallow_cpu.py` | `3c222bdfd256977c` |
| `kaggle/kernels/c92_rf_splits_cpu.py` | `6e8307d39b9abc9c` |
| `kaggle/kernels/hust_k6.py` | `6538d6809a4b1509` |
| `kaggle/kernels/k10_g1.py` | `d79c0c91d366d778` |
| `kaggle/kernels/k10_g2.py` | `c5d5deae5a0fc4ea` |
| `kaggle/kernels/k10_g3.py` | `60be7e29c6ef787d` |
| `kaggle/kernels/k10_g4.py` | `e016227367998214` |
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
| `kaggle/kernels/shot2_k10_g1.py` | `53a4fb416c7cf0db` |
| `kaggle/kernels/shot2_k10_g2.py` | `60a69d62db603aa5` |
| `kaggle/kernels/shot2_k10_g3.py` | `bcc13018b6181ec1` |
| `kaggle/kernels/shot2_k10_g4.py` | `4963084c2ba9a507` |
| `kaggle/kernels/shot_FA.py` | `1f6796b36929c56d` |
| `kaggle/kernels/shot_FB.py` | `32410f94ff3fe736` |
| `kaggle/kernels/shot_k10_g1.py` | `6ea15b7edc7ec3a6` |
| `kaggle/kernels/shot_k10_g2.py` | `a8e1448057ff553f` |
| `kaggle/kernels/shot_k10_g3.py` | `d422c016022ca162` |
| `kaggle/kernels/shot_k10_g4.py` | `24173d1423a5e6ea` |
| `paper/check_manuscript.py` | `8e5256ea9420ff55` |
| `paper/figures/build_figures.py` | `b933a8122f238a25` |
| `paper/figures/build_schematics.py` | `726c3eab767ebc99` |
| `paper/figures/fig1_design.py` | `1d2c54cda18ad78b` |
| `paper/figures/fig_6203_lock.py` | `391c66d5cfc50244` |
| `paper/figures/fig_m1_leakage.py` | `64aeab3af6cee0b9` |
| `paper/figures/fig_splits.py` | `aebfc76283ac2af8` |
| `paper/figures/qa_layout.py` | `557f3de37bab2f57` |
| `paper/figures/style.py` | `1fb214879875a584` |
| `paper/figures/validate_figures.py` | `c583c898cbc5f17f` |
| `paper/make_highlights.py` | `44a5ab79019b670a` |
| `paper/make_s1.py` | `296569aabad53943` |
| `paper/make_s3_table.py` | `f2553d13064ce12f` |
| `paper/make_s4.py` | `cf76b40921f3080d` |
| `paper/make_submission.py` | `fff79915fdad68c1` |
| `paper/make_submission_documents.py` | `91d021f9904946ab` |
| `paper/make_supplement_pdfs.py` | `50801a3571a00b5e` |
| `paper/make_tables.py` | `0f5335210571eb47` |
| `paper/revision_reporting.py` | `a403fa39e52d3458` |
| `runners/bist.py` | `03571366b13b4eff` |
| `runners/sdalr_runner.py` | `9eea05d3c9899dfa` |
| `runners/shot_patch.py` | `a0d94196b59aa20b` |

## Regenerating reporting files only

Use the archived experiment repository plus this revision overlay; preserve the directory layout. No training is required. Historical experiment scripts remain available for audit; the withdrawn SHOT outputs must not be interpreted as valid SHOT performance.

```
python paper/revision_reporting.py
python paper/make_tables.py
python paper/figures/build_figures.py
python paper/figures/build_schematics.py
python paper/make_s1.py
python paper/make_s4.py
python paper/check_manuscript.py
```

