# Literature check of the novelty claims (MSSP submission, SFDA leakage on Paderborn)

Reviewer-style search, 2026-10-02. Sources searched: web search, Firecrawl web and research index, alphaXiv, SciSpace, plus publisher, arXiv, SSRN and PMC landing pages. I list a paper only if I opened a page for it that confirms the title and authors. Where I could only see the abstract, the entry says so. Manuscript text checked: `01_introduction.tex`, `02_background.tex`, `references.bib`, and the project notes (`notes/bio_sfda.md`, `notes/sensors_benchmark.md`, `notes/Q1_ASSESSMENT_2026-09-19.md`).

Each paper is tagged by role: **T** = threatens a novelty claim, **C** = should be cited, **S** = supports a claim.

---

## 0. Findings that need action before submission

1. **There is now a concurrent study of domain adaptation with held-out bearings on Paderborn.** Nagaswetha & Pathak (arXiv 2609.31639, 11 Sep 2026) run unsupervised domain adaptation (RBF-MMD, with source data) across Paderborn operating conditions. Every bearing goes wholly to train or to test. Their "held-out-bearing protocol" reaches 0.95 in the order domain. They do not run source-free adaptation, do not pair leaky and clean targets, and do not report a leaky baseline. As a result:
   - The sentence in Background §2.1, "applies it where it has not been applied: to source-free adaptation", is still literally true for source-free adaptation.
   - The broader picture ("nobody adapts to unseen bearings on PU") is no longer true.
   - This paper must be cited and contrasted. Their 0.95 also sits in visible tension with the manuscript's collapse. The likely reason is that their task is 3-class with mostly artificial-damage bearings (K001–K003, KA01/KA03/KA04, KI01/KI03/KI04) and three folds, and the manuscript should say so.
2. **Background §2.2 contains a sentence that is false as written: "In all of this work the target domain is a different operating condition of the same physical bearings."**
   - Jeong et al. 2025, which the manuscript cites, is cross-machine source-free adaptation over four different rotor rigs (VAT, DXAI, VBL-VA001, MaFaulDa; `notes/sensors_benchmark.md`). Jeong et al. also say they built that benchmark "to address the known issue of test–train leakage".
   - Bio-SFDA, also cited, reports CWRU→PU, a cross-dataset task (`notes/bio_sfda.md`, Table 4).
   - Both are bearing-disjoint by construction.
   - The sentence has to be restricted, for example to "the within-rig Paderborn source-free tasks (SDALR and those it compares against)", and the cross-machine cases have to be acknowledged. A reviewer who knows Jeong et al. will catch this.
3. **"Published audits of SFDA stability in this field address other failure modes, such as collapse under industrial noise" has no citation, and the work it describes is not published.**
   - The only matching item is Song & Ren, "An Empirical Audit and Class-Shift-Based Collapse Detection Framework for Source-Free Domain Adaptation in Bearing Fault Diagnosis". It is a GitHub repository (rxp613-dev/SFDA-Collapse-Detection) described as *submitted* to *Machines*. It covers about 960 runs of SHOT/TENT/NRC/SAR on CWRU. I found no published version.
   - Either cite it as an unpublished manuscript or repository, or rewrite the sentence. A suitable rewrite would cite the published general-ML audits instead: Boudiaf et al., ICML 2023, and Zhao et al., ICML 2023 (both in §C below).
4. **The oracle pseudo-label ceiling, claim (ii), has a direct general-ML precedent.** Schlachter, Fuss & Yang (EUSIPCO 2025) simulate pseudo-labelling with ground truth at controlled quantity and accuracy, and report the "upper bound of adaptation achieved with perfect pseudo-labeling" for source-free universal adaptation. The keep-or-withhold oracle is the same kind of instrument. Claim (ii) has to be worded as an application and decomposition in bearing source-free adaptation, not as a new idea, and this paper must be cited.
5. **The bearing-identity probe finding has a concurrent bearing-diagnosis neighbour.** Lei (SSRN 7226340, posted 3 Aug 2026) uses "channel-predictability probes" to measure bearing and condition predictability on Paderborn, HUST and CWRU. It also reports a 23.28 pp drop on the hardest Paderborn condition-disjoint fold. It is not a named novelty claim, but it is the nearest neighbour for Section `res-probe` and must be cited.

---

## A. Domain adaptation, generalisation and transfer on Paderborn with bearing-disjoint targets

| # | Citation | DOI / URL | Split and relevance | Tag |
|---|---|---|---|---|
| A1 | Nagaswetha, K.; Pathak, R. "When Does Domain Adaptation Help on Physical Vibration Sensors? A Held-Out-Bearing Study of Neural-Operator and Convolutional Models." arXiv:2609.31639, 2026 (IISc). | https://arxiv.org/abs/2609.31639 | **Bearing-disjoint across conditions on PU**: 1500 rpm source, targets at 900 rpm, reduced torque and reduced force. Healthy K001–K003, outer KA01/KA03/KA04, inner KI01/KI03/KI04; 3 folds, one bearing per class held out. Unsupervised MMD adaptation with source data. Source-only 0.36 vs target-supervised 0.97; MMD in the order domain reaches 0.95. No leaky baseline, no source-free method. Cites Hendriks and Vieira. | **T** for the background framing; **C** (must cite) |
| A2 | Sun, D.; Yang, X.; Yang, H. "A Domain Adaptation Meta-Relation Network for Knowledge Transfer from Human-Induced Faults to Natural Faults in Bearing Fault Diagnosis." *Sensors* 25(7):2254, 2025. | 10.3390/s25072254 | Unsupervised adaptation on PU, source KI07/KA06/K004 (artificial plus healthy) → target KI04/KA04/K005 (real plus healthy). Bearing-disjoint by construction, one bearing per class on each side, and still reports 99.62%. An example of a bearing-disjoint PU adaptation target in which one bearing per class still lets identity stand in for class. | **C** (qualifies "same physical bearings") |
| A3 | Chen, Y.; Peng, G.; Xie, C.; Zhang, W. et al. "ACDIN: Bridging the gap between artificial and real bearing damages for bearing fault diagnosis." *Neurocomputing* 294, 2018. | 10.1016/j.neucom.2018.03.014 | The canonical artificial→real PU transfer (supervised). Bearing-disjoint by construction; best conventional result about 75%, ACDIN about 95–96%. | **C** |
| A4 | Cao, X.; Wang, Y.; Chen, B.; Zeng, N. "Domain-adaptive intelligence for fault diagnosis based on deep transfer learning from scientific test rigs to industrial applications." *Neural Comput. Appl.* 33, 2021. | 10.1007/s00521-020-05275-x | Unsupervised adaptation from artificially damaged to real-damage test-rig bearings (PU-type task), then rig → industry. Bearing-disjoint by construction. | **C** (optional) |
| A5 | Kaya, Ş.M.; Jobani, A.E. "IoT-Driven Robust Bearing Fault Diagnosis for Induction Motors Under Operating-Condition Shift." *Sensors* 26(12):3829, 2026. | 10.3390/s26123829 | PU, measurement-wise vs condition-holdout vs **bearing-code-disjoint**. Macro-F1 about 0.86 (condition holdout) falls to about 0.56 (bearing-disjoint). They conclude generalisation to unseen bearing identities "remains challenging". Supervised only. | **S**, **C** |
| A6 | Cekic, Y.; Akan, A. "Motor-Current-Based Bearing Fault Detection Under Unseen Operating Conditions." *Energies* 19(16):3884, 2026. | 10.3390/en19163884 | PU, leave-one-operating-condition-out **plus strictly disjoint physical bearings**; motor current with a vibration reference. Domain generalisation, no adaptation, no leaky comparison. Specificity 0.09–0.56. | **C** |
| A7 | Jeong et al. 2025 (already cited, `jeong2025`). | 10.3390/s25144383 | Source-free adaptation with test-time training, **cross-machine** over four rotor-rig datasets. Different machines, so bearing-disjoint. Contradicts the "in all of this work" sentence. | already cited; fix the text |
| A8 | Yoon et al. 2026, Bio-SFDA (already cited). | 10.1016/j.rineng.2026.111105 | Reports **CWRU→PU** source-free adaptation, which is cross-dataset and so bearing-disjoint by construction. | already cited; fix the text |
| A9 | Zhang, Y.; Ren, Z.; Feng, K.; Yu, K.; Beer, M.; Liu, Z. "Universal source-free domain adaptation method for cross-domain fault diagnosis of machines." *MSSP*, 2023 (Liverpool repository PDF read). | https://www.sciencedirect.com/science/article/abs/pii/S0888327023000663 | Source-free adaptation on a DDS gearbox rig and one bearing rig. Tasks change condition on the same rig, so **not** bearing-disjoint. Listed to record that it is not a threat. | none |

**Bottom line for A.** I found no source-free bearing paper that evaluates a paired leaky vs bearing-disjoint target. Bearing-disjoint targets do appear:
- in cross-machine or cross-dataset source-free adaptation (A7, A8);
- in artificial→real PU transfer (A2–A4);
- in the new held-out-bearing unsupervised adaptation study (A1);
- in held-out-bearing generalisation studies (A5, A6).

Claim (i) survives because of its *paired, shared-checkpoint, within-rig* design, not because of bearing-disjointness itself.

## B. Leakage, bearing-wise splitting and specimen shortcuts beyond the four cited

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| B1 | Lei, Junyu (雷俊煜). "Measuring Protocol-Induced Shortcut Generalization in Bearing Fault Diagnosis: A Suppression-Response Test." SSRN preprint 7226340, posted 3 Aug 2026. | 10.2139/ssrn.7226340 | HUST, PU, CWRU. Grouped protocols plus **channel-predictability probes for bearing and condition identity** plus suppression interventions. 23.28 pp drop on the hardest PU condition-disjoint fold. A compact envelope representation improves unseen-bearing accuracy by 24.86 pp and reduces bearing predictability. Supports BPFO dependence but not a universal BPFI mechanism. Not peer reviewed. | **T** for probe novelty; **C**; **S** for envelope/outer-race findings |
| B2 | Abburi, H. et al. "A Closer Look at Bearing Fault Classification Approaches." *Annual Conf. PHM Society* 15(1), 2023. | 10.36001/phmconf.2023.v15i1.3473 | Shows that "assigning vibration data from a given bearing across training and evaluation splits leads to over-optimistic performance estimates" (run-to-failure data). Predates Wheat 2024. | **C** |
| B3 | Rosa, R.K.; Braga, D.; Silva, D. "Benchmarking deep learning models for bearing fault diagnosis using the CWRU dataset: A multi-label approach." arXiv:2407.14625, 2024 (preprint). | https://arxiv.org/abs/2407.14625 | Precursor to Vieira 2026 (shared authors). Leakage-free CWRU division plus multi-label formulation. | **C** (optional) |
| B4 | Horvath, K. "From Benchmark Accuracy to Industrial Evidence: A Registered Systematic Map and Nested Experiment-Level Audit of Validation Credibility in AI-Based Rotating-Machinery Fault Diagnosis." *Vibration* 9(4):62, 2026. | 10.3390/vibration9040062 | 157 validation experiments; 82.8% at the lowest "physical independence" levels (A0–A1); 59.2% leakage-unclear. A larger survey sample than Vieira's 18 papers. | **S**, **C** (intro) |
| B5 | Matania, O.; Dattner, I.; Bortman, J.; Kenett, R.S.; Parmet, Y. "A systematic literature review of deep learning for vibration-based fault diagnosis of critical rotating machinery: Limitations and challenges." *J. Sound Vib.* 590:118562, 2024. | 10.1016/j.jsv.2024.118562 | Same group as `matania2024leakage`; a review of evaluation limitations in the field. I saw only the abstract and metadata, so I did not verify how it treats leakage. | **C** (optional) |
| B6 | Zhao, Z.; Li, T.; Wu, J.; Sun, C.; Wang, S.; Yan, R.; Chen, X. "Deep learning algorithms for rotating machinery intelligent diagnosis: An open source benchmark study." *ISA Trans.* 107:224–255, 2020. | arXiv:2003.03315; https://www.sciencedirect.com/science/article/abs/pii/S0019057820303335 | Warns that random splits with overlapping sample preparation cause "test leakage". Same group as the cited `zhao2021udtl`, whose transfer benchmark uses same-bearing condition tasks. | **C** (optional) |
| B7 | Zhao, C.; Zio, E.; Shen, W. "Domain generalization for cross-domain fault diagnosis: An application-oriented perspective and a benchmark study." *Reliab. Eng. Syst. Saf.* 245:109964, 2024 (found as a citation in B4's reference list; landing page not opened). | 10.1016/j.ress.2024.109964 | Domain-generalisation benchmark. Its split protocol is unverified, and I list it only as a candidate to check. | to check |

## C. Audits and benchmarks of source-free and test-time adaptation

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| C1 | Song, C.; Ren, X. "An Empirical Audit and Class-Shift-Based Collapse Detection Framework for Source-Free Domain Adaptation in Bearing Fault Diagnosis." Submitted to *Machines*; repository only. | https://github.com/rxp613-dev/SFDA-Collapse-Detection | **This is what the uncited "collapse under industrial noise" sentence refers to.** About 960 runs of SHOT/TENT/NRC/SAR plus two 2024 methods on CWRU, learning-rate sensitivity under noise, and a class-shift collapse detector (AUC 0.809). **Not published**, so "Published audits" is inaccurate. | **C** as unpublished, or reword |
| C2 | Boudiaf, M.; Denton, T.; van Merriënboer, B.; Dumoulin, V.; Triantafillou, E. "In Search for a Generalizable Method for Source Free Domain Adaptation." ICML 2023. | https://arxiv.org/abs/2302.06658 | Source-free methods re-rank on realistic (bioacoustic) shifts and sometimes do worse than no adaptation. A published, general audit of source-free stability. | **C**, **S** |
| C3 | Zhao, H.; Liu, Y.; Alahi, A.; Lin, T. "On Pitfalls of Test-Time Adaptation." ICML 2023 (TTAB). | https://arxiv.org/abs/2306.03536 | Benchmark of 10 test-time adaptation methods; shows that hyperparameter and model selection without target labels is the main pitfall. Supports the manuscript's frozen-protocol stance. | **C** |
| C4 | Yi, L. et al. "When Source-Free Domain Adaptation Meets Learning with Noisy Labels." ICLR 2023. | https://arxiv.org/abs/2301.13381 | Treats source-free pseudo-labels as structured label noise. Useful framing for the oracle and filter section. | **C** (optional) |

## D. Physics-informed pseudo-label selection in bearing adaptation

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| D1 | Jia, N.; Huang, W.; Ding, C.; Wang, J.; Zhu, Z. "Physics-informed unsupervised domain adaptation framework for cross-machine bearing fault diagnosis" (PIUDA). *Adv. Eng. Inform.* 62:102774, 2024. | 10.1016/j.aei.2024.102774 | Builds **physical labels** from fault-characteristic spectral energy, aligns them with spectral clustering into hard pseudo-labels, then iterates soft labels. This is the closest neighbour to Bio-SFDA/PCTL for physics-gated pseudo-labels, and it is cross-machine. From the abstract I saw no false-acceptance-on-healthy metric (full text not accessible). | **C** (nearest neighbour for iii) |
| D2 | Cao, S.; Duan, Y.; Huang, J. "An interpretable unsupervised fault diagnosis method for rolling bearings based on physically-informed pseudo-label updating." *Proc. IMechE Part C*, 2025. | 10.1177/09544062251345305 | Initial pseudo-labels from a **fault octave amplitude ratio** at characteristic frequencies, then a physically constrained update. Not domain adaptation, but physics-generated pseudo-labels. | **C** |
| D3 | Wang, Q.; Taal, C.; Fink, O. "Integrating Expert Knowledge With Domain Adaptation for Unsupervised Fault Diagnosis." *IEEE Trans. Instrum. Meas.* 71, 2022. | https://arxiv.org/abs/2107.01849 | Synthetic faults built from BPFI/sidebands injected into healthy signals, with domain adaptation from synthetic to real. A physics prior in adaptation, through data rather than gating. | **C** (optional) |
| D4 | Liu, L.; Hao, C.; Xiong, L.; Lv, X. "Physics-guided cross-domain adaptation: a hierarchical hybrid transformer framework with contrastive learning…" *Sci. Rep.* 16:27619, 2026. | 10.1038/s41598-026-57900-9 | An envelope/order "physical anchor" plus confidence-thresholded pseudo-labels; CWRU 94.9%, PU 90.3%. No healthy false-acceptance metric in the summary. | **C** (optional) |
| D5 | "Envelope spectrum knowledge-guided domain invariant representation learning strategy for intelligent fault diagnosis of bearing." *ISA Trans.*, 2025 (index entry; PMID 40102111). | 10.1016/j.isatra.2025.03.004 | Envelope-spectrum knowledge as a prior for invariance. Not opened beyond the index. | to check |
| D6 | Chen, Y. et al. "A Multi-level Information Integration Framework for Physically Verifiable Fault Diagnosis of Rotating Machinery." arXiv:2607.22797, 2026. | https://arxiv.org/abs/2607.22797 | Uses predicted characteristic-frequency deviation to flag misclassifications on PU and JNU (AUROC 0.97/0.87). It is a physics "verifier", but on window-level (leaky) splits, and it does not test false acceptance on healthy bearings. | **C** (optional) |

**Bottom line for D.** None of D1–D6, Bio-SFDA or PCTL reports the rate at which a physics gate accepts a fault on real healthy recordings. Claim (iii) survives, but D1 has to be named as a nearest neighbour.

## E. Envelope detectability on Paderborn real damage

I found **no** Smith & Randall-style benchmark that grades Paderborn recordings for envelope diagnosability or counts how many bearings show clear BPFO/BPFI. Searches covered SES, kurtogram, infogram, cyclic spectral coherence, Gryllias/Randall/Antoni and "diagnosability". Lessmeier et al. 2016 describe envelope analysis as the reference procedure, but the PHM Society server returned 503 during this session, so I could not re-check what they report per bearing.

The nearest evidence is indirect:
- B1 (Lei) finds BPFO dependence for outer-race faults but **no universal inner-race BPFI mechanism** on unseen PU bearings.
- Smith & Randall 2015 on CWRU (already cited) found a large non-diagnosable fraction.

The manuscript's roughly 20–24% gate certification therefore does not contradict any published PU figure. It also cannot be called "consistent with prior PU literature", because none exists. Say this explicitly, and present the number as a new descriptive measurement.

## F. Oracle pseudo-label ceilings

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| F1 | Schlachter, P.; Fuss, J.; Yang, B. "Analysis of Pseudo-Labeling for Online Source-Free Universal Domain Adaptation." EUSIPCO 2025; arXiv:2504.11992. | https://arxiv.org/abs/2504.11992 | Controlled simulated pseudo-labelling: the top q% of samples are selected and the top a% get the ground-truth label. Reports the upper bound under perfect pseudo-labelling (e.g., CE 91.9% vs SOTA 41.2% for the partial-set setting), and finds pseudo-label accuracy matters more than quantity. **Direct precedent for the oracle ceiling idea.** | **T** for claim (ii) as worded; **C** (must cite) |
| F2 | Self-training literature routinely reports "fraction of an oracle/ground-truth-trained system recovered". Examples: Kahn et al., self-training for end-to-end ASR, arXiv:1909.09116 (recovers 59.3% of the gap to an oracle); Khurana et al., DUST, arXiv:2011.13439 (up to 80% recovered). | https://arxiv.org/abs/1909.09116 ; https://arxiv.org/abs/2011.13439 | "Share of the gap recovered" is an established metric. The manuscript's "closes a median 19% of the gap" uses that convention. | **C** (optional) |

## G. Cage slip and shaft-order coincidence

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| G1 | Prashad, H. "The Effect of Cage and Roller Slip on the Measured Defect Frequency Response of Rolling-Element Bearings." *ASLE Trans.* 30(3):360–367, 1987. | 10.1080/05698198708981768 | Experimental theoretical-vs-measured defect frequencies with HFRT/envelope analysis; an early measurement of slip. The obvious primary citation next to the "1–2%" rule of thumb. | **C** |
| G2 | Randall & Antoni 2011 (already cited). | 10.1016/j.ymssp.2010.07.017 | The tutorial states that mean slip can **lock onto an exact subharmonic of shaft speed** (FTF at 0.4×, BSF onto 0.2× harmonics). This is a direct published antecedent of the "6203 fault lines lock onto shaft orders" observation. It must be cited *at that sentence*, and the manuscript's contribution framed as the per-manufacturer quantification for automated gating. | already cited; **cite at the slip sentence** |
| G3 | Selvaraj, A.; Marappan, R. "Experimental analysis of factors influencing the cage slip in cylindrical roller bearing." *Int. J. Adv. Manuf. Technol.*, 2011. | 10.1007/s00170-010-2854-5 | Measured cage slip versus load, speed and viscosity. Slip is negligible above a critical load, consistent with a small measured slip under PU's radial load. | **C** (optional) |
| G4 | Zhan, L. et al. "Development of a Novel Detection Method to Measure the Cage Slip of Rolling Bearing." *IEEE Access* 8, 2020. | 10.1109/ACCESS.2020.2976504 | Direct (non-vibration) cage-slip measurement; context for small measured slip. | optional |

I found no published *measured* slip distribution for Paderborn 6203 bearings. A median of about 0.06% would be new data, but it should be framed against G1/G3 (slip depends on load) rather than only against the 1–2% rule.

## H. Shortcut learning and subject-wise splits (analogues)

| # | Citation | DOI / URL | Relevance | Tag |
|---|---|---|---|---|
| H1 | Saeb, S. et al. "The need to approximate the use-case in clinical machine learning." *GigaScience* 6(5), 2017. | https://pubmed.ncbi.nlm.nih.gov/28327985/ | Record-wise vs subject-wise cross-validation; record-wise overestimates; about 45% of reviewed studies used the wrong scheme. The closest analogue of bearing-wise splitting. | **C** |
| H2 | Brookshire, G. et al. "Data leakage in deep learning studies of translational EEG." *Front. Neurosci.* 2024. | 10.3389/fnins.2024.1373515 | Segment-based CV leaks subject identity, and most DNN-EEG studies do this. | **C** |
| H3 | Lin, J.-Y.; Wu, Y.C.; Jung, T.-P. "The Identity Trap in EEG Foundation Models: A Diagnostic Audit." arXiv:2606.06647, 2026. | https://arxiv.org/abs/2606.06647 | Subject identity dominates representation variance and is diagnosable by probing before fine-tuning; subject-disjoint validation alone does not remove the bias. A close analogue of the bearing-identity probes. | **C** |
| H4 | Gholamiangonabadi, D.; Kiselov, N.; Grolinger, K. "Deep Neural Networks for Human Activity Recognition With Wearable Sensors: Leave-One-Subject-Out Cross-Validation for Model Selection." *IEEE Access* 8:133982–133994, 2020. | 10.1109/ACCESS.2020.3010715 | 99.85% (10-fold) vs 85.1% (leave-one-subject-out). | **C** (optional) |
| H5 | de Chazal, P.; O'Dwyer, M.; Reilly, R.B. "Automatic classification of heartbeats using ECG morphology and heartbeat interval features." *IEEE TBME* 51(7):1196–1206, 2004. | 10.1109/TBME.2004.827359 (DOI from memory, not verified) | Origin of the inter-patient vs intra-patient ECG paradigm. | **C** (optional) |
| H6 | Zech, J.R. et al. "Variable generalization performance of a deep learning model to detect pneumonia in chest radiographs: A cross-sectional study." *PLoS Med.* 15(11):e1002683, 2018. | 10.1371/journal.pmed.1002683 | Site (hospital) identity is decodable and confounds diagnosis; the medical analogue of "the shortcut is in the signals". | **C** (optional) |
| H7 | Lapuschkin, S. et al. "Unmasking Clever Hans predictors and assessing what machines really learn." *Nat. Commun.* 10:1096, 2019. | 10.1038/s41467-019-08987-4 | Canonical "Clever Hans" reference, alongside the cited Geirhos 2020. | **C** (optional) |

I found no paper that uses "Clever Hans" or "shortcut learning" explicitly for vibration machine-health data, other than B1 (Lei 2026), which uses "shortcut learning" in its keywords.

---

## Assessment of the four novelty claims

| Claim | Verdict | Reason and needed change |
|---|---|---|
| **(i)** Paired leaky/clean evaluation of source-free adaptation from one shared source checkpoint | **Survives, after rewording of the background** | No paper found pairs leaky and clean targets for source-free (or unsupervised) adaptation. However, bearing-disjoint adaptation targets already exist: cross-machine source-free (Jeong 2025; Bio-SFDA CWRU→PU), artificial→real PU unsupervised adaptation (Sun 2025; ACDIN 2018), and held-out-bearing unsupervised adaptation on PU (Nagaswetha & Pathak 2026). Replace "applies it where it has not been applied: to source-free adaptation" with something like "to a paired, within-rig comparison for source-free adaptation". Delete or restrict "In all of this work the target domain is … the same physical bearings". |
| **(ii)** Oracle pseudo-label ceiling bounding every keep-or-withhold filter | **Needs rewording** | Perfect-pseudo-label upper bounds are established (Schlachter et al. EUSIPCO 2025), and oracle-gap recovery is a standard self-training metric. What remains new is the use in bearing source-free adaptation and the split of the collapse into a filter-recoverable part and a representation-carried part. Cite F1 and state that delta (rule C50). |
| **(iii)** False-acceptance curves on real healthy recordings for physics gates | **Survives** | Not reported by Bio-SFDA, PCTL, PIUDA (Jia 2024), Cao 2025, Liu 2026 or Chen 2026. Add Jia et al. 2024 as the nearest neighbour. "Rarely reported" can become "not reported in the [named] works". |
| **(iv)** Same-condition control: recording-level separation does not remove the leak | **Survives only in a narrow form; reword** | That bearing overlap inflates accuracy beyond window or recording separation is shown in Vieira 2026 (bearing- vs segmentation-level leakage), Kaya & Jobani 2026 (measurement-wise vs bearing-code-disjoint on PU) and Lei 2026 (probes plus protocol drops on PU). What is new is the paired same-condition contrast against Knap et al.'s recording-separated benchmark. Phrase it as a targeted control of that benchmark design, not a new finding about leakage. |

Also affected but not numbered as claims:
- **The probe result** (bearing identity decodable from 10 time statistics) must cite Lei 2026 (B1) and the EEG analogue (H3).
- **The "6203 lock" observation** must cite Randall & Antoni's subharmonic-locking remark (G2) at the sentence where it appears. The manuscript's own notes already concede that Smith & Randall observed the lock.

## Ranked must-cite additions

1. **Nagaswetha & Pathak 2026**, arXiv:2609.31639. Held-out-bearing domain adaptation on PU; the closest concurrent work, and its 0.95 needs a sentence of reconciliation.
2. **Schlachter, Fuss & Yang 2025**, EUSIPCO, arXiv:2504.11992. Precedent for the oracle and perfect-pseudo-label ceiling.
3. **Lei 2026**, SSRN 7226340, 10.2139/ssrn.7226340. Bearing and condition predictability probes and protocol leakage on PU, HUST and CWRU.
4. **Jia et al. 2024**, *Adv. Eng. Inform.* 62:102774, 10.1016/j.aei.2024.102774. Physics-informed pseudo-labels in unsupervised adaptation; nearest neighbour for (iii).
5. **Kaya & Jobani 2026**, *Sensors* 26:3829, 10.3390/s26123829. PU bearing-code-disjoint collapse in a supervised setting.
6. **Text fixes using already-cited Jeong 2025 and Bio-SFDA**: correct the "same physical bearings in all of this work" sentence. Also cite **Sun, Yang & Yang 2025** (10.3390/s25072254) and **ACDIN 2018** (10.1016/j.neucom.2018.03.014) as bearing-disjoint artificial→real PU transfer.
7. **Song & Ren (unpublished)**, cited as a repository or submitted manuscript, or replaced by **Boudiaf et al. ICML 2023** and **Zhao et al. ICML 2023**. Fix the uncited "Published audits" sentence.
8. **Horvath 2026**, *Vibration* 9:62, 10.3390/vibration9040062, and **Abburi et al. 2023**, PHM Society, 10.36001/phmconf.2023.v15i1.3473. Field-level leakage evidence that strengthens the Introduction.
9. **Cekic & Akan 2026**, *Energies* 19:3884, 10.3390/en19163884. Held-out bearing plus held-out condition on PU.
10. **Prashad 1987**, *ASLE Trans.* 30:360, 10.1080/05698198708981768, plus Randall & Antoni 2011 cited at the slip-lock sentence.
11. **One or two cross-domain analogues**: Saeb et al. 2017 (*GigaScience*) and Lin, Wu & Jung 2026 (EEG identity trap). Optionally Brookshire 2024 and Zech 2018.

Lower priority: Cao et al. 2025 (*Proc IMechE C*); Wang, Taal & Fink 2022; Zhao et al. 2020 *ISA Trans.* open benchmark; Rosa et al. 2024; Matania et al. 2024 *JSV*; Yi et al. ICLR 2023.

## Verification limits

- **Seen only as an abstract or index entry:** D1 (Jia 2024) and B5 (Matania JSV). D5 and B7 were seen as index or citation entries only.
- **Unverified DOI:** H5 (de Chazal), supplied from memory.
- **Not accessible:** Lessmeier 2016 (server 503) and the full texts of PIUDA and the ASLE paper.
- **Not peer reviewed:** Lei 2026 (SSRN) and Nagaswetha & Pathak 2026 (arXiv), both posted within the last two months. A reviewer would still expect them cited, or at least acknowledged as concurrent work.
