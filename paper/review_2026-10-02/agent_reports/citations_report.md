# Citation fact-check: paper/tex (MSSP submission), 2026-10-02

Scope: I checked every `\cite` in `sections/*.tex` and `tables/*.tex` (64 citation lines, 36 bib entries) against primary sources, plus the bibliographic metadata in `references.bib` (Crossref API and publisher pages). Ordered by consequence. Verdicts: CONFIRMED / WRONG / PARTLY / UNVERIFIABLE.

Full text I read: Vieira (arXiv 2509.22267v5), SDALR (arXiv 2503.08749v1 and GitHub README), Knap (PHME PDF), PCTL (EiN PDF), Bio-SFDA (ScienceDirect HTML, open access), Jeong (PMC), HUST, UORED, JNU, Kapoor (PMC), Lessmeier (PHME PDF), Smith & Randall (RG PDF), Liu 2021 (arXiv), US 10,168,248 (Google Patents).
Abstract or excerpt only: Hendriks, Matania 2024 and 2025, Borghesani, Wheat, Randall & Antoni, SDALR Neurocomputing version, ISO 15243 (table of contents).

---

## A. Consequential (fix before submission)

### A1. Novelty item (iv) and the Knap characterisation omit directly overlapping prior results. WRONG/PARTLY
- **Claim:** 01_introduction.tex:69-70: "(iv) a same-condition control showing that recording-level separation does not remove the leak". 02_background.tex:92-94: Knap's separation "is enforced at *recording* level, which removes window leakage but still permits the same physical bearing on both sides of a transfer task". 06_results.tex:98 describes the same thing.
- **What the sources say:**
  - **Vieira et al.** (v5, Sec. 6.2, Table 12) already ran this control on Paderborn. In a *repetition-wise* split, the model is trained on some measurement repetitions and tested on others from the same bearing at the same operating condition, so recordings are separated. The same split also appears as *condition-wise*. Both are classed as bearing-level leakage. On Paderborn, WDCNN Macro-AUROC is 98.6-100 % with repetition-wise leakage and 86.9-92.3 % with condition-wise leakage, against 54.3-77.0 % with no leakage. Vieira calls the repetition-wise split "as detrimental as segmentation-level leakage".
  - **Knap et al.** Table 1 includes a **"PU Cross-Bearing Instance"** scenario (shift factor "bearing identity"; held-out bearings K001, KA30, KI21, KB23). They also include CWRU Cross-Fault Instance (held-out 0.021" fault families) and PU Cross-Damage Provenance (artificial to real). Sec. 4.4 calls PU Cross-Bearing Instance one of "the most challenging settings" (best ML macro-F1 0.355). The protocol's *rule* is recording-level. The benchmark itself, however, contains a bearing-disjoint scenario and reports it as among the hardest.
- **Suggested fix:**
  - Keep (iv), but scope it to what is new: an SFDA-paired, same-condition control on ten pre-registered splits with cluster-level inference.
  - Name Vieira's repetition-wise PU result (Table 12) as the nearest neighbour, with a one-sentence delta. Rule C50 requires this.
  - In 02_background, add that Knap include a bearing-disjoint "Cross-Bearing Instance" scenario and find it among the hardest, so the gap is the recording-level *default* and the absence of SFDA, not a lack of bearing-disjoint evaluation.

### A2. "In all of this work the target domain is a different operating condition of the same physical bearings". WRONG
- **Claim:** 02_background.tex:115-116 (closing the SFDA paragraph that cites SHOT, SDALR and Jeong).
- **What the sources say:**
  - **Jeong et al. 2025** (Sensors 25:4383, Sec. 4.1) build a cross-*dataset* benchmark. VAT, MaFaulDa and DXAI are the source. **VBL-VA001 is "reserved as a test-only target domain"**, a different machine with different bearings. Their classes also include misalignment and unbalance.
  - **Bio-SFDA** is "strict CWRU → PU" (different rigs).
  - **PCTL** transfers CWRU↔PU and PHM2012→CWRU/PU.
- **Suggested fix:** Restrict the sentence to SDALR and the Paderborn/JNU condition-transfer protocol. For example: "In SDALR and the condition-transfer protocols it inherits, the target domain is a different operating condition of the same physical bearings; cross-dataset SFDA (Jeong, Bio-SFDA) changes rig, bearing and often label space at once, and so cannot isolate bearing identity either."

### A3. PCTL described as a pseudo-label filter. WRONG
- **Claim:** 01_introduction.tex:33-35: "characteristic-frequency evidence can filter pseudo-labels during adaptation, as in the EAGLE module of Bio-SFDA or the consistency validator of PCTL".
- **What the source says** (PCTL PDF Sec. 2.1, Alg. 1, Eq. 5-6, Sec. 3.2):
  - PCTL uses **no pseudo-labels**; the word appears once in the paper, in an unrelated phrase.
  - Stage 2 fine-tunes "on a small amount of labeled target-domain data".
  - The Physics Consistency Validator (PCV) produces a score S_phys that supervises a confidence predictor through an MSE loss. Nothing is filtered.
  - The score is computed on the **predicted** envelope spectrum, P_phy(E(x)), reconstructed from the latent features, not on the measured signal. It is the mean prominence of the first 3 harmonics; for the Normal class it is 1 - the mean energy at the fault frequencies.
  - The setting is UDA pre-training followed by supervised fine-tuning, not SFDA.
- **Suggested fix:**
  - Intro: "...can filter or weight pseudo-labels during adaptation, as in the EAGLE module of Bio-SFDA, or supervise model confidence, as in the consistency validator of PCTL".
  - 02_background.tex:45-46 is correct in substance (labelled target data, confidence predictor) but should say "against the envelope spectrum **predicted from the learned features**".
  - 05_gates.tex:23 and t5_gates "PCV-style": PCV is a continuous peak-prominence score on a predicted spectrum, not a threshold rule. Rename to "Envelope threshold rule", or keep the label with a footnote that it is inspired by, not a reimplementation of, PCV.

### A4. Vieira "100 evaluation splits" attached to the leakage measurement. WRONG (02_background) / PARTLY (intro)
- **Claim:** 02_background.tex:9-11: Vieira "measured the inflation caused by bearing- and segmentation-level leakage over 100 evaluation splits". 01_introduction.tex:65: "over four datasets and 100 splits".
- **What the source says** (v5):
  - The 100 splits are the leakage-free performance-estimation stage of their CVM-CV protocol (Sec. 4.1.3, 4.2), run per dataset.
  - The leakage experiments (Sec. 6) use **20 splits on UORED, 20 on PU, and 12 condition/fault-size groups on CWRU**.
  - Leakage is measured on **three** datasets. HUST appears only in Appendix B (co-occurring faults, 2:2 split, 100 splits).
  - "Four datasets" is correct for the paper as a whole: the abstract lists CWRU, PU, UORED-VAFCLS and HUST.
- **Suggested fix:** "...generalised bearing-wise partitioning across four datasets (100 evaluation splits each), reformulated diagnosis as multi-label detection, and measured the inflation caused by bearing- and segmentation-level leakage on three of them". In the intro, use "over four datasets" and drop "and 100 splits", or say "100 bearing-disjoint splits per dataset".

### A5. Vieira Table 1 survey: the 18th paper is unaccounted for. PARTLY (numbers CONFIRMED)
- **Claim:** 01_introduction.tex:14-16: "sampled 18 ... every one reported above 94%, five reported 100%, and none split ... by physical bearing --- eight split at random and nine by condition (load, speed or noise level)".
- **What the source says** (v5 Sec. 3.3, Table 1, p. 8-9):
  - 18 papers: 10 drawn at random from 195 MSSP 2025 hits, plus 8 from other journals.
  - "8 of the 18 papers used a random splitting strategy, while 9 detailed a condition-wise split... **The remaining paper did not mention any partitioning methodology**." That paper is ref. [35]: Fang et al., MSSP 232 (2025) 112707, "Not detailed", result ">94%".
  - Exactly five report 100 % ([25]-[29]).
  - The lowest entry is ">94%", so "above 94%" is accurate.
  - Conditions are load (most common), rotation speed or noise level. Confirmed.
- **Suggested fix:** "...eight split at random, nine by condition (load, speed or noise level), and one did not state its split". Optionally add "(ten drawn at random from MSSP)".

### A6. Table 1: CWRU sampling rate. WRONG/incomplete
- **Claim:** tables/t1_datasets.tex:13 gives f_s = 12 kHz for CWRU. 06_results.tex:225 uses "4 CWRU baselines" for off-rig calibration.
- **What the sources say:**
  - Smith & Randall 2015, App. A, has the table heading "48k normal baseline data; fs = 48 kHz" for data sets 97-100. Fault data are 12 kHz.
  - The CWRU Bearing Data Center page confirms the 12k and 48k acquisitions.
  - The project's own `notes/_pmmcp_records.py:116-117` already records 48000 for the normal baselines.
- **Suggested fix:** Change the f_s cell to "12 (faults), 48 (normal)". Re-check the "≈10 s" record length for the 48 kHz baselines against the files' sample counts; I did not verify lengths from a primary document.

### A7. SDALR "preprocessed archive is not publicly available". PARTLY/WRONG wording
- **Claim:** 04_protocol.tex:27-28.
- **What the source says:** The SDALR README (github.com/BdLab405/SDALR) links the preprocessed `PU_1d_8c_2048` and `JNU_1d_2048_2000` archives on Baidu Netdisk, with the extraction code in the URL. `notes/sdalr_code_audit.md` A6 says the same.
- **Suggested fix:** Say what is true. For example: "its preprocessed windows are distributed only through a Baidu Netdisk link that we did not use (or could not retrieve), and the paper states neither a hop nor start positions, so our hop is our choice".

### A8. SDALR numbers are verified only in the arXiv preprint. PARTLY
- **Claim:** 96.8 / 96.78 % on PU; 98.50 on JNU; A3→A2 97.84; A1→A2 87.03; eight classes (K001, KA04, KA15, KA22, KA30, KI14, KI17, KI21); 2048-sample windows; 2000 per class; code released. Locations: 01_intro:17, 02_bg:34-36, 04_protocol:26-27, 06_results:7-13.
- **What the sources say:**
  - All of these are **CONFIRMED in arXiv 2503.08749v1**: Sec. 4.1, Table 1, Table 4 (SDALR row 87.03 / 99.95 / 96.19 / 99.73 / 99.96 / 97.84, avg 96.78) and Table 5 (avg 98.50).
  - The bib cites the Neurocomputing 657:131661 version, which is paywalled. Its abstract (seen) confirms the method and code URL but not the tables.
  - The README describes a ∂ sweep of 0.45-0.95, while the arXiv paper sweeps 0.5-0.95. That suggests the published version was revised.
- **Suggested fix:** Check the numbers against the Neurocomputing tables through institutional access before submission, or cite them as "(arXiv v1, Table 4)".

### A9. Table 1 Paderborn "Conditions: 4 (2 used)" is internally inconsistent. Not a citation error
- t1_datasets.tex:11 says "4 (2 used)". 03_data.tex:9-11 uses three conditions (A1-A3) for adaptation, plus N09 for gates and slip. All four conditions are confirmed by Lessmeier Table 6 (N15_M07_F10, N09_M07_F10, N15_M01_F10, N15_M07_F04).
- **Suggested fix:** "4 (3 for adaptation)".

---

## B. Moderate

### B1. Wheat et al. "gap ... large enough to change method rankings". UNVERIFIABLE (abstract only)
- **Claim:** 02_background.tex:7-9; also intro:64.
- **What the source says:**
  - Abstract (IEEE Access 12:169879): six methods (PCA, SPCA or LDA, each with frequency or envelope features) on McMaster and Paderborn data. There is an "over a 40% drop in accuracy" depending on the split. The good McMaster frequency-analysis results "are not expected to generalize".
  - The split names run-to-run, day-to-day and part-to-part are confirmed (IEEE full-text page; Vieira p. 9).
  - I could not retrieve a full-text sentence saying the method ranking changes.
- **Suggested fix:** "...and found accuracy drops of over 40 % between them, enough to overturn conclusions drawn from the leaky split". Or quote the ranking statement once it is located in the full text.

### B2. Patent US 10,168,248 as an instance of the "sufficient spectral resolution" view. PARTLY
- **Claim:** 06_results.tex:314-315.
- **What the source says** (Google Patents):
  - Claim 1 covers resampling vibration to fixed angular increments using integer-tabulated gear ratios.
  - The description argues that "bearing vibration occurs at non-integer multiples of shaft speeds", so synchronous and non-synchronous components (turn-synchronous averaging over many revolutions) separate gear from bearing content.
  - It does not argue about spectral resolution as such.
- **Suggested fix:** "The contrary working assumption, that bearing lines are non-synchronous and therefore separable from shaft harmonics, appears in practice; a patent states it explicitly ('bearing vibration occurs at non-integer multiples of shaft speeds')". Bib metadata (Morey and Steward; Tensor Systems; granted 1 Jan 2019; continuation US 10,598,568 B1, granted 24 Mar 2020) is CONFIRMED.

### B3. JNU "3 speeds" cited to Li et al. 2013. PARTLY
- **Claim:** t1_datasets.tex:15: JNU, 50 kHz, 20 s, 3 speeds.
- **What the source says:** Li et al. 2013 (Sensors 13:8013, Sec. 4) gives 50 kHz and 20 s, which is CONFIRMED. However, "the rotation speed varies from 400 to 800 rpm". The 600/800/1000 rpm three-domain structure is how the distributed JNU dataset is used (SDALR Table 2), not something Li 2013 describes.
- **Suggested fix:** Footnote: "3 speeds (600/800/1000 rpm) as distributed and as used by SDALR".

### B4. Matania et al. 2025 "project order-domain envelope spectra onto kinematic harmonic positions ... machine-invariant". UNVERIFIABLE (abstract only)
- **Claim:** 02_background.tex:60-62; intro:73-74.
- **What the source says:** The abstract states only that the method "projects the signals into an invariant feature space by physics-based algorithms" and classifies spall type with a fully connected network, using six datasets. The full text is paywalled.
- **Suggested fix:** Verify the order-SES/harmonic-position description in the full text. If it cannot be confirmed, soften to "project signals into a physics-based invariant feature space".

### B5. Bio-SFDA EAGLE as a raw-spectrum mechanism. PARTLY (paragraph otherwise CONFIRMED)
- **Claim:** 02_background.tex:47-48; 05_gates.tex:28-37.
- **What the source says** (Sec. 4.1-4.2):
  - Confirmed: four ROIs at BPFO, BPFI, BSF and an impulse band, "on the STFT magnitude X(f,t)"; thresholds "refined automatically using only unlabeled target statistics"; "a light-weight routine rescales thresholds so that band activation rates stay within a conservative range"; SPIDER "may apply bounded multiplicative factors to adaptive_thresholds" and adjusts τ; the per-sample weight is w_e·s(x) with teacher confidence.
  - However, the ROI features include "envelope peak counts" and thresholds for "envelope percentiles", and the noise feature is a "robust SNR_ROI" rather than a peak-to-neighbourhood ratio.
  - A ball class (CWRU-sized 0.007-0.021 defects) appears in the 4-class table, and the task is CWRU→PU. This supports the "cannot be reconstructed" caveat.
- **Suggested fix:** In 05_gates, add "(the published module also uses envelope peak counts within each ROI, which ours omits)" so that "raw spectrum vs envelope" reads as a property of our implementation.

### B6. "Published audits of SFDA stability in this field address other failure modes, such as collapse under industrial noise". Uncited
- **Claim:** 02_background.tex:114-115 carries no citation.
- **Suggested fix:** Cite the audit(s) meant, or delete the sentence.

### B7. Matania et al. 2024 "same case for condition-based maintenance generally". PARTLY (minor)
- **What the source says:** The abstract (Crossref) frames it within CBM but reviews the issue for rolling-bearing fault-type classification. Vieira (p. 9) notes it proposes fault-size-guided splitting on CWRU and PU, with healthy samples excluded.
- **Suggested fix:** "...make the same case for bearing fault classification in condition-based maintenance".

### B8. HUST "one physical bearing per class for each of five types". CONFIRMED with a source caveat
- **What the source says** (Thuan & Hong 2023, BMC Res Notes 16:138):
  - Confirmed: 6204-6208; 51.2 kHz; 10 s; 0, 200 and 400 W; inner, outer and ball diameters plus ball count, with **no pitch diameter and no characteristic orders**. This supports 03_data.tex:38-39.
  - The note also says "27 prototype defective bearings and 3 healthy bearings", which is inconsistent with its own 99 files = 33 configurations. Vieira Table 14 lists five healthy files, N4-N8.
- **Suggested fix:** No change needed. Optionally footnote that the healthy-bearing count in the data note is inconsistent and the file list is used.

### B9. UORED Table 1 "1 condition". PARTLY (minor)
- **What the source says** (Sehri et al. 2023): 42 kHz, 10 s and 20 bearings are confirmed. Each bearing has one healthy recording (H-n-0), and the bearings were run from healthy to failure, so "natural faults" is confirmed. Healthy, inner, outer and cage data are at 400 N; **ball-fault data at 0 N**; 1750 rpm throughout.
- **Suggested fix:** Optional "1 (healthy at 400 N, 1750 rpm)". Correct as is for the healthy-only gate use.

---

## C. Confirmed claims (seen in source)

| Ref | Manuscript claim | Evidence |
|---|---|---|
| vieira2026 | 02_bg:11-13 quote "training and testing within a single testbench"; inter-testbench named as an alternative not pursued | v5 p. 2, verbatim |
| vieira2026 | 08_rec:42-43 "number of unique training bearings is the decisive factor" | Abstract; Sec. 5 Fig. 10 |
| vieira2026 | intro:25 leakage "change[s] conclusions" | Sec. 6.1: distorts "conclusions about the most suitable input representation"; Sec. 3.2 toy LR vs DT |
| hendriks2022 | 02_bg:6-7 | Abstract: "the same physical bearings exist in both training and testing sets ... independent sets of bearings". Vieira notes their healthy signals still leak; optional caveat. |
| knap2026 | Six fixed scenarios on CWRU and PU; recording-level separation; no SFDA | Sec. 1.2, 2.2, 3.1, Table 1; adaptation listed only as future work. See A1 for the omission. |
| kapoor2023 | 17 disciplines; taxonomy | "294 papers across 17 scientific fields"; "taxonomy of eight types" |
| geirhos2020 | Shortcut definition | Standard; metadata correct |
| liu2021labelshift | Marginal alignment under label shift induces concept shift and mixes classes | Theorem 2 and following text (arXiv 2107.13469): "concept shift is induced ... may mix the feature of all classes" |
| jeong2025 | Order normalisation + U-Net VAE + TTT; order normalisation gives most of the gain | Table 6: target F1 0.23 → 0.46 (order) → 0.46 (+recon) → 0.50 (+TTT), i.e. ~85 % of the gain. See A2 for the target-domain issue. |
| pctl2026 | Confidence predictor; small labelled target set | Sec. 2.1, 3.2. See A3 for the rest. |
| yoon2026biosfda | STFT band energy and SNR at BPFO/BPFI/BSF; online rescaling; SPIDER; ball class | Sec. 4.1-4.2, Table 2/3. See B5. |
| sdalr2025 | All numbers, classes, windowing, code | arXiv v1. See A8. |
| lessmeier2016 | Table 5: KA04, KA16, KA22 and all KI = "fatigue: pitting"; KA15, KA30 = "Plastic deform.: Indentations" | Verbatim, PDF p. 5-6 |
| lessmeier2016 | 6203; 64 kHz; 20 × 4 s; four conditions; 6 healthy; no rolling-element damage | "Damage at the rolling elements was not observed"; artificial damage also only on IR/OR. The manuscript could say Paderborn has no rolling-element damage at all. |
| lessmeier2016 | Kinematics | The paper says the manufacturers' geometries are "nearly identical, so that the characteristic kinematic frequencies do not vary more than 1-2%". Its example datasheet gives pitch 28.55 mm, 8 × 6.75 mm. |
| smith2015 | 06_results:311-312 lock-like behaviour making a definite diagnosis difficult | Verbatim: "the bearing frequencies appear to lock onto these shaft harmonics, making it difficult to establish a definite diagnosis" (fan-end SKF 6203; BPFO 3.053) |
| smith2015 | 03_data:36 BPFO "3.0531" | CWRU site table gives 3.0530; the closed form from its listed dimensions (d = 0.2656 in, D = 1.122 in, n = 8) gives 3.05312. Consistent with rule C13. Optional footnote. |
| randall2011 | Random slip 1-2 % | ScienceDirect intro excerpt: "typically of the order of 1–2%, both as a deviation from the calculated value and also as a random variation" |
| borghesani2013 | SES statistics under coloured noise and thresholds | Highlights: "Derivation of a statistical test (thresholds) for the identification of CS2 components" |
| iso15243 | Clauses 5.1 Rolling contact fatigue and 5.5 Plastic deformation | ISO 15243:2017 table of contents (iTeh sample) and SKF summary. 5.5.3 is "indentations from particles". |
| benjamini1995 / benjamini2001 | BH under positive dependence; BY under any dependence | Standard results; metadata checked (but see C1 for the DOI) |
| zhao2021udtl, liang2020shot, li2018ciddg, ozdenizci2020eeg, yang2021nrc, yang2022aad, antoni2007kurtogram, pedregosa2011sklearn | Generic attributions | Metadata checked (NRC pages not independently verified) |
| sehri2023uored, thuan2023hust, li2013jnu | Dataset facts | See B3, B8, B9 |

---

## D. Bibliographic metadata (`references.bib`)

| Entry | Problem | Fix |
|---|---|---|
| benjamini1995 | **DOI 10.2307/2346101 does not resolve**: doi.org handle API returns code 100, not found; Crossref 404 | `doi = {10.1111/j.2517-6161.1995.tb02031.x}` (Crossref: JRSS-B 57(1):289-300) |
| li2018ciddg | **Pages wrong**: bib 624-639; Crossref 647-663 (LNCS, ECCV 2018) | `pages = {647--663}` |
| lessmeier2016 | No DOI or volume; `pages = {05--08 July}` puts the conference dates in the pages field | `doi = {10.36001/phme.2016.v3i1.1577}`, volume 3, number 1 (Crossref: PHM Society European Conference 3(1), 2016); move the dates to `note` or remove |
| borghesani2013 | Issue missing | `number = {1}` |
| vieira2026 | OK: MSSP 258, 114640, Aug 2026 (Crossref) | Optional: the arXiv note may stay. The cited survey and quote are from v5 (6 Jul 2026), and earlier versions (v2) list three datasets, so make sure the published version matches. |
| knap2026leakagesafe | OK: published 2026-07-03, PHME 9(1):1-8 | none |
| sdalr2025 | OK: Neurocomputing 657, 131661 (online 2025-09-25). The title and author order are the Crossref ones. | See A8 |
| pctl2026 | OK: EiN 28(2), 2026, article 211797 (online 2025-10-19) | none |
| yoon2026biosfda | OK: Results in Engineering 30, 111105 (June 2026; open access) | none |
| jeong2025, wheat2024leakage, hendriks2022, smith2015, randall2011, matania2024leakage, matania2025, kapoor2023leakage, geirhos2020shortcut, thuan2023hust, sehri2023uored, li2013jnu, antoni2007kurtogram, zhao2021udtl (article 3525828 confirmed on IEEE Xplore), ozdenizci2020eeg, liu2021labelshift, yang2022aad, benjamini2001 | Match Crossref or the publisher | none |
| patent10168248 | Matches Google Patents | none |

---

## E. Suggested minimal edit list
1. 01_intro:69-70 and 02_bg:92-95: cite Vieira's PU repetition-wise result (Table 12) and Knap's PU Cross-Bearing Instance scenario as nearest neighbours to (iv), and narrow (iv) to the SFDA-paired, ten-split control.
2. 02_bg:115-116: restrict "In all of this work..." to SDALR-style condition transfer; note that Jeong and Bio-SFDA are cross-dataset.
3. 01_intro:34-35: PCTL supervises confidence and does not filter pseudo-labels. 02_bg:45: "predicted envelope spectrum". 05_gates "PCV-style": add a caveat or rename.
4. 02_bg:9-11 and intro:65: correct the 100-splits attribution (leakage uses 20/20/12 on three datasets).
5. 01_intro:16: add "and one did not state its split".
6. t1_datasets: CWRU f_s "12 (faults), 48 (normal)"; Paderborn conditions "4 (3 for adaptation)"; JNU speeds footnote.
7. 04_protocol:27: reword "not publicly available" (it is a Baidu Netdisk link).
8. Check the SDALR tables against the Neurocomputing version.
9. 02_bg:9: soften or support "change method rankings".
10. 06_results:314-315: reword the patent sentence.
11. 02_bg:114: cite or drop the "audits of SFDA stability" sentence.
12. bib: benjamini1995 DOI, li2018ciddg pages, lessmeier2016 DOI/volume/pages, borghesani2013 issue.
