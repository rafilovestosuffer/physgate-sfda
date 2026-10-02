i got a deeep reseearch report of our paper, make deep research on everything from here , deep research y yourself


Peer-Review Report — "Bearing-wise evaluation of source-free domain adaptation: leakage, bearing-identity memorisation and the ceiling of physics-gated pseudo-labels"

(Target venue: Mechanical Systems and Signal Processing, Elsevier. Anonymous preprint dated 21 Sept 2026.)

1. Summary of the paper

The manuscript is a critical re-evaluation of a published source-free domain-adaptation (SFDA) method for cross-condition bearing fault diagnosis (SDALR). Using a paired experimental design in which only bearing overlap between source and target changes, the authors show that "bearing-disjoint" targets (physically different bearings at the target condition) collapse accuracy relative to "leaky" targets (the same physical bearings at the target condition). On Paderborn, mean accuracy falls from 94.1% to ~56% across two mechanical folds and by a median of 36.2 percentage points over ten pre-registered random bearing splits; a comparable collapse is reproduced on the HUST dataset, for the SHOT method, and against a non-adaptive random forest that outperforms the adapted model on bearing-disjoint targets. A logistic-regression probe on frozen source features recovers individual bearing identity within a class in 507/508 held-out recordings, supporting a "bearing-identity memorisation" interpretation. An oracle pseudo-label filter recovers a median 82% of the collapse (argued to bound keep/withhold filters), and physics-based kinematic envelope gates add 4–7 points in paired comparisons while a raw-spectrum band rule (an EAGLE/Bio-SFDA-style mechanism) lowers accuracy. The authors state they introduce no new network or algorithm and position the work as an evaluation-methodology contribution.

2. Overall assessment and recommendation

Recommendation: Major revision. The central scientific contribution — demonstrating, with a clean paired design and a persuasive memorisation probe, that cross-condition SFDA gains on these benchmarks are substantially an artefact of same-bearing overlap — is timely, well-motivated, and largely convincing. The external literature and dataset facts check out well, and the statistical scaffolding (pre-registered splits, distributional reporting, oracle decomposition) is above the norm for the field. However, several concrete problems must be resolved before acceptance: (i) an internal inconsistency in the headline "clean" accuracy and collapse magnitude (56.8%/37.3 pp vs 56.05%/38.1 pp); (ii) figure/text numeric mismatches (KA04 purity, S04 recoverable share); (iii) a source-free-premise tension in how the physics gates' operating points are selected on labelled target-rig recordings; (iv) statistical pseudo-replication when treating 12 fold-tasks that share source checkpoints as independent; (v) an under-justified decision to omit HUST gating on the grounds that geometry is "unavailable," when HUST characteristic fault orders are in fact published; and (vi) citation errors. None of these appears fatal to the main claim, but collectively they require substantial revision and re-checking.

3. Strengths
Important, well-posed question. The paper isolates a specific and consequential confound (bearing identity vs. operating condition) with a paired "only bearing overlap changes" design, which is cleaner than most leakage critiques.
Convergent evidence. The collapse replicates across two datasets (Paderborn, HUST), two SFDA methods (SDALR, SHOT), mechanical and random splits, and is corroborated by a direct memorisation probe and a non-adaptive baseline. This triangulation is a genuine strength.
Above-average statistical hygiene. Pre-registered random splits with a version-controlled seed, distributional reporting over splits rather than single numbers, one-sided Wilcoxon signed-rank tests with exact small-sample p-values, and a transparent oracle decomposition of "recoverable" vs. "non-recoverable" collapse.
Physics grounding. The kinematic envelope gates are tied to documented bearing geometry and characteristic orders, and the authors honestly report that their raw-spectrum band rule (a re-implementation of the Bio-SFDA/EAGLE mechanism) hurts accuracy — a candid negative result.
Reproducibility posture. Code availability, explicit configuration inheritance from SDALR, and a fixed seed are all commendable.
4. Major concerns
Inconsistent headline "clean" accuracy and collapse magnitude (numerical error). Issue: Table 3 reports fold-A clean = 56.8% and fold-B clean = 55.3%, whose mean is 56.05%; Section 6.5 correctly uses ~56.0% and a 38.1-pp collapse. But the abstract, highlights ("37 points"), Section 6.2, Table 4, and the conclusions use 56.8% clean and a 37.3-pp collapse — i.e., fold A's value alone. The leaky side is averaged correctly ((88.3+99.9)/2 = 94.1), so the clean side should be 56.05%, not 56.8%. Where: Abstract, Highlights, Table 3 footer, Sections 6.2/6.5, Table 4, Conclusions. Why it matters: This is the paper's headline number; two different collapse magnitudes circulate through the manuscript. Action: Recompute and reconcile to a single pooled definition (state explicitly whether "94.1 vs X" is the 12-task pooled mean or the mean of two fold means), and correct every downstream instance including the highlight.
Source-free premise vs. gate calibration on labelled target-rig data. Issue: Gate operating points (e.g., envelope z-threshold, comb α) are selected by false-acceptance on 480 real healthy Paderborn recordings — the same rig and including target bearings — which injects target-domain label information and is chosen on data also used for evaluation. Where: Section 6.6, Table 6; Gates description in Section 5. Why it matters: It weakens the "strict source-free" framing and risks optimistic gate gains. Action: Select thresholds on a held-out rig/dataset or purely from geometry/first principles; report sensitivity to the operating point; separate calibration from evaluation recordings.
Gate characterisation population is mis-described and mixes artificial with real damage. Issue: Table 1 implies only real-damage bearings (5 outer + 6 inner) are used, but the Table 6 population of 2,319 recordings = 480 healthy (6×4×20) + 1,839 faulty resolves to 23 faulty bearings × 4 conditions × 20 − 1 unreadable file (the known corrupt N15_M01_F10_KA08_2.mat). Thus 23 = 11 real + 12 artificial-damage bearings, and all four operating conditions are used for gating even though only three are used for adaptation. Where: Table 1 ("4 (2 used)"), Table 6, Section 6.6 ("6 of 23 faulty bearings"). Why it matters: Gate false-acceptance/coverage is characterised partly on artificial-damage bearings that are not the ones used in adaptation; coverage on the real-damage adaptation bearings is left unknown. Action: State the population explicitly, separate artificial vs. real damage, and report gate coverage specifically on the real-damage bearings used in the transfer experiments.
Statistical pseudo-replication and absent multiplicity control. Issue: Within each fold, the 12 tasks share source checkpoints (each source model serves two targets) and bearing sets; treating them as independent units in the Wilcoxon test inflates significance. No multiple-comparison correction is applied across the many paired tests. Where: Section 5 (statistics), Tables 4, 7. Why it matters: Reported p-values (e.g., 2⁻¹² = 0.00024) overstate evidence. Action: Use a clustered/hierarchical test or treat the fold (not the task) as the unit; or bootstrap at the bearing-cluster level as done elsewhere in the paper; report corrected p-values.
Figure/text numeric mismatches that touch interpretation. Issue: (a) Fig. 3(b) shows KA04 gated purity 0.71 while Section 6.6 text says it falls to 0.56; (b) Fig. 4 labels S04 recoverable as "100%" while Table 3 lists 222% — which is arithmetically correct given the decomposition ((92.1−74.0)/(82.2−74.0)=221%), meaning the oracle can exceed leaky and the "recoverable share" can exceed 100%. Where: Figs 3–4, Sections 6.4–6.6. Why it matters: The >100% case directly undermines the "oracle bounds any pseudo-label filter" language for at least one split, and the purity discrepancy affects the case study. Action: Reconcile figure and text; either cap and explain, or drop the "bound" phrasing where negative decomposition terms occur.
Over-claim: "the strongest lever is the number of distinct source bearings." Issue: This causal-sounding claim is asserted (with reference to Vieira et al.) but not tested with a scaling experiment in this manuscript. Vieira et al. (MSSP 258, 2026, 114640) do report that "the number of unique training bearings is a decisive factor for achieving robust performance," 
arxiv
 so the claim is defensible as attributed prior work but not as a finding of this paper. Where: Discussion/Section 8. Why it matters: It reads as an empirical finding of the paper. Action: Either run a source-bearing-count scaling study or explicitly attribute the claim to Vieira et al. and downgrade to a hypothesis.
HUST gating omitted on questionable grounds. Issue: The authors state HUST pitch diameter is unavailable so no HUST gating is done; however, the HUST source publication (Thuan & Hong, BMC Research Notes 16(1):138, 2023) tabulates per-type bearing dimensions (inner/outer/ball diameters, ball count) and the characteristic fault orders — e.g., for the 6204 the outer-race ratio is 3.093× and inner-race 4.907× shaft speed 
arxiv
 — that are exactly what an envelope gate needs. Where: Datasets/Kinematics section. Why it matters: A physics gate on HUST would materially strengthen the generality claim and is apparently feasible. Action: Either implement HUST gating using the published orders or correct the justification for its omission.
5. Minor concerns
Rounding-level inconsistencies: RF 64-band collapse stated as 40.7 in text vs 40.6 in Table 4 (93.2−52.6=40.6); RF envelope 76.7−43.1=33.6 vs 33.5; HUST H0 98.1−63.7=34.4 vs 34.5; S07 99.2−51.5=47.7 vs 47.8; S00 gain 69.7−66.5=3.2 vs 3.1. Standardise rounding and state that displayed values are rounded from higher-precision underlying numbers.
Fold-B clean accuracy: with purity 1.000 and one of three bearings correct per fault class plus all-correct healthy, the arithmetic gives 5/9 = 55.56%, close to but not exactly the reported 55.27–55.33%; the "one class right, two wrong" wording is confusing and should be rewritten (and the two-outer-bearing composition of fold B — only KA22/KA30 — noted).
"Target-label selection worth 1.0–2.0 points": Table 4 shows only 0.6 pp (leaky, 94.7 vs 94.1) and 1.0 pp (clean, 57.8 vs 56.8) differences; the 1.0–2.0 range is not traceable and should be corrected.
"Variance of the difference roughly half the variance of accuracies": (1.7/2.8)²≈0.37 and (2.4/2.8)²≈0.73; "roughly half" holds for only one seed set. Rephrase quantitatively.
Probe expected recording count: 3×90+3×80=510 versus 508 reported; explain the two missing recordings (likely the corrupt file and one other) and confirm whether probe test recordings were excluded from source training.
Probe lacks a baseline: report the same bearing-identification probe on raw/handcrafted features to show the effect is not merely session/mounting artefact.
Code-availability text refers to "three declared adapters described in Section 4," but only SDALR and SHOT are described (the random forest is not an adapter). Reconcile.
Pre-registration and Supplementary S1–S4 are not externally verifiable (no registry link/timestamp); provide a citable, timestamped registration.
Terminology: reviewers may reasonably contest whether same-bearing cross-condition transfer is "leakage" or simply a different (and legitimate) task definition (a new operating point of the same machine). Add a paragraph defending the terminology and distinguishing deployment scenarios (same machine re-instrumented vs. bearing replaced).
Reference [24] is a US patent used to support a claim about "industrial practice"; supplement with a peer-reviewed or standards source.
6. Internal numerical consistency audit
Claim location	Reported value	Recomputed / cross-checked value	Verdict
Number of 3/3/3 draws	4,000	C(6,3)·C(5,3)·C(6,3)=20·10·20=4,000	Correct
Fold leaky mean	94.1%	(88.3+99.9)/2=94.1	Correct
Fold clean mean (headline)	56.8%	(56.8+55.3)/2=56.05	Error — 56.8 is fold A only
Fold collapse (headline)	37.3 pp	94.1−56.05=38.05≈38.1 (as in §6.5)	Inconsistent (37.3 vs 38.1)
Median Δleak (10 splits)	36.2 pp	median of {8.2…61.6}=(35.2+37.2)/2=36.2	Correct
Median recoverable	82%	median of {48…222}=(79+85)/2=82	Correct
Gate gain median	+4.5	median of gains=(4.3+4.7)/2=4.5; 9/10 positive	Correct
p for 10/10 collapse	0.001	1/2¹⁰=1/1024≈0.00098	Correct
p for 9/10 gate gain	0.003	3/1024≈0.0029	Correct
p for 12/12 fold collapse	0.00024	1/2¹²=1/4096≈0.00024	Correct (but see Concern 4 re independence)
HUST 6/6 positive p	0.016	1/2⁶=1/64=0.0156	Correct
HUST median loss	33.5 pp	median{25.8,30.9,32.5,34.5,49.9,61.1}=33.5	Correct
HUST leaky/clean means	98.7 / 59.6	592.2/6=98.7; 357.6/6=59.6	Correct
Comb mean gain	+4.03	(3.79+4.56+3.73)/3=4.03	Correct
Envelope mean gain	+7.04/7.05	(7.44+7.99+5.70)/3=7.04	Correct
S04 recoverable	222% (Table 3) / 100% (Fig 4)	(92.1−74.0)/(82.2−74.0)=221%	Table 3 correct; Fig 4 mislabeled
RF 64-band collapse	40.7 (text) / 40.6 (Table 4)	93.2−52.6=40.6	Text off by 0.1
S07 Δleak	47.8	99.2−51.5=47.7	Rounding (−0.1)
KA04 gated purity	0.56 (text) / 0.71 (Fig 3b)	n/a	Figure/text mismatch
Gate population 2,319	480 healthy + 1,839 faulty	6×4×20=480; 23×4×20−1=1,839	Correct (implies 23 = 11 real + 12 artificial)
BPFO orders	3.0706 / 3.0543	4(1−6.75/29.05)=3.0706; 4(1−6.75/28.55)=3.0543	Correct arithmetically (3.0706 depends on unverified 29.05 mm)
Slip s*	2.30 / 1.78 / 1.74%	consistent with δ/BPFO₀ formulation	Plausible, not independently checked
6203 measurable recordings	304 = 242+52+10	242+52+10=304	Correct
7. Reference verification
Ref	As cited	Verified?	Discrepancies
[1]	Randall & Antoni, MSSP 25(2) 2011, 485–520, doi 10.1016/j.ymssp.2010.07.017	Yes	None
[2]	Zhao et al., IEEE TIM 70 (2021) 3525828	Not independently confirmed	Consistent with a known survey; verify article number
[3]	Liang, Hu, Feng, SHOT, ICML 2020	Yes	None (SHOT = Liang, Hu, Feng, ICML 2020)
[4]	"H. Wu, Y. Zhang, J. Wang," SDALR, Neurocomputing 657 (2025) 131661	Partly	Author list wrong: actual authors are Wenyi Wu, Songsong Wu, Hao Zhang, Zhisen Wei, Xiao-Yuan Jing, Qinghua Zhang 
SSRN
 (arXiv 2503.08749; SSRN listings). The "author initials as indexed by the publisher" note signals the authors know of a mismatch — fix it
[5]	Vieira et al., MSSP 258 (2026) 114640, arXiv 2509.22267, doi 10.1016/j.ymssp.2026.114640	Yes	Correct (journal ref Vol. 258, 2026, 114640, "To appear in MSSP"); the "18 papers in 2025" survey is present in the source (§3.3), which states leakage "persists in the majority of works"
[6]	Hendriks, Dumond, Knox, MSSP 169 (2022) 108732	Yes	None; claim (condition-wise split places same bearings in train/test) is accurate — the source argues that "the same physical bearings exist in both training and testing sets" 
ScienceDirect

[7]	Wheat et al., IEEE Access (2024), doi 10.1109/ACCESS.2024.3497716	Exists but malformed	No volume/article-number/pages; complete the citation
[8]	Bio-SFDA, Results in Engineering 30 (2026) 111105, doi 10.1016/j.rineng.2026.111105	Yes	Confirmed (Yoon et al., SKKU); the "EAGLE" module is "a physics-guided reliability functional that exploits BPFO/BPFI/BSF and impulsive-band activity to weight and gate pseudo-labels" 
Skku
 — matches the manuscript's description. Verify the specific ball-class-on-Paderborn claim against the paper's experiments
[9]	Jiao, Zhang, Cao, Eksploatacja i Niezawodnosc 28(2) (2026) 211797, doi 10.17531/ein/211797	Yes	Confirmed (PCTL / physics-guided consistency-verification framework); "small labelled target set" not independently verified
[10]	Borghesani et al., MSSP 40 (2013) 38–55	Not independently confirmed	Plausible; could not verify within budget
[11]	Matania et al., MSSP 224 (2025) 112117	Yes	doi 10.1016/j.ymssp.2024.112117; zero-fault-shot physics+ML hybrid, consistent
[12]	Li et al., ECCV 2018, 624–639	Yes	Confirmed pages 624–639 (LNCS 11219); title "Deep Domain Generalization via Conditional Invariant Adversarial Networks" 
Springer

[13]	Knap et al., PHM Society European Conf. Vol 9, 2026	Yes	doi 10.36001/phme.2026.v9i1.4924; six fixed source–target scenarios with recording-level separation on CWRU+Paderborn 
Phmsociety
 confirmed; code repo github.com/1Sensor/pdm-bench confirmed
[14]	Jeong, Kim, Seo, Kwon, Sensors 25(14) 2025 4383	Yes	doi 10.3390/s25144383; order-normalisation preprocessing + U-Net VAE + test-time training 
nih
 confirmed
[15]	Antoni, Fast kurtogram, MSSP 21(1) 2007 108–124	Yes (standard)	None
[16]	Liu et al., ICCV 2021, 10347–10356	Not independently confirmed	Plausible
[17]	Özdenizci et al., IEEE Access 8 (2020) 27074–27085	Not independently confirmed	Plausible
[18]	Lessmeier et al. (2016), venue missing	Incomplete	Add venue: European Conference of the PHM Society, Bilbao, 5–8 July 2016
[19]	Thuan, Hong, BMC Research Notes 16(1) 2023 138; data doi 10.17632/cbv7jyx4p9	Yes	doi 10.1186/s13104-023-06400-4; dataset facts (6204–6208, 0/200/400 W, 51.2 kHz, 10 s) 
Springer
 confirmed. Data DOI should include version (Mendeley V3 / .3)
[20]	Smith & Randall, MSSP 64–65 (2015) 100–131	Yes	Fan-end 6203 BPFO≈3.053× confirmed (source: "values of 4.947, 3.053 and 1.994 (×fr) for BPFI, BPFO and BSF"); 
ResearchGate
 near-integer-order behaviour supports the "lock-like" claim
[21]	Sehri, Dumond, Bouchard, Data in Brief 49 (2023) 109327	Yes	doi 10.1016/j.dib.2023.109327
[22]	Li et al., JNU, Sensors 13(6) 2013 8013–8041	Not independently confirmed	Plausible (JNU dataset paper)
[23]	Pedregosa et al., scikit-learn, JMLR 12 (2011) 2825–2830	Yes	None
[24]	US Patent 10,168,248 B1 (and 10,598,568 B1)	Exists	Inappropriate as sole support for "industrial practice"; add peer-reviewed/standards citation
8. Missing literature the authors should cite/discuss
Kapoor & Narayanan (2023), "Leakage and the reproducibility crisis in machine-learning-based science," Patterns 4(9):100804, doi 10.1016/j.patter.2023.100804 (published 8 Sept 2023). The definitive treatment: the survey "find[s] 17 fields where leakage has been found, collectively affecting 294 papers and, in some cases, leading to wildly overoptimistic conclusions," 
PubMed
 and introduces a taxonomy of eight leakage types. 
Hbiostat
 This directly frames the paper's contribution and should be cited.
Geirhos, Jacobsen, Michaelis, Zemel, Brendel, Bethge & Wichmann (2020), "Shortcut learning in deep neural networks," Nature Machine Intelligence 2(11):665–673, doi 10.1038/s42256-020-00257-z (16 April 2020). Shortcuts are defined as "decision rules that perform well on standard benchmarks but fail to transfer to more challenging testing conditions" 
Nature
 — precisely the bearing-identity memorisation mechanism argued here; name and cite it.
Zhao et al. (2020), "Deep learning algorithms for rotating machinery intelligent diagnosis: an open source benchmark study," ISA Transactions (arXiv:2003.03315). The open-source Paderborn benchmark and its evaluation protocol; it also reproduces the real-damage bearing table used here.
Yang et al., NRC (NeurIPS 2021) and AaD (NeurIPS 2022). The authors concede only SDALR and SHOT were tested; NRC and AaD are the obvious next SFDA baselines and should at least be discussed as limitations.
Matania, Cohen, Bechhoefer, Bortman (2024), "Test–Training Leakage in Evaluation of Machine Learning Algorithms for Condition-Based Maintenance," PHM Society European Conference 8(1):13, doi 10.36001/phme.2024.v8i1.4125. A closely related leakage critique that should be positioned against.
Rauber et al. / Varejão "similarity bias" work (referenced by Vieira: 40 of 41 CWRU studies from 2008–2020 were susceptible), 
arXiv
 useful historical grounding for the memorisation argument.
9. Specific questions to the authors
Which definition underlies the headline 56.8% clean and 37.3-pp collapse — the 12-task pooled mean or the mean of two fold means? Please reconcile with the 56.05%/38.1-pp figures in Section 6.5.
Were the gate operating points chosen on recordings disjoint from the evaluation recordings? If not, can you re-select them on a held-out rig/dataset and report the change in gate gains?
Please clarify the Table 6 population: how many of the 6 "engaged" faulty bearings are real-damage vs. artificial-damage, and what is the gate coverage specifically on the real-damage bearings used in adaptation?
Given HUST publishes per-type characteristic fault orders (e.g., 6204 BPFO = 3.093× fs), why was HUST gating omitted, and can it be added?
For the probe, were test recordings excluded from source training, and what is the identification rate on raw/handcrafted features (baseline)? Please also account for the 508 vs. expected 510 recordings.
How do you defend treating 12 fold-tasks that share source checkpoints as independent in the Wilcoxon tests? Can you provide clustered or fold-level tests and multiplicity-corrected p-values?
Since the oracle can exceed leaky (S04, 222%), can the "oracle bounds any pseudo-label filter" statement be restricted to keep/withhold filters and per-window action, and re-examined against per-recording gates?
Can you confirm the corrected author list for reference [4] and the venue for reference [18]?
Because the Paderborn real-damage bearings differ in damage mechanism (see §11), can you add a same-condition bearing-disjoint control that holds operating condition fixed, so bearing identity is not confounded with damage mechanism and difficulty?
10. Confidential comments to the editor

This is a valuable, contrarian evaluation paper whose main message (that cross-condition SFDA "gains" on Paderborn/HUST are largely a same-bearing memorisation artefact) is credible and well-supported by convergent evidence and a persuasive probe. The external references and dataset facts hold up well under checking. The blocking issues are internal-consistency and methodology problems rather than the core claim: a headline-number inconsistency (56.8 vs 56.05), figure/text mismatches, a source-free-premise tension in gate calibration, statistical pseudo-replication, and citation errors (notably the wrong author list for the very method being re-evaluated). I judge these fixable within a major revision. The generative-AI disclosure (Claude used for drafting/code/consistency checks) is appropriately declared, but given the numerical slips I recommend the authors independently re-verify all tables. The topic is squarely in MSSP scope and, once corrected, would be a useful methodological corrective for the field.

11. Cross-check of this report
4,000 draws: 20·10·20=4,000 — confirmed.
Fold means: leaky (88.3+99.9)/2=94.1 confirmed; clean (56.8+55.3)/2=56.05 confirmed; therefore the manuscript's 56.8/37.3 is internally inconsistent with its own Table 3 and with §6.5's 56.0/38.1 — confirmed.
Median Δleak 36.2, median recoverable 82, gate-gain median 4.5: recomputed from Table 3 values — all confirmed.
p-values 0.001/0.003/0.016/0.00024: 1/1024, 3/1024, 1/64, 1/4096 — confirmed as exact small-sample signed-rank/sign values; my Concern 4 is about the independence assumption, not the arithmetic.
HUST medians/means (33.5, 98.7, 59.6): recomputed from Table 5 — confirmed.
S04 recoverable 221–222%: (92.1−74.0)/(82.2−74.0)=2.207 — confirmed; Fig 4's 100% is therefore the mislabeled item.
Gate population decomposition (480 + 1,839; 23 faulty bearings): 6×4×20=480 and 23×4×20−1=1,839 — confirmed, and the "−1" corresponds to the independently documented corrupt file N15_M01_F10_KA08_2.mat (Paderborn KAt datacenter / DPMHM documentation, which notes the file "cannot be loaded by scipy.io.loadmat"), which strengthens the inference that artificial-damage bearings are included.
BPFO orders: 4(1−6.75/28.55)=3.0543 confirmed from verified Paderborn geometry (8 balls, 6.75 mm ball diameter, 28.55 mm FAG pitch diameter, all from Lessmeier et al. 2016 Table 1). The 3.0706 value follows from a 29.05 mm pitch diameter that I could not verify against any named primary source — the Lessmeier paper publishes only 28.55 mm (FAG), and a nominal 6203 (17 mm bore, 40 mm OD) gives a mean pitch diameter ≈ 28.5 mm, consistent with 28.55 but not 29.05 mm. Flagged for the authors to source. CWRU fan-end 6203 BPFO 3.053× confirmed from Smith & Randall (2015).
Damage-mechanism confound (audit item K): confirmed against Lessmeier et al. (2016) Table 5 — the outer-race real bearings mix fatigue-pitting (KA04, KA16, KA22) and plastic-deformation/indentation (KA15, KA30), while all six inner-race real bearings (KI04, KI14, KI16, KI17, KI18, KI21) are fatigue-pitting; the paper states "indentations were found at the outer ring only." 
phmsociety
 Hence bearing-disjoint splits can confound bearing identity with damage mechanism as well as difficulty. This belongs in the manuscript as an additional caveat and motivates a same-condition control (Question 9).
Operating conditions and 20 measurements/condition: confirmed against Lessmeier et al. (2016) Table 6 (N15_M07_F10 = 1500 rpm/0.7 Nm/1000 N; N09_M07_F10 = 900/0.7/1000; N15_M01_F10 = 1500/0.1/1000; N15_M07_F04 = 1500/0.7/400) 
phmsociety
 and "20 measurements of 4 seconds each for each setting." 
Uni-paderborn
Reference [4] author list: confirmed wrong (actual first author Wenyi Wu; not "H. Wu, Y. Zhang, J. Wang").
Reference [5]: confirmed exactly (MSSP 258, 2026, 114640; contains the 18-paper 2025 survey 
arXiv
 and the "unique training bearings is a decisive factor" finding).
Items I could NOT independently verify (flagged): refs [2], [10], [16], [17], [22]; the specific "every one of 18 reported >94% and six reported 100%" percentages (the 18-paper survey exists in ref [5], but I could not confirm those exact numbers); SDALR's reported 96.8% Paderborn mean (consistent with the manuscript's own reproduction of 96.78%/96.20% but not independently confirmed from the source text); the 29.05 mm Paderborn pitch diameter; the Borghesani SES-statistics content; and all Supplementary/pre-registration claims (not externally accessible). These should be treated as reviewer-unverified rather than confirmed or refuted.

Distinction of claim types: Verified facts are those confirmed against primary sources (dataset documentation, original papers, DOIs) or exact recomputation. Likely errors are the internal inconsistencies recomputed above (headline 56.8/37.3; RF 40.7; Fig 4 100%; KA04 0.56 vs 0.71; ref [4] authors). Reviewer judgement covers the source-free-premise tension, pseudo-replication, terminology ("leakage" vs "new task"), and the recommendation itself.