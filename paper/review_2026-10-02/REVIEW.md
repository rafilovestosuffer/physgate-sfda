# Referee report — "Bearing-wise evaluation of source-free domain adaptation: leakage and the limits of physics gating"

Target: Mechanical Systems and Signal Processing. Reviewed 2026-10-02 against `paper/tex/` (HEAD `b95740f`).
Sources: full read of all sections, tables and figures; five independent checks whose reports are in `agent_reports/`
(citations vs primary sources, literature/novelty search, numbers vs ledger artifacts, an independent blind referee
report, MSSP guide compliance). Every claim below marked **[verified]** was re-checked by hand at the source
(log file, artifact, or paper page); others cite the audit file that computed them.

**Recommendation: MAJOR REVISION.** The headline finding (bearing-disjoint targets lose ~36 pp, 10/10 splits, replicated
across methods, forests and a second rig) is solid and important. But (1) the paper's own logs show the loss is already
present *before* adaptation, which undercuts the SFDA-specific framing; (2) the nearest neighbour (Vieira et al., MSSP
2026) already contains the paired fixed-train design and a same-condition repetition-wise control on Paderborn, so two
of four novelty claims must be narrowed; (3) a provenance error (fold and gating jobs trained different source models)
contradicts statements in the text, a figure caption and the graphical abstract; (4) the mechanism, oracle-bound and
coverage claims are stronger than the design identifies. Most fixes need no new GPU compute.

---

## What is strong (keep, and say it earlier)
- Effect is large, consistent (10/10 splits for SDALR, SHOT, two forests, same-condition control) and replicated on HUST.
- Target-label-free checkpointing, A/A floor of 0.00, failed hypotheses reported, shallow-baseline calibration bar.
- Gate false-acceptance on real healthy recordings is genuinely unreported in the physics-gated SFDA literature
  (claim iii survives the literature search).
- Reproducibility apparatus (ledger, protocol history, retained artifacts) is far above the field norm.

---

## MAJOR revisions (ranked)

### M1. The SFDA-specific motivation is contradicted by your own logs — reframe the paper around this result  [verified]
- Intro ¶4 (`01_introduction.tex` "SFDA deserves separate scrutiny…") argues adaptation *sharpens* an identity decision.
  The pre-update (source-only) target accuracy is logged for every arm. On the ten splits:
  - source-only Δ_leak median **35.1 pp**; after SDALR **36.2 pp**; amplification +4.7 pp, 8/10, two-sided Wilcoxon
    p = 0.16 (not significant);
  - adaptation **lowers** clean accuracy in 7/10 splits (median −2.3 pp). The text's "adaptation itself 2.2–5.4 points
    on clean targets" (`06_results.tex`, §6.2) holds only on the two folds;
  - SHOT: source-only 35.1 → adapted 21.7; SHOT's smaller loss comes mainly from adaptation *lowering leaky* accuracy.
- Consequence: the collapse is a property of the source model trained on 3 bearings/class; SFDA neither creates nor
  repairs it. This is a cleaner and more honest headline, and it is new information.
- **Do:** add a "source only" row/column to Tables 3–4 and Fig. 2; rewrite Intro ¶4 as a tested hypothesis with this
  answer; reconsider title/abstract framing ("source-free adaptation inherits, and does not repair, a source-model
  collapse"). Script: `agent_reports/q7_preupdate.py`.

### M2. Novelty overlaps with Vieira et al. 2026 and recent work are under-stated  [verified for Vieira]
- Vieira et al. (MSSP 258, 114640; arXiv v5 §6) already (a) hold the training set fixed and vary only the test set —
  "no prior work has done so solely by altering the test set" — i.e. the paired leaky/clean idea; (b) run a
  **repetition-wise** split on Paderborn (same bearing, same condition, held-out recordings; Table 12: 98.6–100 % vs
  54–77 % Macro-AUROC leakage-free), which is the substance of your claim (iv); (c) show per-bearing feature blocks
  ("memorize intrinsic signal characteristics", Fig. 16), which anticipates the identity-probe argument.
- Knap et al. include a "PU Cross-Bearing Instance" scenario (held-out K001, KA30, KI21, KB23) and call it among the
  hardest — so "still permits the same physical bearing on both sides" describes their *default* rule only.
- Concurrent/recent (existence verified): Nagaswetha & Pathak, arXiv:2609.31639 (held-out-bearing UDA; order-domain
  representation + MMD reaches 0.95 — must be reconciled with "any source-trained classifier", see M3);
  Kaya & Jobani, Sensors 26:3829 (bearing-code-disjoint PU, Macro-F1 ≈0.56); Schlachter et al., EUSIPCO 2025,
  arXiv:2504.11992 (upper bound from perfect pseudo-labelling in SFDA — nearest neighbour for claim ii).
  Unverified-by-hand but reported by the search: Lei, SSRN 7226340; Jia et al., Adv. Eng. Inform. 62:102774.
- False sentence: `02_background.tex` "In all of this work the target domain is a different operating condition of
  the same physical bearings" — Jeong et al. (test-only VBL-VA001 rig), Bio-SFDA (CWRU→PU) and PCTL (CWRU↔PU) cross rigs.
  Also "applies it where it has not been applied" must be narrowed to *paired, within-rig, shared-checkpoint SFDA*.
- **Do:** rewrite the novelty paragraph with C50-style deltas: (i) Vieira's fixed-train design applied to SFDA with a
  shared checkpoint and a source-only arm (M1); (ii) oracle ceiling *after* Schlachter, plus the decomposition;
  (iii) unchanged; (iv) narrowed to "ten-split, cluster-level replication of Vieira's repetition-wise result with a
  per-class mechanism breakdown". Cover letter must stop saying Vieira "explicitly placed [SFDA] out of scope"
  (round 4 already established the phrase is not in their text — `submission/cover_letter.md`).

### M3. The mechanism ("identity shortcut … in the signals … any classifier") is not identified  
- Identifiability ≠ use. A probe that separates bearings within a class shows the information exists, not that the
  classifier relies on it. Competing explanation: 3 specimens/class under-sample damage-signature variability
  (extent, mechanism, manufacturer, session). Your own data favour the latter in places: unseen *healthy* bearings
  transfer (recall 99.9 → 98.2 %) though equally identifiable; C104b shows a mechanism effect (plastic deformation 23 %
  vs pitting 64 %); §6.3 already retreats to "specimen-level damage signature" while Intro/Discussion/Conclusions
  still say "identity", "memorisation", "which bearing it is listening to". Harmonise.
- Block labelling is not clean-specific: per task 89 % of clean bearing×task pairs are block-labelled, but so are 90 %
  of **leaky** ones; pooled over a split's six tasks only 51 % have purity ≥ 0.99; the fold-A direction is not pure
  (K004 0.667, KI17 0.559) (`agent_reports/numbers_audit.md` Q6). Fig. 3 shows the one direction where it holds.
- Representation (MSSP reviewers will compute this): a 2048-sample window at 64 kHz is 32 ms = 0.8 shaft revolutions,
  ~2.5 BPFO impacts; envelope resolution ≈31 Hz, so BPFO (≈77 Hz) and BPFI (≈123 Hz) are ~1.5 bins apart. The
  networks and forests cannot represent the kinematic signature the gates use on the full 4 s record. "Available to any
  source-trained classifier" and "the mechanism sits in the data" over-generalise from this input contract — and the
  concurrent held-out-bearing study reports order-domain inputs recover most of the gap.
- Logical contradiction: Conclusions say a representation-level remedy cannot address the root cause "since the
  information is present before any representation is learned"; §9 calls a class-conditional adversary "the obvious next
  experiment". Invariance learning exists precisely to remove nuisance information present in the input. Delete the
  Conclusions sentence.
- Probe details: "1080 source recordings … 508/572" is wrong — the pool is 1020 (540 + 480), split 508/512 [chance 0.35
  matches 1020]; "p < 10⁻²⁰⁰" treats recordings as independent (§4 says they are not); the mean statistic largely
  encodes the sensor/amplifier chain.
- **Do (CPU only):** (a) forest learning curve vs 1–4 source bearings/class (identity shortcut predicts flat; under-
  sampling predicts rising); (b) probe per class incl. healthy, without the mean, per statistic; (c) nearest-source-
  bearing test: does an unseen bearing receive the label of its nearest source bearing in feature space?; (d) one
  forest on order-domain envelope features from the full record under the same splits.

### M4. "Attributable to bearing overlap alone" and the decomposition's second term are not identified
- Leaky and clean targets contain *different bearings* (difficulty, mechanism, manufacturer — KA04/KA15/KI16/KI21 are
  FAG — extent, session). `04_protocol.tex` says the difference is "attributable to bearing overlap alone"; §7 and §9
  concede otherwise. a_leaky − a_oracle compares different bearing sets, so it is not "carried by the source
  representation" (S04 222 %, fold A 101 % show this).
- You already have the fix: across ten splits each bearing is sometimes seen, sometimes unseen. Within-bearing seen −
  unseen accuracy: median 38.7 pp, 14/17 positive, 3 ties, none negative (`numbers_audit.md` Q8; caveat: different
  adaptation batches). Make this the primary inferential analysis (bearing as unit) and rename Eq. 1's second term
  ("not recovered by the oracle filter").
- Add a per-bearing table: manufacturer, damage mechanism and extent (Lessmeier Table 5), seen/unseen accuracy,
  gate certification count. It serves M3, M4 and M6 at once.

### M5. Provenance: the fold and gating jobs trained *different source models*  [verified]
- Same task, fold A, A2→A3 (`adapt_21.log`): pre-update accuracy **36.18 %** in `physgate-m1-fa` vs **44.37 %** in
  `physgate-m2-fa`; across fold A tasks up to 9.3 pp apart. Source pretraining logs diverge from epoch 6.
- This contradicts: Fig. 1 caption ("Gated and oracle arms reuse the same source checkpoint" — false for folds); the
  §4 diagnosis that the extra loader pass changed the post-pretraining trajectory only; "arms are never crossed between
  jobs" (§4) and "no reported comparison crosses jobs" (§9). Table 3's fold-A "Recoverable 101 %" uses leaky from the
  fold job and oracle/clean from the gating job (the gating job has **no leaky arm**); `results/c88/C88_RESULT.md`
  reports 106 % for the same cell.
- Graphical abstract mixes jobs and seeds: 94 %/57 % (fold job), 63 % (≈ gating-job clean 56.0 + three-seed mean gain
  7.05), 83 % (fold oracle, seed 2024). Subtitle "two rigs, 16 splits, two methods" implies they summarise everything.
- **Do:** either remove the fold rows from the decomposition (use the ten splits, where all arms share a job) or run the
  leaky arm inside the gating job; rewrite the cross-job paragraph ("different source checkpoints"); rebuild the
  graphical abstract from ten-split medians. Move the cross-job story (currently told four times) to the supplement.

### M6. Physics-gate claims: coverage–gain is near-mechanical, needs labels, and the detector limits coverage
- No spillover: certified windows gain a median 47 pp; uncovered faulty windows +0.33 pp (S00 −4.4, S09 −3.1)
  (`numbers_audit.md` Q9). With transductive SFDA evaluation, gain ≈ coverage × fix on covered windows, so ρ = 0.95 is
  largely built in. Say so; report gain on certified vs uncertified windows.
- "Computable from the target recordings alone" is false: coverage = fault verdicts on *faulty* recordings / number of
  faulty recordings (labels). A label-free version (share of all target recordings) gives ρ = 0.93 — use it. Partial
  correlations use a non-standard residual method (textbook partial Spearman: 0.932 and 0.043). Coverage is driven by
  four bearings (KA04, KA16, KI16, KI18) shared across splits.
- Raw-spectrum rule "lowers accuracy by 3.9 points" (no table) is the seed-2024 fold mean of **+5.35 (fold A)** and
  **−13.21 (fold B)**, positive on 6/12 tasks, never run on splits. "False acceptance predicted the sign of the effect in
  every case we tested" (§8 item 6) is not supported (also S03's −1.5 with the 1/480 gate). Report it in Table 6.
- Detector, not data (MSSP will press): the envelope rule has no band selection or pre-whitening; z is defined as a
  median-normalised ratio in §5 but a "robust z-score" in §6.6; the ±2 % slip window is >2× the largest measured slip;
  "unmistakable line" is undefined; Fig. 5a saturates at 373. Delete "coverage and the filter ceiling … are properties of
  the data" or benchmark per-bearing detectability with a standard pipeline (CPW + kurtogram + SES, Smith & Randall
  style) against damage extent/mechanism.
- Naming: PCTL's PCV is a continuous score on the *predicted* envelope spectrum used to supervise a confidence predictor
  with labelled target data — PCTL does not filter pseudo-labels (`01_introduction.tex` ¶5 and `02_background.tex` are
  wrong). Rename "PCV-style" or add a caveat.

### M7. The oracle is called a bound more strongly than shown
- Fig. 1 "oracle filter (upper bound)"; Intro item 3 "bounds every pseudo-label filter, physical or statistical";
  Conclusions/cover letter "the remainder … is beyond any filter". Adaptation is non-convex; withholding some correct
  labels (class rebalancing, curriculum) can beat keep-all-correct, and the oracle trains on true labels of the very
  windows it is scored on. §6.4 is already careful — propagate its wording everywhere ("oracle reference"), and state what
  happens to withheld windows (do they enter SDALR's entropy term?).

### M8. Statistics
- Splits share bearings (KA16 in 8/10 sources); sign-flip exchangeability is violated, and inference is conditional on
  this 17-bearing pool. Say so in the abstract-level claims and lean on the bearing-level analysis (M4).
- The protocol promises cluster-bootstrap intervals for every primary effect; **none appear in the manuscript**. They
  exist in artifacts for the mean only (e.g. ten-split collapse 38.17 [27.81, 48.43]; gate gain 7.82 [3.30, 13.07]).
  Report median CIs; give bearing-cluster CIs for 0/480, 1/480, 9/480 (6 healthy bearings).
- Table 3 note names the test "one-sided Wilcoxon", the text "cluster-level permutation"; pick one per effect.
- IQR "68–90 %" uses a non-default quantile rule (numpy default 70–90) — state it.
- Remove false precision: p < 10⁻²⁰⁰, p = 1.5×10⁻⁶, "agree to 0.000 points".

---

## MINOR revisions (factual — each checked)
1. Table 1 Paderborn "4 (2 used)" → three for adaptation, four for gates/slip (hard-coded in `make_tables.py::t1_datasets`).
2. Table 1 CWRU f_s: normal baselines (files 97–100) are 48 kHz; fault data 12 kHz. JNU "3 speeds" needs a footnote (Li 2013 describes 400–800 rpm variation).
3. `06_results.tex` KA04 purity "1.00 to 0.56" vs Fig. 3 data 0.711 (KA16 0.512); 0.56 is a single-task value — say so or use 0.71.
4. Probe recording count 1080 → 1020; 508/572 → 508/512.
5. Code availability says methods run from authors' released code, unmodified; SHOT is `runners/shot_patch.py` (own implementation) and gates modify the pseudo-label step.
6. `04_protocol.tex` "preprocessed archive is not publicly available" — SDALR README links it (Baidu Netdisk). Reword. Check SDALR numbers (96.78, 98.50, 97.84, 87.03) against the Neurocomputing VoR, not only arXiv v1.
7. Vieira survey: the 18th paper is "Not detailed" ([35]) — add "and one did not state its split". "100 evaluation splits" belongs to their leakage-free runs; the leakage inflation used 20/20/12 splits on three datasets.
8. Uncited claim: "Published audits of SFDA stability … collapse under industrial noise" (`02_background.tex`) — cite (Boudiaf/Zhao ICML 2023) or delete.
9. Wheat et al. "change method rankings" — not supported by the abstract; find the sentence or soften.
10. Patent US 10,168,248 separates lines by synchronous averaging, not spectral resolution — reword or drop (recommended: drop).
11. UORED is listed in the slip measurement (`03_data.tex`) and excluded from it (`09_limitations.tex`).
12. Slip: median 0.06 % is below the estimator's validated 0.17 % (masked arm 0.28 %); 90/304 (30 %) slips are negative (IBU/MTK min −1.00 %, FAG 35/52), one at +4.07 % outside the ±2 % search; synthetic validation has 15 of 20 cases. Negative "slip" signals geometry/contact-angle/speed error — discuss, and consider moving §6.8 to the supplement (it is off-thesis).
13. C104 pitting 64 % / plastic 23 % medians include the two folds (ten splits alone: 64.7 % / 22.6 %). C104 uses balanced accuracy, the 22.7-pp comparison plain accuracy — state it.
14. Highlight 2 ("…and at a fixed operating condition") follows an SFDA highlight but the fixed-condition result is forest-only.
15. "The gates that are safe … median 4.5 points over the ten splits" — only the envelope gate ran on the splits; "in every seed and in 9 of 10 splits" — splits are single-seed.
16. Conclusions: "share of target recordings … a median 24 %" — it is of *faulty* target recordings (15.2 % of all).
17. "22–41 points" (§7, §8) excludes SHOT's 21.7 median.
18. Fig. 5b labels S01 while the caption discusses S03; Fig. 6 vertical bars undefined (task-level bootstrap — declare or replace with cluster CI); Fig. 2 fold rows mix jobs (see M5); Fig. 1 says "3 healthy, 3 inner, 3 outer" and "same 12 tasks" (fold B is 3/2/3; splits have 60 tasks).
19. Eq. (1) ends with a comma followed by a new sentence.
20. Bibliography: benjamini1995 DOI → 10.1111/j.2517-6161.1995.tb02031.x; li2018ciddg pages 647–663; lessmeier2016 add DOI 10.36001/phme.2016.v3i1.1577, vol. 3(1), remove "05--08 July" from pages; borghesani2013 add issue 1.
21. Matania 2024 concerns bearing fault classification specifically, not "condition-based maintenance generally".
22. Bio-SFDA features include envelope peak counts — "raw rather than envelope" describes your implementation, not theirs (already caveated; tighten).

## Journal compliance (MSSP Guide for Authors, checked live)
- Abstract 246 words from source, 254 in the compiled PDF → cut to ≤235; define SDALR and SHOT or drop the acronyms.
- MSSP is an "Option C" data journal: deposit data/code at submission (private reviewer link is fine) and cite it as a `[dataset]` reference; "DOI on acceptance" does not meet it. Reconcile `data_availability.md` with the tex (JNU missing in tex).
- Highlights must be a separate editable file (all five are ≤85 characters: 74/82/74/72/70).
- AI declaration: use the current title ("…in the manuscript preparation process"), give model name/version/developer in Methods; caption disclosure for script-drawn schematics (Fig. 1, graphical abstract).
- Competing-interest declaration via Elsevier's tool (.docx); authors/CRediT/ORCID still placeholders.
- `rpm` → add Hz; LTWA journal abbreviations.
- MSSP's *Guidelines for ML papers* (Dec 2024) and *Signal Processing guidelines*: frame the contribution as "increase of knowledge" (measured mechanism, ceiling, gate safety), not "the novelty is narrow… we claim no new…". Keep the honesty, change the emphasis.
- Cover letter: remove reviewer table and internal note; fix the Vieira "out of scope" sentence; state article type.
- Suggested reviewers: Silva (Vieira) and Dumond (Hendriks, UORED) are interested parties; keep at most one.

## Presentation
- ~24 pages, ~300 numbers; abstract carries ~20 numbers. Aim for 5–6 in the abstract.
- Move to supplement: §6.8 slip and 6203 lock, §2.5, the A/A and cross-job narrative, most of the multiplicity discussion, the off-rig z = 40 detour.
- Replace jargon ("speak on", "certify", "engages", "honest test") with neutral terms; reduce defensive asides.
- Add the per-bearing table (M4) and replace Fig. 3 with seen-vs-unseen accuracy per bearing.

---

## Revision plan, by cost
**Tier 1 — text and existing artifacts only (do first):** M1 source-only arm; M4 within-bearing analysis; M5 provenance
rewrite + graphical abstract; M6 spillover split, label-free coverage, raw-spectrum into Table 6; M7 wording; M8 CIs;
M2 novelty rewrite + citations; all minors; compliance items.
**Tier 2 — CPU (Kaggle CPU kernels):** forest learning curve over bearings/class; probe ablations; nearest-source-bearing
test; order-domain envelope classifier on full records; standard SES detectability per bearing.
**Tier 3 — GPU (optional, strengthens):** leaky arm inside the gating job; SDALR/SHOT at fixed condition; one
neighbourhood SFDA method (AaD) on the ten splits.
