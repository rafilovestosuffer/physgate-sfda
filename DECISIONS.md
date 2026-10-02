# DECISIONS

Every choice that could move a headline number is logged here with the value before and after.
Research judgments made on the researcher's behalf are marked **[delegated]** and are open to reversal.

## Calendar (hard dates)

| Milestone | Date |
|---|---|
| Sessions 0–1 | 2026-09-20 |
| M0 + M1 (Sessions 2–5) | 2026-10-04 |
| **Hard preprint deadline — whatever M1 says** | **2026-10-18** |
| M2–M5 (Sessions 6–10) | 2026-11-01 |
| Full matrix (Sessions 11–12) | 2026-11-22 |
| **Target submission** | **December 2026** (MSSP primary, RESS secondary — C67) |

## Log

| Date | Decision | Before → after | Basis | Status |
|---|---|---|---|---|
| 2026-09-13 | Introduction framing | "99.0% vs F1 0.47 cannot both be true" → within-task question | Session 0: different datasets and taxonomy (C20) | adopted |
| 2026-09-13 | Track A window | 2.0 s → **3.0 s** | feasibility: PU N09 marginal at 2.0 s (C21). Shorter window would have gained samples at the cost of resolution — rejected for that reason | adopted |
| 2026-09-13 | FTF role | decision family → context channel | no cage class in L3/L4 (C22) | adopted |
| 2026-09-13 | Gate null | Gamma(N,1) + median floor → **CA-CFAR F(2n,2m), ref 25 Hz, guard 2 Hz** | null-only MC: 0.074 → 0.049–0.055 realised at nominal 0.05 (C24) | adopted |
| 2026-09-13 | Kinematics table tolerance | KICKOFF atol 1e-4 race lines → **2e-4**; ball 5e-4 unchanged | measured worst deviation vs CWRU's 4-dp table: 1.19e-4 (6203 BPFO) | adopted |
| 2026-09-13 | Venue | RESS primary retained | user named an unrecognised venue ("ASUARI Kiwan"); awaiting clarification | **[delegated]** |
| 2026-09-13 | Pre-registered constants `s_max=0.02, K=5, J=2, M=9, T_A=3.0 s`, 1 segment / no Welch, CA-CFAR ref 25 Hz / guard 2 Hz, α=0.05 | proposed -> **frozen** | Researcher's blanket authorisation of 2026-09-13 ("do everything, all permission given"). Frozen in git BEFORE any gate result on real data; see commit containing C28. | **[delegated]** — reversible only by a logged §13 entry |
| 2026-09-13 | **Rev 6 reconciliation** — external audit (PROGRAMME_REV6, SESSION_2, BLOCKED_ITEMS) plus full texts of Bio-SFDA, Rong & Lee, Li 2013, Sun & Gao 2024, Jeong 2025 | audit C27–C41 → our **C35–C51** (renumbered; audit numbers collided with ours) | every audit claim checked against a primary source before adoption; two rejected (UORED "gate day one"; HUST "softened") | **[delegated]** |
| 2026-09-13 | PU kinematics | CWRU SKF 6203 for all PU → **per bearing from PU profile PDFs** (Pd 29.05 × 26, 28.55 × 6) | C35. BPFO 3.0531 → 3.0706 (IBU/MTK), 3.0543 (FAG) | adopted |
| 2026-09-13 | H6 | one pre-registered run → **pre-registered run (reported as run) + corrected-geometry run, both reported** | C35: geometry error found in primary documentation, outcome-blind | adopted |
| 2026-09-13 | Track A window | T_A 3.0 s / step 1.0 s **retained** after the sample-count sweep | C37: 480 ≥ 250 training windows in the smallest class; 3.0 s / 50 % would give 240 and fail | adopted |
| 2026-09-13 | Claim order | leakage protocol first → **gate first, stratification second, leakage-safe SFDA evaluation third** | C39 | **[delegated]** |
| 2026-09-13 | Bio-SFDA | planned baseline/comparator → **cited for mechanism only; no numeric comparison** | C49 | adopted |
| 2026-09-13 | UORED | not in roster → **target + gate evaluation only**, gate blocked until NSK/FAFNIR geometry verified | C42, C51 | adopted |
| 2026-09-13 | Ladder input | undeclared → **all rungs at T_A; L0 full raw window, disadvantage stated** | C47 | **[delegated]** |
| 2026-09-13 | Preprint scope | "whatever M1 says" → **methods + calibration note incl. completed pre-registered gate results**; date unmoved | C48 | **[delegated]** |
| 2026-09-13 | Prior-art sweep (C50) | sweep #1 logged: no source-free + calibrated-gate + leakage-safe competitor found; He et al. EAAI 2026 is nearest SFDA cross-machine neighbour | next sweep due at session +3 | logged |
| 2026-09-13 | JNU | Z unknown → **Z 10/11 primary (Li 2013), Pd unpublished → still blocked; Track R only** | C45 | adopted |
| 2026-09-13 | External calibration memo | adopted as written → **checked against Vieira v2: survey counts and PU subset correct; "+6.4 % envelope inflation" false (frequency-domain); Table 7 is tuning-optimistic; anchors taken from Tables 8–10** | C57 | adopted |
| 2026-09-13 | Backbone / variance / tuning | resnet18_1d only, 5 seeds, no tuning protocol → **+WDCNN (L0/L2.5/L5/H9); K ≥ 10 bearing-level splits with seeds nested; source-side CVM-CV** | C60–C62 | adopted |
| 2026-09-13 | H9 | not in plan → **pre-registered, motivation corrected** | C59 | adopted |
| 2026-09-13 | Claim 1 after H7 | "test beats rules" → **evaluation of physics gating by realised FA; PCV-style rule co-reported everywhere** | C65: PCV-style 0.994 / 1 FA vs comb 0.955 / 9 FA; EAGLE-style 214/480 FA | **[delegated]** |
| 2026-09-13 | Memo's "do not choose T_A / three signatures required" | wait for researcher → **decided under the researcher's standing instruction ("make your own decision for every step")**; each marked [delegated] and reversible | C37, C39, C48 | **[delegated]** |
| 2026-09-13 | Memo T3 "paste BLOCKED_ITEMS fragment verbatim" | → **not pasted**: its NTN numbers conflict with our NTN reading and with Li 2013; primary Z/Dw recorded instead; UORED geometry found in the dataset article (C54), contradicting "unpublished" | C45, C54 | adopted |
| 2026-09-13 | KNEOS-HC novelty | architecture claim → **withdrawn; L4 = Matania-style features; L4m faithful rung added** | C66, Matania public code | adopted |
| 2026-09-13 | Venue | RESS primary → **MSSP primary, RESS secondary** | C67 | **[delegated]** |
| 2026-09-13 | UORED speed | C68 spectral → C69 logged → **C70 unresolved, both arms, no primary; H8 inconclusive** | shaft-harmonic lines mistaken for fault lines in C69 | adopted |
| 2026-09-13 | Reviewer mechanism (BPFI k3 → BPFO k5; K = 3 fix) | proposed → **checked; corrected to integer-shaft snapping + sparse-comb arbitration (C71); K = 3 prediction not adopted** | code-level diagnostics: BPFO excess 6.7–13.3 from 5 shared lines vs BPFI 2.8–4.4 from 25 | adopted |
| 2026-09-13 | comb_v2 | — → **pre-registered co-reported variant (C72); synthetic null FAR 0/36 cells** | dropped if PU healthy FA > 9/480 | adopted |
| 2026-09-13 | Open item: identity of the ~29.6 Hz UORED line / true shaft speed | — → **ask dataset authors (Sehri, Dumond, uOttawa) for Hall-logging method and a tachometer trace**; working hypothesis (not claimed): it is the true shaft rate of the 4-pole motor | C70 | human (optional email) |
| 2026-09-15 | Scope | open-ended experiment plan → **freeze: C83 seeds only; ladder/H1/H4/H5/H9/full matrix deferred; start manuscript** | C84 | **[delegated]** |
| 2026-09-15 | Supervisor review (C86 fatal flaw) | C86 unconditional bearing adversary → **withdrawn unrun; BIST-W class-conditional + N1 decodability control first (C87)** | Y = g(B) ⇒ Z⊥B forces Z⊥Y; verified Liu et al. 2107.13469 Thm 2 discussion; nearest neighbour CIDDG (Li et al. ECCV 2018) | adopted |
| 2026-09-15 | Two folds insufficient | 2 folds → **+10 random 3/3/3 splits (C88), split = unit, ≈24 GPU-h over both accounts** | Vieira used 100 splits; Wilcoxon floor | adopted |
| 2026-09-15 | Gating comparison paired? | unstated → **verified paired from logs; per-task paired differences reported (C89)** | identical batch-0 accuracy; worst task −0.08 pp | adopted |
| 2026-09-15 | Decomposition in abstract | supervisor 69/31 (mixed variants) → **matched-variant 70/30 on folds, but fold A 101 % vs fold B 48 %: abstract carries the C88 distribution, not one number** | results/PAIRED_GATING.md; c88_eval M1 rows | adopted |
| 2026-09-15 | Slip proposition | subsection → **remark: measured slip ≈ 0.1 %, lock bracket [0, 0.99 %] (C90, pre-registered rule)**; "within normal slip" withdrawn | results/c90 | adopted |
| 2026-09-15 | Manuscript structure | 6 parallel contributions → **v0.2 single thread; gate ROC → S2; hygiene → S3; title owns single-rig scope** | supervisor review | adopted |
| 2026-09-15 | Bio-SFDA right of reply | draft → **send before submission, wording "the mechanism as described, as we implemented it"** | supervisor; the user cannot send email — supervisor/co-author to send | human |
| 2026-09-19 | Reference he2026 (EAAI 166:113585) | cited → **removed**: title/authors could not be verified on the publisher page or any index | rule 8 integrity: no unverifiable citation enters the manuscript; the sentence was not load-bearing | adopted |
| 2026-09-20 | Submission source format | Word vs LaTeX → **LaTeX (elsarticle, elsarticle-num numbered references)** | MSSP accepts .tex or .docx only; user chose LaTeX. No local TeX toolchain: structural validation here, one Overleaf compile by the user | **[user]** |
| 2026-09-20 | Bio-SFDA right of reply | draft email on file → **not sent; named in the paper without prior contact** | user decision. Mitigation: wording stays "the mechanism as described, as we implemented it", no comparison against their reported accuracy, their Paderborn task definition stated as unreconstructable | **[user]** |
| 2026-09-20 | Preprint (supersedes C48's 2026-10-18 hard preprint deadline) | arXiv/SSRN preprint → **no preprint; journal submission only** | user decision; accepted risk of no priority timestamp in a crowded 2026 leakage literature | **[user]** |
| 2026-09-22 | Review round 2: coverage vs the ceiling argument | "gates act on about a quarter of the faulty bearings" → **in-loop, per-record coverage (C98): median 24 % of a clean target's faulty recordings, median 2 of 5 faulty target bearings; the ceiling paragraph is rebuilt around the measured coverage-gain correlation (Spearman rho = 0.95, p = 2e-5, split-level)** | The reviewer showed the bearing count (7/11 over four conditions) did not support the claim. The loop vetoes per record, and at the three adaptation conditions only 4 of 11 real-damage bearings carry more than one certified recording | adopted |
| 2026-09-22 | Review round 2: source-free premise | caveat sentence → **off-rig calibration measured (C99): the pre-registered z = 10 accepts 4 of 24 healthy UORED/CWRU recordings; zero off-rig false acceptance needs z = 37.5; transferred to Paderborn that point keeps 333 of 366 fault verdicts and improves healthy FA to 0/480** | Answering an objection with a measurement beats answering it with a disclaimer, even when the measurement is unflattering. Adaptation was NOT re-run at z = 40, and the manuscript says so | adopted |
| 2026-09-22 | Review round 2: probe interpretation | "bearing-identity memorisation" → **"bearing-identity shortcuts"; identity is present in the raw signal (508/508 from ten time statistics), not learned** | The handcrafted-feature probe beats the learned one, so a representation-level remedy does not address the root cause. Title, abstract, Section 6.7 and the conclusions changed together; session/mounting confound named | adopted |
| 2026-09-22 | Review round 2: fold-level p-values | reported throughout → **removed from the abstract, Section 6.6, Table 4 and Table 6; split-level tests carry all inference** | C96's two-cluster floor of p = 0.25 makes them meaningless. Random forests moved to ten splits from existing artifacts (C101); SHOT on ten splits pre-registered and run (C100) | adopted |
| 2026-09-22 | Review round 2: HUST sensitivity gate run | reviewer's optional suggestion → **not run** | The 0.58 % estimate error is indeed inside the +-2 % slip window, but the rule against estimated geometry is what makes every other kinematic number auditable; recorded in Limitations as the route for a follow-up | adopted |
| 2026-09-29 | Cross-job gap (C103) | "pretraining state" hypothesis → **rejected (0.000 pp); probable cause from code: evaluation wrapper of `d9ad845` advances the torch RNG (post-hoc, not isolated by a run)** | C103 pre-registered rule; CPU check of DataLoader seed draw; gap 1.6 pp inside the 3.2 pp between-seed range of the ungated fold-A mean | adopted |
| 2026-09-29 | C100 SHOT on splits | 8 of 10 splits → **10 of 10 (g3 pulled): median 21.7 pp, positive 10/10, sign-flip p = 0.001 → GENERALISES**; Table 4 and Section 6.3 carry the split result; BH family recomputed (collapse 0.002, gate 0.005, RF 0.002, HUST 0.023, SHOT 0.002) | pre-registered C100 rule; 120 ledger rows appended with verified account attribution (g1/g3 co-author, g2/g4 primary) | adopted |
| 2026-09-29 | A/A floor (C102) | fold A only, 18 pairs → **all retained executions: 11 arm pairs, 66 tasks, both folds, all 0.00 pp**; the ratio-to-zero table withdrawn and replaced by the between-seed range | the original gating job and the C103 arms are further executions of the same configuration | adopted |
| 2026-09-29 | C99 off-rig threshold | manuscript z = 37.5 → **z = 36 (the calibration minimum); Paderborn transfer stated at z = 40, the nearest sweep point >= 36**; C99 script's inverted "more permissive" clause fixed, transfer written into C99_RESULT.md | the 37.5 was a table row, not z*; the checker's substring match had let it pass, now tightened | adopted |
| 2026-09-29 | Review round 4, major 3 (identity vs condition) | "same-condition control not run" (Limitations) → **run as pre-registered C104: median 29.7 pp same-condition collapse, 10/10, p = 0.001; identity claim kept and strengthened; recording-level separation shown to leave the leak in place** | cheapest decisive experiment; CPU only; leakage sanity checks passed (disjoint bearings, disjoint record halves) | adopted |
| 2026-09-29 | Review round 4, verified independently | survey: reviewer said the 18-paper table may not be in Vieira → **it is (Vieira Table 1, arXiv v5); but our text said six at 100 % where v5 has five, and omitted that the 18 are supervised papers: both fixed**; Vieira "out of scope" → **not in their text; rewritten to their own sentence (single testbench)**; BH citation → **BH 1995 added for the procedure, BY 2001 kept for validity under positive dependence**; SDALR PU → **8 classes, one bearing per class: stated in 6.1 and 2.2** | primary sources read 2026-09-29 | adopted |
| 2026-09-29 | Review round 5 (source-check report) | reviewed a stale PDF (built 14:03Z, pre-round-4); its BY objection assumed HUST at rank 1 → **HUST is rank 7 of 10: BY = (1/64)*10*2.929/7 = 0.0654, recomputed with exact fractions; printed values stand** | exact recomputation | adopted |
| 2026-09-29 | C104 wording | "the loss is carried by bearing identity" → **specimen-level damage signature; post-hoc C104b: inner race (one mechanism) drops 28.5 pp, outer race 66 pp, healthy 1.7 pp; session not crossed; RF-only, SFDA not run at fixed condition (limitation)** | reviewer correct that the control does not separate specimen from mechanism | adopted |
| 2026-09-29 | Bio-SFDA caveat | threshold rescaling attributed to the EAGLE module only → **both: band thresholds rescaled online (p. 6), and SPIDER applies bounded factors to them and adjusts acceptance thresholds tau_s, tau_w** | full text on disk read; reviewer had the abstract only | adopted |
| 2026-09-29 | Damage labels | "datasheets' own descriptions; ISO mapping is our reading" → **Lessmeier et al. 2016 Table 5 cited; ISO 15243 clauses 5.1 and 5.5** | dataset paper and ISO table of contents read | adopted |
