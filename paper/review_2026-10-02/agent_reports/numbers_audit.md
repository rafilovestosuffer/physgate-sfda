# Numbers audit: manuscript (`paper/tex/`) vs retained artifacts — 2026-10-02

Read-only audit. No repo file was edited. The helper scripts are in this scratchpad (`load_all.py`, `q7_preupdate.py`, `q689.py`, `regen_tables.py`). `all.pkl` caches the per-window predictions and pre-update accuracies parsed from `results/artifacts/`.

Paths: `S/` = `paper/tex/sections/`, `T/` = `paper/tex/tables/`, `A/` = `results/artifacts/`.

## 0. Summary

**Things that hold up:**
- All seven tables regenerate byte-identically from the artifacts. I called each `make_tables.tN()` in memory without calling `main()`.
- `check_manuscript.py` passes.
- The ledger has 1246 rows (670 + 576) and every `artifact_path` exists.
- The BH and BY adjustments recompute exactly.
- The 1:1 A/A floor holds: 54 repeat tasks match to 0.00.
- Every headline median I recomputed matches.

**Errors to fix (factual mismatches with the artifacts):**

| # | Where | Manuscript | Artifact | Verdict |
|---|---|---|---|---|
| E1 | `S/06_results.tex:259-260` | KA04 purity "falls from 1.00 to 0.56" | `paper/figures/data/fig3_purity.csv`: KA04 gated = **0.711** (KA16 = 0.512) | **WRONG** (0.56 is not any bearing's value) |
| E2 | `S/06_results.tex:273-274` | "divides the **1080** source recordings **508/572**" | CRC32 parity on the fold A+B source records gives **1020** records, split **508/512** (A: 271/269, B: 237/243). Fold A has 9 bearings × 20 × 3 = 540 and fold B has 8 × 20 × 3 = 480. | **WRONG** |
| E3 | `T/t1_datasets.tex:11` (hard-coded in `make_tables.py` t1) | Paderborn conditions "4 (2 used)" | `S/03_data.tex:10-11` uses three (A1, A2, A3) for adaptation, and N09 enters the gate and slip analyses | **WRONG**: it should say 3 used for adaptation (all 4 for gate/slip) |
| E4 | `S/99_declarations.tex:88-89` | "adaptation methods are run from their authors' released code … no numerical component of the released training pipeline is modified" | SHOT is `runners/shot_patch.py`, which replaces SDALR's `obtain_label` and `train_target` with our own SHOT re-implementation. `final_checkpoint_patch` changes checkpoint selection. `S/04_protocol.tex:95` itself says "SHOT is our implementation". | **CONTRADICTION** |
| E5 | `T/t3_collapse.tex:22`, `S/06:157` | fold A Recoverable **101 %** | `results/c88/C88_RESULT.md` reports **106 %** for the same cell. The two use different job-crossings (Q2). | **INCONSISTENT** and crosses jobs and source checkpoints |
| E6 | `S/08_recommendations.tex:165`, `S/07:33-34`, `S/10:94` | false acceptance "predicted the sign of the effect in every case we tested"; the raw-spectrum rule "makes accuracy worse" | `A/physgate-m2-fa`: the raw-spectrum gate is **+5.35 pp on fold A**, which is larger than v2 (+3.95) and pcv (+4.41). It is −13.21 on fold B. Over 12 tasks it is positive on 6. It was run on one seed and never on the ten splits. | **OVERSTATED** |
| E7 | `S/04_protocol.tex:83-84` | "we report every primary effect three ways … a bootstrap that resamples whole clusters" | No bootstrap CI appears anywhere in the manuscript. The CIs exist only in artifacts (Q10). | **CLAIM NOT MET** |
| E8 | `S/09_limitations.tex:17-18` | "no reported comparison crosses jobs" | The fold-row Recoverable % does cross jobs (Q2) | **FALSE as written** |
| E9 | `S/04_protocol.tex:55` (Fig. 1 caption) | "Gated and oracle arms reuse the same source checkpoint" | True for the ten splits. For the folds, the gating job's source model differs from the fold job's: pre-update accuracy differs by up to 9.3 pp (Q16). | **FALSE for the fold rows** |

**Wording that overreaches:**
- Highlight 2 ("…and at a fixed operating condition") follows a highlight about SFDA, but the fixed-condition control is random-forest only.
- `S/10_conclusions.tex:95` calls coverage "the share of **target recordings** … a median 24 %". The 24 % is the share of **faulty** target recordings. Over all target recordings the median is 15.2 %.
- `S/07_discussion.tex:30` says coverage "can be computed from the target recordings alone". The reported quantity uses target labels (Q5).
- `S/06:48` says "adaptation itself 2.2–5.4 points on clean targets". That holds on the folds only. On the ten splits, adaptation **lowers** clean accuracy in 7 of 10 splits (Q7).

## Item-by-item

### Q1. Table 1, Paderborn "4 (2 used)"
- **Manuscript:** `T/t1_datasets.tex:11` says "4 (2 used)". `S/03_data.tex:9-11` says "We use the three conditions … A1 (N15_M01_F10), A2 (N15_M07_F04) and A3 (N15_M07_F10); the fourth (N09) enters only the gate and slip analyses".
- **Artifacts:** every k10, m1 and m2 result has six tasks over A1/A2/A3 (`TASKS` in `experiments/c88_eval.py`). `c98` uses 3 adaptation conditions. `c90` and `c95` include N09.
- **Verdict: error.** The string is hard-coded in `paper/make_tables.py::t1_datasets`, so it must be fixed there. Suggested text: "4 (3 adaptation; 4 gate/slip)".

### Q2. Table 3 fold A "Recoverable 101 %"
- **Formula** (`paper/make_tables.py::t3_collapse`): `100*(orc − b)/(lk − b)`, where b is the **gating job's** ungated clean arm (56.762).
  - Fold A: (88.537 − 56.762)/(88.333 − 56.762) = 31.775/31.571 = **100.6 %**.
  - Leaky 88.333 comes from the **fold job** `A/physgate-m1-fa`.
  - Oracle 88.537 and clean 56.762 come from the **gating job** `A/physgate-m2-fa`.
- **C88 formula** (`experiments/c88_eval.py::fmt`): `(orc − ref)/(lk − cl)`, where the denominator uses the fold-job clean (58.363).
  - Fold A: 31.775/29.970 = **106 %** (written to `results/c88/C88_RESULT.md`).
  - So the paper's Table 3 and the C88 result file report two different values for the same cell. Both cross jobs.
- Fold B is unaffected (48 % either way) because both jobs give a clean arm of 55.312.
- **Does the gating job have its own leaky arm?** **No.**
  - `A/physgate-m2-fa/m2` and `A/physgate-m2-fb/m2` contain only F{A→B} and F{B→A} arms (none, c30, v2, pcv, eagle, oracle).
  - The repeat and seed jobs (`m2rep-*`, `m2seed-*`) and C103 are also clean-only.
  - So a within-job Recoverable share **cannot** be computed for the folds. The fold row necessarily combines a leaky arm from one job with oracle and clean arms from another.
- **Stronger than "crossing jobs": the two jobs used different source models.**
  - Fold A pre-update clean accuracy (accuracy before any adaptation step, from `adapt_NN.log`):
    - m1: [63.23, 68.47, 57.53, 67.82, 36.33, 36.18]
    - m2: [65.12, 69.28, 57.65, 67.97, 45.63, 44.37]
  - The source pretraining logs (`…FAtoA…/pretrain.log` in m1 vs `…FAtoB…/pretrain.log` in m2) are identical up to epoch 5 and diverge from epoch 6.
  - So the fold-row Recoverable % divides an oracle gain measured from checkpoint X by a leaky arm measured from checkpoint Y.
- **Verdict:**
  - 101 % is arithmetically correct for the stated formula.
  - It contradicts "arms are never crossed between jobs" (`S/04:162`, `S/09:17`).
  - It contradicts the C88 artifact's 106 %.
  - The fold Recoverable column (and `S/06:157` "fold A 101 %") should be dropped, or labelled as cross-job and cross-checkpoint.

### Q3. Table 4, RF (time statistics) clean 63.6 on both folds and ten splits
- Folds: `A/physgate-c91-shallow-cpu/c91/c91_result.json` T.clean_mean = **63.5806**.
- Ten splits: `results/c101/c101_rf_splits.json`, mean of per-split clean = **63.6172** (71.06, 63.08, 64.74, 58.41, 74.46, 52.04, 73.05, 68.18, 53.09, 58.06). These equal `A/physgate-run-c92-*/c92_result.json`.
- **Verdict: coincidence of rounding (63.58 vs 63.62), not a copy error.** Both are generated by code from different artifacts.
- Side note: `c101_rf_splits.json` stores the **cluster-bootstrap mean** (23.397 and 35.508) under the key `"median"`. The true medians are 22.65 and 32.09, which the manuscript uses correctly. This is an artifact labelling bug.

### Q4. "The unsafe raw-spectrum rule lowers accuracy by 3.9 points" (`S/06:255-256`)
- **Source:** `results/M2_SINGLE_RUN.md:29,32` (eagle −3.93). Recomputed from `A/physgate-m2-f{a,b}/m2/result_*_gateeagle_s2024.json` minus the same job's ungated arm, over the 12 fold tasks at **seed 2024 only**:
  - Mean −3.93, median −4.03, min −20.01, max +6.63, positive in 6/12 tasks.
  - Fold A: **+5.35** (per task +6.25, +4.29, +6.63, +2.35, +6.05, +6.53).
  - Fold B: **−13.21** (−17.1, −10.4, −10.63, −10.51, −20.01, −10.63).
- It was never run on the ten splits or on other seeds. It is not in Table 6, and no p-value is possible (two clusters).
- **Verdict:**
  - The number traces, but it is a two-fold, one-seed mean whose sign flips between folds.
  - "makes adaptation worse" and "false acceptance predicted the sign … in every case" are not supported on fold A.
  - Coincidence: the surrogate-null comb (c30) gain is exactly +3.93 on the same 12 tasks.

### Q5. Coverage definition and correlations (`results/c98`)
- **Definition** (`experiments/c98_inloop_coverage.py::coverage`): `spoke_share_faulty = |records with ground-truth fault_type ≠ normal AND gate verdict ≠ normal| / |records with fault_type ≠ normal|`.
  - Both the numerator and the denominator use **target labels**.
  - The numerator counts **any** fault verdict on a faulty record, including wrong-race verdicts (S03: 2 spoken, 1 correct). It is not restricted to correct verdicts.
- **"Computed from the target recordings alone, before adapting anything"** (`S/07:30`, `S/06:201`, `S/10:96`):
  - **Literally false** for the reported metric.
  - The label-free analogue (share of **all** target records given a fault verdict, `spoke_share`) gives **Spearman ρ = 0.930, p = 9.6e-5**.
  - Every split has 480 records and 300 faulty ones, so the two metrics differ only by the healthy false acceptances (S00 42 vs 41, S05 78 vs 77, S07 48 vs 47).
  - So the substance survives, but the stated 0.95 is the label-based number.
- **Recomputed:**

| Relation | Reported | Recomputed |
|---|---|---|
| gain ~ coverage | ρ 0.95, p 2e-5 | ρ = 0.9512, p = 2.3e-5 ✓ (leave-one-split-out ρ 0.933–0.979; Pearson 0.940) |
| gain ~ headroom | 0.53, p 0.12 | 0.527, p 0.117 ✓ |
| coverage partial (headroom out) | 0.98, p 1.5e-6 | 0.976, p 1.5e-6 ✓ |
| headroom partial (coverage out) | −0.07, p 0.85 | −0.067, p 0.85 ✓ |

- **Caveat on the partial correlations.**
  - The script computes them non-standardly: it regresses the ranks on z, re-ranks the residuals, then calls `spearmanr`, whose p-value uses n−2 instead of n−3.
  - The textbook partial Spearman gives **0.932 (p = 2.5e-4, df = 7)** for coverage and **0.043 (p = 0.91)** for headroom.
  - The qualitative conclusion is unchanged, but "0.98" and "1.5e-6" are method-dependent and optimistic.
- **Medians:**
  - "Speaks on a median 24 %" = median of `spoke_share_faulty` over 12 target sets = 24.3 % ✓.
  - Over all records the median is 15.2 % (relevant to `S/10:95`).
- **Interpretive point:** see Q9. The gain is produced almost entirely on the certified windows, so ρ(coverage, gain) is close to mechanical.

### Q6. Per-window predictions and purity
- **Availability:**
  - `pred_NN.npz` (keys `prob` 6000×3, `label`, `record_id`, `index`) exist for every arm of the ten splits (`A/physgate-run-k10-g{1..4}/k10/Sxx/logs_*`: leaky, clean, gatepcv, gateoracle), for SHOT k10 and folds, for the gating jobs m2/m2rep/m2seed, and for C103.
  - They do **not** exist for the fold job (`A/physgate-m1-f*`, logs only), so the fold **leaky** arm has no per-window predictions.
  - Labels: 0 = normal, 1 = inner, 2 = outer. The npz accuracy reproduces `result_*.json` exactly.
- **Fig. 3 (fold B direction, gating job m2-fb, ungated):** purities K001–K003 1.000, KA04 1.000 (I), KA15 0.999, KA16 1.000 (I), KI04 1.000 (N), KI14 1.000 (O), KI16 0.999.
  - "1.000 for every bearing" holds after rounding ✓.
  - The labels match the text ✓.
- **Fold A direction (m2-fa ungated) is not block-pure:** K004 0.667, K005 0.667, KA30 0.942, KI17 0.559, KI18 0.619, KI21 0.664.
- **Ten splits, clean arm, purity pooled over the six tasks** (the manuscript's definition):
  - 80 bearing-split pairs: median 0.994, min 0.500.
  - **Only 42 % are 1.000 and 51 % are ≥ 0.99.**
  - Per split, the count with purity ≥ 0.99 is: S00 1/8, S01 6/8, S02 5/8, S03 4/8, S04 5/8, S05 3/8, S06 3/8, S07 2/8, S08 7/8, S09 5/8.
- **Per task:**
  - 480 bearing-task pairs (clean arms): **89.2 % have purity ≥ 0.99**, median 1.000.
  - Of the 300 faulty bearing-task pairs: 167 are pure and wrong, 84 pure and right, 49 mixed.
  - **The leaky arms are block-labelled just as often** (89.8 % ≥ 0.99), so block labelling is generic. What differs is whether the block label is correct.
- **Verdict:**
  - Block labelling holds **within a task** for about 90 % of bearings.
  - Pooled over a split's six tasks it holds for only about half, because the block label changes with the condition pair.
  - The fold B figure is the cleanest case and is not representative. "assigns a single label to each unseen specimen as a whole" (`S/10:84`, `S/07:12`) should be qualified to "within a task".

### Q7. Pre-update (source-only) accuracy and leaky vs clean, before and after adaptation
Pre-update accuracy is logged in every `adapt_NN.log` (first `批次: 0/N; 总正确率` line), for leaky and clean arms, ten splits and folds.
- Within a split, the pre-update accuracy is identical across the none, pcv and oracle arms in all 60 tasks (pairing claim `S/04:107-109` ✓).
- It is also identical across all 9 gating-job arm groups.
- SHOT k10 shares the SDALR source checkpoint per split. SHOT fold runs do not.

**Ten splits (SDALR final_checkpoint, seed 2024), split means:**

| split | pre leaky | pre clean | Δ pre | adapted leaky | adapted clean | Δ adapted | Δ adapted − Δ pre | clean: adapted − pre |
|---|---|---|---|---|---|---|---|---|
| S00 | 90.29 | 55.49 | 34.80 | 91.52 | 66.51 | 25.02 | −9.79 | +11.02 |
| S01 | 93.91 | 43.31 | 50.60 | 96.10 | 39.83 | 56.27 | +5.66 | −3.48 |
| S02 | 88.53 | 53.12 | 35.41 | 88.80 | 51.56 | 37.25 | +1.83 | −1.56 |
| S03 | 91.10 | 61.84 | 29.26 | 93.77 | 58.61 | 35.16 | +5.90 | −3.23 |
| S04 | 77.97 | 75.92 | 2.04 | 82.19 | 74.03 | 8.16 | +6.12 | −1.89 |
| S05 | 96.24 | 31.93 | 64.30 | 98.03 | 36.42 | 61.61 | −2.70 | +4.49 |
| S06 | 88.02 | 66.86 | 21.16 | 90.19 | 68.57 | 21.62 | +0.46 | +1.72 |
| S07 | 96.19 | 55.05 | 41.15 | 99.23 | 51.47 | 47.75 | +6.61 | −3.57 |
| S08 | 95.34 | 40.30 | 55.04 | 97.07 | 37.64 | 59.42 | +4.38 | −2.66 |
| S09 | 87.76 | 63.40 | 24.36 | 89.52 | 60.08 | 29.43 | +5.07 | −3.32 |

- The source-only Δ_leak has a **median of 35.1 pp**. The adapted Δ_leak has a median of 36.2 pp.
- Adaptation **amplifies** the leak in 8 of 10 splits (median +4.7 pp; two-sided Wilcoxon p = 0.16, not significant).
- On leaky targets adaptation adds a median +2.0 pp.
- On clean targets adaptation has a **median effect of −2.3 pp and lowers accuracy in 7 of 10 splits**.

**Folds (fold job m1):**
- Fold A: pre-update Δ 32.65, adapted Δ 29.97. Clean adaptation gain +3.44 (as_released +5.45).
- Fold B: pre-update Δ 45.81, adapted Δ 44.60. Clean gain +2.21.
- On the folds, adaptation slightly **reduces** the leak.

**SHOT (ten splits, same source checkpoints as SDALR):** the median Δ goes from 35.1 (pre-update) to 21.7 (adapted), a median change of −9.1. SHOT's smaller collapse comes mostly from adaptation **lowering leaky accuracy** (S01 93.9 → 72.8, S08 95.3 → 73.0), not from raising clean accuracy.

**Verdict:**
- The collapse is already essentially complete in the source model. SDALR adaptation adds little on average (slightly amplifying it on the splits, slightly reducing it on the folds).
- `S/06:48` "adaptation itself 2.2–5.4 points on clean targets" is fold-only. On the inferential ten splits, adaptation is net harmful on clean targets.
- Not reported anywhere in the manuscript. Worth adding, because it answers the "does adaptation amplify the shortcut" question that `S/09:43-44` says is unmeasured (for the fixed-condition case).

### Q8. Within-bearing contrast (seen in source vs unseen), ten splits, adapted ungated SDALR
- **Method:** per-bearing accuracy from the per-window predictions. "Seen" uses the leaky arm of splits where the bearing is in the source; "unseen" uses the clean arm. Each is the mean over (split, task).
- All 17 bearings appear both ways:

| bearing | seen | unseen | Δ |
|---|---|---|---|
| K001 | 100.0 | 90.5 | +9.5 |
| K002 | 100.0 | 82.3 | +17.7 |
| K003 | 100.0 | 100.0 | 0.0 |
| K004 | 100.0 | 100.0 | 0.0 |
| K005 | 100.0 | 94.3 | +5.7 |
| K006 | 100.0 | 100.0 | 0.0 |
| KA04 | 87.5 | 25.0 | +62.5 |
| KA15 | 68.1 | 29.4 | +38.7 |
| KA16 | 75.0 | **0.03** | +74.9 |
| KA22 | 100.0 | 55.4 | +44.6 |
| KA30 | 93.9 | **0.01** | +93.8 |
| KI04 | 84.1 | 60.8 | +23.3 |
| KI14 | 86.5 | 42.6 | +43.9 |
| KI16 | 95.1 | 41.0 | +54.1 |
| KI17 | 95.5 | 20.9 | +74.7 |
| KI18 | 96.2 | 31.1 | +65.1 |
| KI21 | 100.0 | 74.4 | +25.6 |

- **Median within-bearing difference: 38.7 pp** (mean 37.3); positive for 14/17 bearings (the other 3 are tied at 0); one-sided Wilcoxon p = 4.9e-4.
- By class: healthy median 2.9, outer 62.5, inner 49.0.
- **Caveat:** the seen and unseen arms differ in which other bearings are in the transductive target batch, so this is not a pure same-model contrast. It is still the cleanest specimen-level evidence available, and it is not in the manuscript.

### Q9. Does the gate improve accuracy on recordings it did not certify?
- Clean arms, PCV-gated vs ungated, pooled over the six tasks.
- Windows are grouped by their record's pcv verdict (`results/m2/gate_verdicts.json`, which matches `h7_records.csv` pcv_class on all 2319 records).
- Median within-group gain over 10 splits:
  - **Certified** windows: **+47.0 pp** (positive 10/10).
  - **Uncovered faulty** windows: **+0.33 pp** (mean −0.32, positive 7/10). S00 −4.4, S09 −3.1, S03 −2.2.
  - **Uncovered healthy** windows: 0.0 (S05 +4.9, S07 −4.6).
- **Contribution to the split gain:**
  - Certified windows: median +5.82 pp.
  - Uncovered faulty windows: median +0.16 (mean −0.30).
  - Uncovered windows together contribute **−3.7 %** of the summed gain.
- **Folds (gating job):**
  - Fold A: certified 29.5 → 90.6; uncovered faulty 48.9 → 47.2.
  - Fold B: certified 28.6 → 61.7; uncovered faulty 35.3 → 35.2.
- **Verdict: no transductive spillover.** The gate helps only where it speaks, and slightly hurts elsewhere in some splits. The gain is close to coverage × (fix on covered windows), so ρ(coverage, gain) = 0.95 is close to mechanical. The headroom-partial argument in `S/06:204-207` is therefore less informative than presented. `S/06:261` ("says nothing on the three quarters … it does not certify") is confirmed quantitatively.

### Q10. Bootstrap confidence intervals
**Computed in artifacts:**

`results/c96/C96_RESULT.md` (cluster bootstrap of the **mean**):

| effect | mean (pp) | 95 % CI |
|---|---|---|
| collapse, 2 folds | 37.28 | [29.97, 44.60] (just the two fold values; meaningless with 2 clusters) |
| collapse, 10 splits | 38.17 | [27.81, 48.43] |
| gate gain, 10 splits | 7.82 | [3.30, 13.07] |
| v2 gain, 2 folds | 3.73 | [3.52, 3.95] |
| pcv gain, 2 folds | 5.70 | [4.41, 6.99] |
| RF-T, 10 splits | 23.35 | [16.77, 29.42] |
| RF-TFE, 10 splits | 35.47 | [28.85, 43.54] |
| HUST | 39.12 | [30.14, 49.77] |
| C104 | 29.81 | [23.59, 36.08] |
| SHOT | 25.30 | [16.36, 35.21] |

Also:
- `results/c100/C100_RESULT.md:18` gives the SHOT CI [16.4, 35.2].
- `results/c101/C101_RESULT.md:21,38` gives RF-T [17.0, 29.5] and RF-TFE [28.9, 43.7].
- `results/h6_c35`, `results/b6a` and Supplementary S3 have bearing-cluster bootstrap intervals for gate rates.

**In the manuscript: none.** A grep of `sections/` and `tables/` finds no CI, and every effect is reported as a median plus p.

Further issues:
- `S/04:83-84` promises a bootstrap for every primary effect.
- `S/04:104-105` promises bearing-cluster intervals on record-level rates, yet 1/480, 9/480 and 214/480 are reported bare.
- The artifact CIs are for the **mean** while the paper headlines **medians**.
- `paper/figures/build_figures.py:206-207` (Fig. 6) draws a **task-level, non-cluster** bootstrap CI of the median over 12 tasks (2000 resamples). This is the resampling the protocol calls invalid, and the caption (`S/06:242`) does not mention it.

### Q11. BH/BY values (`results/c96/c96_family.json`, 10 members)
- Recomputed from the cluster p-values [0.25, 0.000977 ×5, 0.00293, 0.015625, 0.25, 0.25]:
  - BH: 0.001953 (ten-split collapse, RF ×2, C104, SHOT), 0.004883 (gate gain), 0.022321 (HUST), 0.25.
  - BY with c(10) = 2.928968: 0.00572, 0.01430, 0.06538, 0.7322.
- Text vs artifact:
  - p_BH 0.002 (`S/06:55,78,100`, `T/t4`) ✓
  - 0.005 (`S/06:253`) ✓
  - 0.022 (`T/t7`) ✓
  - p_BY "largest 0.014" for ten-split results (`S/04:93`) ✓
  - HUST 0.065 ✓
- The gate-gain cluster p (0.00293) equals the Wilcoxon p by coincidence. The exact sign-flip count is also 3/1024.
- **All match.**

### Q12. Highlights (`paper/tex/main.tex:33-37`; limit 85 characters including spaces)

| # | chars | text |
|---|---|---|
| 1 | 74 | Bearing-disjoint targets cut source-free adaptation accuracy by 37 points. |
| 2 | 82 | The loss replicates on a second rig, for SHOT, and at a fixed operating condition. |
| 3 | 74 | Ten time statistics identify same-class bearings in 508 of 508 recordings. |
| 4 | 72 | A physics gate's gain tracks how many target recordings it can speak on. |
| 5 | 70 | A non-adaptive forest also collapses: a calibration bar, not a remedy. |

- **All pass the length limit.**
- Content notes:
  - #1 uses the descriptive two-fold 37.3 rather than the inferential ten-split median 36.2.
  - #2 implies SFDA was run at a fixed condition, but only the RF was (`S/09:42-44`).

### Q13. SHOT code
- `runners/shot_patch.py` (128 lines; header: "SHOT target adaptation … patched into SDALR's target script").
- It replaces SDALR's `obtain_label` and `train_target` with a SHOT-style implementation:
  - frozen classifier head;
  - β = 0.3 CE + entropy − diversity;
  - weighted-centroid cosine pseudo-labels with one refinement, recomputed each epoch;
  - SDALR's backbone, loaders, schedule and `lr_scheduler`.
- Activated by `runners/sdalr_runner.py:109-113` (`variant == "shot"`).
- It is **our re-implementation** spliced into SDALR's code, not the released SHOT repository (tim-learn/SHOT) run as-is.
- **Verdict:** `S/99_declarations.tex:88-89` contradicts `S/04:95` and the code. Suggested wording: "SDALR is run from its authors' released code (commit fb9c379, `third_party/SDALR_UPSTREAM.txt`) with two adapters …; SHOT is our implementation of the published method on SDALR's pipeline (`runners/shot_patch.py`)". Also delete "no numerical component … is modified".

### Q14. Recomputations from Table 3 and related claims
- **Median Δ_leak:** 36.20 (range 8.16–61.61) ✓.
- **Gain:** median +4.51, positive 9/10 ✓.
- **Recoverable share:** median 82 % ✓.
  - Values sorted: 48.2, 60.0, 68.0, 76.0, 79.0, 84.7, 89.9, 89.9, 98.2, 221.7.
  - The IQR "68–90 %" (`S/06:154`) uses hinge or inverted-CDF quantiles. numpy's default gives 70–90. It is not printed in any artifact.
- **"Closes a median 19 % of the oracle gap":** median of gain/(oracle − clean) = 0.1948 ✓. It matches `C88_RESULT.md` (D).
- **"RF beats adapted model by median 8.9":**
  - RF-T clean minus SDALR clean per split: +4.55, +23.25, +13.18, −0.20, +0.43, +15.62, +4.48, +16.71, +15.45, −2.02. The median is +8.865 ✓.
  - It is positive in only **8/10** splits and has no test.
  - "Matches the gated method" (`S/07:42`): RF − gated median +0.94 (range −6.88 to +16.04) ✓.
- **Fold and other text values, all ✓:**
  - Fold means 94.12 / 56.84 / Δ 37.28.
  - as_released 94.71 / 57.84 / 36.87.
  - Selection worth 0.59 (leaky) and 1.00 (clean).
  - Per-task range max 4.05 (`S/06:48` says "4.1"; 73.53 − 69.48 = 4.05, a borderline rounding).
  - Fold B leaky per task: 99.73–100. Clean per task: 55.27–55.33.
  - Gating-job clean 56.04, giving collapse 38.08.
- **Table 6 and its text:** seed means 3.79 / 4.56 / 3.73 and 7.44 / 7.99 / 5.70. Mean of means: 4.027 and 7.045 ✓. Between-seed SD of per-task gain: 1.73 (comb) and 2.44 (envelope), against 2.75 for ungated accuracy ✓. Variance ratios: 0.37 and 0.74, stated as "0.4 / 0.7" ✓.

### Q15. Slip (`results/c90/`)
- **Median, range and counts:**
  - IBU/MTK median 0.06 %, 5–95 % range −0.31 to +0.22 (width 0.53, `S/03:43`) ✓.
  - FAG median −0.07 (−0.065), p95 0.88 ✓.
  - 304 measurable records = 242 + 52 + 10 CWRU fan end ✓.
  - 304/1872 = **16.2 %** ✓.
  - 3 in-lock records, all KI21 at N09, all failing the masked arm ✓.
- **Estimator accuracy "within 0.17 %":**
  - True for the **unmasked** arm (max |error| 0.170 %).
  - The masked arm reaches **0.28 %** (FAG outer at 1.78 %: 1.50).
  - `c90_synthetic.txt` has **15 lines, not 20**: FAG (2855) inner race is missing, although `C90_RESULT.md` says "both PU geometries and both races".
- **Negative slips** (physically, cage slip should be ≥ 0):
  - **90 of 304 measurable 6203 records (30 %) are negative.**
  - IBU/MTK: 49/242 (20 %), min −1.00 %, 22 below −0.2 %. The max is +4.07 %, outside the ±2 % search the gate uses.
  - FAG: 35/52 (67 %), min −0.40 %.
  - CWRU fan end: 6/10, min −0.63 %.
  - CWRU drive end 6205: 21/21 negative, median −0.33 %.
  - The manuscript attributes a −0.3 % offset only to CWRU (`S/06:325-327`). The PU negatives imply a comparable ±0.3 % estimator/speed bias on PU, which is the same order as the 0.06 % median being reported.

### Q16. The 1.6-point cross-job gap (C103)
- `A/physgate-c103-pretrain-state/c103/result_pretrain_in_process.json` and `result_skip_pretrain.json` are identical per task (76.13, 76.98, 61.12, 57.72, 34.07, 34.55; mean 56.762). They also equal m2-fa, m2rep-fa-r1 and m2rep-fa-r2 (54 repeat tasks, max |Δ| 0.00) ✓.
- The fold job m1-fa clean arm is 58.363 (76.3, 77.08, 66.6, 69.48, 30.2, 30.52). Gap 1.60 ✓. Fold B agrees: 55.312 both.
- **New finding:** the gap is already present in the **source model**.
  - Pre-update fold A clean accuracy is identical in m2 and C103 but differs in m1 (A2→A1: 36.33 vs 45.63; A2→A3: 36.18 vs 44.37).
  - The pretrain logs diverge from source epoch 6 (loss 0.004 vs 0.018; source accuracy 100.00 vs 99.82 %).
  - `results/c103/C103_RESULT.md`'s statement that "the wrapper first runs at the pre-update evaluation, before any training step" is therefore contradicted by the logs. The RNG shift must already act during source pretraining (presumably at the mid-pretraining evaluation).
  - The manuscript text (`S/04:158-161`) is compatible with an RNG shift. It should say the two jobs trained **different source checkpoints**, which bears directly on Q2 and Fig. 1.
- **Provenance quirk:** `c103/pretrain_in_process/result_PU_M1_final_checkpoint_FAtoB_s2024.json` has the skip_pretrain arm's timings (no `pretrain` key), so the logs in `pretrain_in_process/` are probably arm 2's.
- `experiments/c88_eval.py::m1_rows` docstring still says "GPU non-determinism" (stale since C102).

### Q17. Same-condition control (`results/c104/`)
- **C104 (all ✓):**
  - Leaky median 94.05 (94 %). Clean median 65.0 (65 %; midpoint of 60.0 and 70.0, a large gap).
  - Δ median 29.65 (29.7), positive 10/10, p = 1/1024.
  - Folds: fold A 30.1, fold B 42.1.
- **C104b** (`c104b_per_class.json`): median per-split drops are healthy 1.67, inner 28.50, outer 65.99 ✓, each positive 10/10. Healthy recall 99.9 → 98.2 ✓.
- **Pitting 64 % vs plastic deformation 23 %:**
  - These medians **include the two folds** (10 and 8 target sets: 63.7 % and 22.6 %).
  - Over the ten splits only: pitting 64.7 % (n = 8) and plastic 22.6 % (n = 6).
  - The values are highly heterogeneous. Pitting includes two 0.0 splits (S05, S08). In S00, plastic (81 %) exceeds pitting (64 %).
  - The text places these figures inside the ten-split control; it should say "over 10 / 8 target sets including the folds".
- **Comparability:** C104 reports **balanced** accuracy on recording-disjoint halves, while the 22.7 cross-condition RF loss is plain accuracy with all source recordings. "More than the same forest's 22.7-point cross-condition loss" (`S/06:101`) compares slightly different metrics and training sets. The paper says the comparison is "forest-internal", but not that the metric differs.

### Q18. `python paper/check_manuscript.py`
```
checked 21 headline numbers, 32 citations, 34 labels
manuscript checks passed
```
- Exit code 0.
- The checker only tests substring presence of each value in both the manuscript and the source file. For example, "82" or "0.000" match anywhere. It could not catch E1 (0.56), E2 (1080) or E3 ("2 used").
- `python -m pytest tests/ -q`: **73 passed in 99 s** (CLAUDE.md states < 60 s).

## Other numbers verified (no issue)
- **Abstract:**
  - 94.1 → 56.8; median 36.2, p = 0.001.
  - HUST 33.5; SHOT 21.7; RF +8.9.
  - Probes 507/508 (`results/c87/N1_RESULT.md`) and 508/508, chance 0.353, p = 1.9e-230 (`results/c97`).
  - 29.7; 82 %.
  - Gates 1 / 0 / 9 / 214 of 480; median +4.5; 19 %; ρ = 0.95.
- **Table 5 and ROC** (`results/roc/roc_pu.json`):
  - pcv z = 10: 366 correct / 1 FA; at zero FA 351 (z = 15).
  - v2 312/0; c30 309/9; eagle 429/214, 0 at zero FA.
  - "373 of 1839 before FA passes 10 %" = pcv z = 8 (8/480).
  - Eagle has no correct verdict below 55/480 = 11.5 % FA.
  - z = 40 gives 333 = 91 % of 366.
  - C99: 4/24 at z = 10; z* = 36.
- **C95:** 7/11 real (209/880), 6/12 artificial, v2 5/11, eagle 9/11. **C98:** KA04 41/60, KA16 40/60, KI16 32/60, KI18 45/60, KA30 1/60.
- **Gate correctness and engagement:** "Right in 96–100 % of cases on eleven of twelve" (S07 is 95.8 %). Median 2 of 5 bearings engaged.
- **HUST (Table 7):** mean leaky 98.7, clean 59.6.
- **Reproduction** (`results/M0_PU_RESULT.md`, `M0_JNU_RESULT.md`): 96.20 vs 96.78; 98.03 vs 98.50; 93.90 ± 4.72; 90.34 ± 4.88.
- **Kinematics:** BPFO 3.0706 and 3.0543; s* 2.30 / 1.78 / 1.74 %; the 28.50 mm substitution shifts the order by 0.58 %.
- **Window counts:** 680/660/660 and 1000/1000 confirmed in the npz files. The 55.33 % arithmetic is ✓.
- **Ledger:** 1246 rows ✓.

## Numbers I could not trace to an artifact
- "Interquartile range 68–90 %" (`S/06:154`): reproducible only with a non-default quantile rule; not printed in any result file.
- The JNU and Paderborn datasheet counts (32 datasheets, 26/6 split; `S/03:29-34`): I did not open the PDFs.
- Vieira survey counts (18 papers, five at 100 %, 8/9 split types; `S/01:14-16`): literature, not an artifact. Not checked.
