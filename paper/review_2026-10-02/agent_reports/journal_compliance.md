# MSSP compliance check and journal-fit assessment

Date of check: 2026-10-02. Read-only: no project file was edited.
Manuscript checked: `paper/tex/main.tex` + `sections/*.tex`, `tables/*.tex`, built PDF `paper/manuscript.pdf` (24 pages, A4, elsarticle `preprint`), `paper/cover_letter.md`, `paper/data_availability.md`, `paper/coi.md`, `paper/credit.md`. (`paper/submission/` copies are byte-identical for the cover letter, declarations, main.tex and abstract.)

Primary sources (all fetched live on 2026-10-02):
- MSSP Guide for Authors: https://www.sciencedirect.com/journal/mechanical-systems-and-signal-processing/publish/guide-for-authors  (cited below as "GfA, <section>")
- Guidelines for Machine Learning Papers in MSSP, dated 5 December 2024: https://legacyfileshare.elsevier.com/promis_misc/mssp-guidelines-machine-learning-papers.pdf  ("ML-G")
- Guidelines for MSSP Papers on Signal Processing: https://legacyfileshare.elsevier.com/promis_misc/mssp-guidelines-signal-processing.pdf  ("SP-G")
- Elsevier Generative AI policies for journals, "Policy updated June 2026": https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals  ("AI-P")
- MSSP journal page (metrics): https://www.sciencedirect.com/journal/mechanical-systems-and-signal-processing

---------------------------------------------------------------------------------------------------

## 0. Headline findings (what needs action before submission)

| # | Severity | Item |
|---|---|---|
| 1 | HIGH | **Abstract word count is borderline.** 246 words counted from the LaTeX source (formulas and `\SI` as one word each), but **254** by whitespace-splitting the compiled PDF text (where "94.1 %" and "p = 0.001" split into separate tokens; MS Word counts the same way). Limit is 250. Cut to <= 235. |
| 2 | HIGH | **Research data: MSSP is an "Option C" journal.** Authors are *required* to deposit data in a repository, cite and link it, or explain why that is impossible. The manuscript says the ledger/artifacts are "provided to the reviewers" and will get a DOI "on acceptance". That does not meet the requirement at submission. Deposit (Zenodo / Mendeley Data / Figshare, reviewer-only private link is fine) now and cite as a `[dataset]` reference. |
| 3 | HIGH | **Highlights must be a separate editable file** with "highlights" in its name (`.docx`). The `highlights` environment in main.tex is not enough. The 5 highlights themselves pass (see 2.2). No such file exists in `paper/submission/`. |
| 4 | HIGH | **AI declaration needs the model/version, and a decision on figure captions.** Elsevier (June 2026) requires name of model/tool, **version** and developer when AI is part of research methods or data visualisation, and a caption disclosure for AI-assisted explanatory images. See section 7. |
| 5 | MED | **Declaration of competing interest must be completed in Elsevier's declarations tool and uploaded as .doc/.docx** at the "attach files" step (GfA, Declaration of competing interests). The in-manuscript section alone is not enough. |
| 6 | MED | **Human-only placeholders still open** in main.tex: author list, affiliations, corresponding author + e-mail, ORCID iDs (GfA, "Journal specific information": ORCID iDs "for all authors, where available"). The tex CRediT section has "Author 1 / Author 2" while `credit.md` lists only "Rafiur Rahman": reconcile. CLAUDE.md mentions a co-author who ran compute on a second Kaggle account; CRediT must cover that person. |
| 7 | MED | **Cover letter file contains the reviewer table and an internal "Note for the authors" below the signature.** Strip both before uploading as the cover letter. Replace "Research Paper" with MSSP's article-type name ("Standard Research Article"). |
| 8 | MED | **Data availability statement omits JNU** (used to reproduce SDALR, Table 1) and `data_availability.md` disagrees with the tex version (md lists "four datasets" incl. Jiangnan and the "predictive-maintenance-mcp" CC BY-NC-SA source; tex lists PU, HUST, CWRU, UORED). Make one authoritative statement. |
| 9 | LOW | SI units: `rpm` is used (03_data.tex, "1500 rpm", "900 rpm"); GfA requires SI or an SI equivalent. Add "(25 Hz)" / "(15 Hz)". |
| 10 | LOW | Reference formatting: journal names are not abbreviated per LTWA (GfA requires it); `lessmeier2016` has no DOI and a malformed `pages = {05--08 July}` field; datasets are not `[dataset]`-marked. |
| 11 | LOW | Abstract uses "SDALR" and "SHOT" without expansion (GfA: define non-standard abbreviations in the abstract at first mention). |
| 12 | INFO | Strategic: the paper is an *evaluation/leakage* paper whose own text says "We claim no new network, no new detector and no new adaptation algorithm." MSSP's ML and SP guidelines make conceptual novelty and "increase of knowledge" the test. The Vieira et al. precedent in MSSP helps; the cover letter should map explicitly onto ML-G and SP-G (section 8). |

---------------------------------------------------------------------------------------------------

## 1. Scope, article type, length

| Requirement (source) | Manuscript status |
|---|---|
| Scope: "signal and information processing and related topics in engineering dynamics and dynamical systems"; authors "must select the single best fitting subject area during manuscript submission"; subject area **A. Signal processing in machine/system health monitoring** (GfA, Aims and scope) | Fits A. Select A in Editorial Manager. Not in the "outside scope" list. |
| Article types: Standard Research Article; Long Research Article ("must, in their cover letter, provide clear justification for the reason(s) behind the extra length"); Short Communication (GfA, Article types) | **The guide gives no page or word limit for any type** (I searched the full text for "page", "word", "limit"; only the 250-word abstract, 85-character highlights and 1-7 keyword limits exist). Manuscript: 24 pages in single-column `preprint` layout, about 15,700 words including tables and references, 7 figures, 7 tables. The cover letter does not claim "Long Research Article". The guide's general rule "All manuscripts submitted to MSSP should be concise and of high clarity" (GfA, Article structure for MSSP, item 1) is the only length-related constraint. Expect reviewers to ask for cuts; if the editor classes it as long, the cover letter needs a justification sentence. |
| Peer review: single anonymized (GfA, Peer review) | Author names are visible to reviewers; the current "Anonymous" placeholder is only a draft state. |
| Submission declaration: not published, not under consideration elsewhere; preprints allowed (GfA, Submission declaration; Preprints) | Cover letter states this. SSRN free preprint posting is offered at submission (optional). |

## 2. Front matter

### 2.1 Abstract (GfA, Abstract: "does not exceed 250 words")
- Count method A (LaTeX source tokens, `\SI{94.1}{\percent}` -> "94.1%", `$p=0.001$` -> one token, formulas as typed): **246**.
- Count method B (whitespace split of the abstract text extracted from `paper/manuscript.pdf`): **254**.
- Verdict: **fails or passes depending on the counter; treat as non-compliant.** Trim at least 15 words (e.g., drop the "two mechanical folds" clause detail or the 8.9-point RF figure, which the highlights already carry).
- Other guide rules for the abstract: states purpose, procedures, main findings with statistical significance (yes: p = 0.001 and rho = 0.95 given), no references (none), "avoid non-standard or uncommon abbreviations... defined within your abstract at first mention": SFDA is defined; **SDALR and SHOT are not expanded**.

### 2.2 Highlights (GfA, Highlights: "3 to 5 bullet points, each a maximum of 85 characters, including spaces"; "Submit highlights as a separate editable file ... with the word 'highlights' included in the file name")
Exact counts (characters including spaces and punctuation):

| # | Text | Chars | <= 85 |
|---|---|---|---|
| 1 | Bearing-disjoint targets cut source-free adaptation accuracy by 37 points. | 74 | yes |
| 2 | The loss replicates on a second rig, for SHOT, and at a fixed operating condition. | 82 | yes |
| 3 | Ten time statistics identify same-class bearings in 508 of 508 recordings. | 74 | yes |
| 4 | A physics gate's gain tracks how many target recordings it can speak on. | 72 | yes |
| 5 | A non-adaptive forest also collapses: a calibration bar, not a remedy. | 70 | yes |

Number (5) is within 3-5; all within 85. **Gap: the separate editable file does not exist** (the highlights are only inside main.tex). Highlight 5 ("calibration bar, not a remedy") is slightly opaque out of context. Highlight 4's "speak on" is jargon.

### 2.3 Keywords (GfA, Keywords: "1 to 7 keywords... try to avoid keywords consisting of multiple words (using 'and' or 'of')")
Six keywords: rolling bearing; source-free domain adaptation; data leakage; bearing-wise evaluation; pseudo-label gating; envelope analysis. Count OK (6 <= 7). None contains "and"/"of". Compliant.

### 2.4 Graphical abstract (GfA: "encouraged", not mandatory; 531 x 1328 px (h x w) or proportionally more, readable at 5 x 13 cm; TIFF, EPS, PDF or MS Office; separate file)
`paper/tex/figures/graphical_abstract.pdf`: 11.2 x 4.5 cm vector PDF, aspect ratio 2.501:1 (matches 1328/531 = 2.501), fonts embedded (ArialMT, Arial-BoldMT). Compliant in format. **Policy point (AI-P, graphical abstracts): "General-purpose generative AI image tools must not be used to create graphical abstracts"; the FAQ table says to "mention the tool used in the image caption".** A script-generated vector graphic is not a generative image model, but because Claude wrote the script, say so plainly (section 7) or redraw it by hand in a vector editor to remove any doubt.

### 2.5 Title page (GfA, Title page)
Title is concise, no abbreviations or formulae: OK. Open: given and family names, affiliations with full postal address and country, corresponding author with e-mail (published in the article), ORCID iDs, present-address footnotes. All pending (human-only).

## 3. Tables, figures, equations, units

| Requirement (GfA) | Status |
|---|---|
| Tables: editable text, cited in text, numbered consecutively, captions, notes below the body, "Avoid vertical rules and shading", "use tables sparingly" | All 7 tables are booktabs LaTeX text, column specs have no `|`, no `\rowcolor`/`\cellcolor`, all have captions and are cited. Compliant. 7 tables with 7 figures is heavy against the "sparingly" advice; t4/t6/t7 could be merged or moved to supplementary. |
| Figures: separate files, logical names (Figure_1...), each cited, captions with brief title + description; vector EPS/PDF with embedded fonts; "Do not submit... multiple images or graphs combined into one file" | 7 vector PDFs, fonts embedded (Arial/DejaVu), all captioned and cited. Files are named `fig1_design.pdf`... : rename to `Figure_1` etc. for upload. Fig. 5 (panels a, b) and probably Figs 2-4 are multi-panel in one file; the guide's exception is only for images "intended to be compared to each other". Likely acceptable for multi-panel result plots but be ready to split. |
| Math: editable, numbered consecutively, variables italic, exp for powers of e | LaTeX; fine. |
| Units: SI, or give SI equivalent (GfA, Units) | `rpm` used without SI equivalent (03_data.tex lines 10-11). Fix. |
| Sections numbered 1, 1.1 ...; abstract unnumbered; cross-refer by number (GfA, Article sections) | Compliant (Sections 1-10; declarations unnumbered). |
| Appendices lettered A, B; equations (A.1) | No appendices; N/A. |
| Supplementary material: cited in text, submitted at the same time, labelled "Supplementary Table S1"; "will appear online in the exact same way as received" | S1-S4 are cited as "Supplementary S1..S4". Files are Markdown: convert to PDF/DOCX because they are published unformatted. |

## 4. References (GfA, References / Reference style)

- **Style: numbered, in square brackets, in order of appearance** ("Indicate references by adding a number within square brackets... Number references in the order they appear"). Manuscript: `elsarticle-num` -> compliant. (Caution: the guide's recommended LaTeX template section lists `cas-model2-names.bst`, which is name-year; the explicit reference-style text is numbered and Vieira et al., 2026 in MSSP cites as "[43]", so numbered is right.)
- Journal names must be abbreviated per LTWA: references.bib uses full names ("Mechanical Systems and Signal Processing", "IEEE Access"). Fix at proof stage or in the bib.
- DOIs "where available": 26 DOI fields among 32 entries. `lessmeier2016` has none (PHME 2016 paper has a DOI; verify on the PHM Society site before adding) and a bad `pages = {05--08 July}` field.
- Datasets should be cited as `[dataset]` references with repository, version, year, persistent ID (GfA, Data references: "encouraged"). Currently cited via the data papers only.
- "Every reference... must correspond to a real, existing source" and AI-P: "Inclusion of fabricated references may lead to rejection." The bib header says VERIFY marks were to be cleared; none remain. Do a last DOI-resolution pass (also for `knap2026leakagesafe` and `wheat2024leakage`).
- Reference management: preprints must be marked "preprint" + server + DOI unless a published version exists. Vieira et al. is cited with `note = {arXiv:2509.22267}` plus the final MSSP DOI: fine (final version used).
- MSSP-archive citations: SP-G says citing MSSP papers is "one indication" of fit. 7 of 32 references are MSSP (Vieira 2026, Hendriks 2022, Smith & Randall 2015, Randall & Antoni 2011, Borghesani 2013, Matania 2025, Antoni 2007): good.

## 5. Declarations

| Item | Guide requirement | Manuscript status |
|---|---|---|
| CRediT | "Corresponding authors are required to acknowledge co-author contributions using CRediT roles" (14 listed roles) (GfA, Author contributions: CRediT) | Section present with valid role names; placeholders "Author 1/2". `credit.md` has one named author with "Add co-authors". Must list each human author (and the person who operated the second Kaggle account if an author). |
| Competing interests | All authors must disclose; "The declarations tool should always be completed"; Word document from the tool uploaded at "attach/upload files" | Standard Elsevier wording present in tex and coi.md ("Confirm before submission"). **The .docx from the declarations tool is still needed.** |
| Funding | List sources; if none, "recommended" sentence: "This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors." | Exact recommended sentence is used. Compliant. Consider acknowledging free Kaggle GPU quota in a separate Acknowledgements section placed directly before the reference list (GfA, Acknowledgements); optional. |
| Data statement | "required to state the availability of any data at submission"; "Option C... you are required to: Deposit your research data in a relevant data repository; Cite and link to this dataset in your article; If this is not possible, make a statement explaining why" (GfA, Research data) | **Not met** (deposit deferred to acceptance). Public source datasets are fine to cite; the *derived* artifacts (frozen splits, 1246-row ledger, scripts, retained run artifacts) are the "research data" that must be deposited. Use a reviewer-only private link now, public DOI on acceptance. SP-G adds: "Reproducible research is an essential requirement for papers submitted to MSSP." The ledger/protocol approach is a strength; it must be visible to the editor at submission. |
| Code availability | not a separate heading in the guide (code counts as research data) | Present; "released with the supplementary material": include the repository link/DOI. |
| Suggested reviewers | **Not mentioned anywhere in the MSSP guide.** Editorial Manager may ask for them at submission (not verifiable without a live submission). | Six names in the cover-letter file. Considerations: Silva (Vieira et al.) and Dumond (Hendriks et al.; UORED) are authors of work the paper critiques or extends: defensible as subject experts but they are interested parties, and an editor may discount them; use institutional e-mail addresses; confirm none co-authored with you in 3 years; check the MSSP editorial board page so you do not propose a sitting editor. |
| Cover letter | Not required by the guide, except: Long Research Articles (justify length); Review/Tutorial/Braun papers (cite approval) (GfA, Article types) | Present; see section 9. |
| ORCID, corresponding author e-mail | required/expected (above) | pending |
| Ethics / human subjects / image manipulation | N/A (no humans, no photographs/micrographs; figures are data plots) | OK |

## 6. LaTeX template

- Guide (GfA, MSSP-specific, Manuscript preparation systems): "The use of the freely available LaTeX system is encouraged but not required. If selected, the use of the LaTeX els-cas-templates is recommended: LaTeX class file cas-sc.cls (single column)..." So `cas-sc` is *recommended*, `elsarticle` is not forbidden. Editable `.tex` source is required; "A PDF is not an acceptable source file"; double-column only permitted for LaTeX (GfA, File format).
- Manuscript: `\documentclass[preprint,3p,times]{elsarticle}` + `elsarticle-num`. `preprint` gives the single-column review layout; `3p` only matters for the final layout (harmless; standard practice is `preprint,review,12pt`). Compliant. A switch to `cas-sc` is optional and would require changing `\begin{highlights}`/frontmatter markup and the bst (cas-model1-num or equivalent for numbered refs, not the recommended names bst).
- Submit: main.tex + sections/ + tables/ + references.bib (or compiled .bbl) + figure files separately; editable files are required for typesetting.

## 7. Generative-AI declaration (Elsevier policy, updated June 2026; GfA, Declaration of generative AI use)

### 7.1 What the policy requires (exact)
- Placement: "a separate declaration section at the end of your manuscript, immediately before the references" (AI-P, FAQ). GfA: "should be placed in a new section before the references list."
- Suggested title (AI-P): "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process". (The 2023-25 wording was "...in the writing process", which the manuscript still uses.) The policy says "titled for instance", so it is not rigid, but update to the current wording.
- Suggested statement: "During the preparation of this work, the author(s) used [NAME OF TOOL / SERVICE] in order to [REASON]. After using this tool/service, the author(s) reviewed and edited the content as needed and take(s) full responsibility for the content of the published article."
- Disclosure should include "the name of the AI tool used, the purpose of its use, and the extent of their oversight."
- **Research-process use goes in Methods, not (only) the declaration:** "Where AI tools are used as part of the research process rather than manuscript preparation, this use should be described in detail in the Methods section." FAQ: the policy "does not prevent the use of AI tools in formal research design or research methods, including but not limited to study design, code development and data analysis... they should be described as part of the methodology." "If authors write or edit code using AI tools as part of their research, they should declare this in detail in the Methods section and follow field-specific standards." Reproducibility standard: "name of the model or tool, the version used, and the developer or manufacturer".
- Data visualisations: AI may be used "only when the visual output is directly derived from underlying data... via reproducible analytical, computational, or statistical methods that are clearly reported within the Methods section", disclosing "the name of the model or tool, the version used, and the developer" in Methods.
- Explanatory images (flow charts, schematics): permitted; "The use of AI tools should be disclosed in the caption of each image (including the specific tool, version, and how the tool was used) and in the general AI disclosure statement."
- Graphical abstracts: "General-purpose generative AI image tools must not be used"; mention the tool in the image caption.
- Not permitted: listing AI as author; fabricating or altering data/references; "Generating sections of a manuscript without genuine intellectual contribution from the author" is listed as *inappropriate use*. "AI tools must never be used as a substitute for human critical thinking, expertise and evaluation... only applied with human oversight and control."
- Reviewers/editors may not upload manuscripts to AI tools (irrelevant to authors, but confirms confidentiality norms; do not paste the unpublished manuscript into third-party AI tools beyond those already used, per the "check the terms and conditions" duty).

### 7.2 Manuscript status
- Declaration (99_declarations.tex) is placed correctly (after Data/Code availability, before `\bibliography`), names the tool ("Claude (Anthropic)"), purposes (draft/edit text, write analysis and figure code, check numerical consistency), and has the "reviewed and edited ... take full responsibility" sentence. **Compliant in form.**
- Methods paragraph "AI-assisted execution" (04_protocol.tex line 121) exists. **Compliant with the "describe in Methods" rule, and this is exactly what Elsevier expects.** Missing: **model name and version** (e.g., the specific Claude model ID and the Claude Code CLI version used; the ledger/commit trailers probably hold them), and the access route. Add them; the policy asks for "name of the model or tool, the version used, and the developer".
- **Does saying the AI "executed" analyses raise a policy problem?** No rule prohibits it: the policy explicitly allows AI in "code development and data analysis" provided it is described in Methods and reproducible. The wording that carries risk is not "executed" but (a) "draft ... text": the policy treats substantive drafting without genuine author contribution as inappropriate, so the claim "the authors reviewed and edited" must be literally true and ideally the Methods paragraph should say who decided the claims (the paragraph already says AI "did not choose hypotheses, decision rules or operating points"); (b) the CRediT list credits human authors with Software, Formal analysis, Investigation and Writing - original draft: keep it, because AI cannot be credited, but the authors must be able to defend those roles; (c) "take full responsibility" must be accurate.
- Suggest rewording (keeping the facts): in the declaration, "...used Claude (Anthropic, model <ID>, via Claude Code <version>) to draft and edit text, write analysis and figure code, and cross-check numbers against retained artifacts; analysis use is described in Section 4." Keep the sentence that no hypothesis or decision rule was AI-chosen in Methods.
- Figures: the 7 figures are data plots produced by scripts (`paper/figures/build_figures.py`, `build_schematics.py`) that Claude wrote. This is the "data visualisations from reproducible methods" category (permitted; disclose in Methods: add the tool/version there and say the plots are produced by released scripts). `fig1_design.pdf` and the graphical abstract are schematics (the "explanatory image" category): the policy's literal reading asks for a caption disclosure for AI-supported explanatory images. Because the schematics are script-drawn, the lowest-risk path is one added caption sentence ("Drawn by a script written with Claude; all content verified by the authors") or hand redrawing.
- Reference-checking by AI: policy FAQ says "If these or any other AI tool are used to select, collate, generate or edit references, this should be declared in the manuscript." The project verified bibliographic data from primary sources; if Claude assembled or edited the bib, add "and references" to the declaration purposes.

## 8. MSSP-specific editorial policies

### 8.1 What exists (verified)
There is no single "desk-reject CWRU-only" rule, but two official guideline documents state the policy; both are linked from the Guide for Authors ("Guidelines for MSSP Papers on Signal Processing", "Guidelines for Machine Learning Papers in MSSP").

**Guidelines for Machine Learning Papers in MSSP (5 Dec 2024), summarised:**
- MSSP receives "a large number" of ML/"soft computing" papers; "many of these papers are rejected without review" because they "do not contribute to engineering knowledge".
- Commonest reject pattern: a simple rig (e.g. rotor-bearing), feature extraction + classification; "not sufficient motivation ... to base the paper on a 'new' feature or a 'new' classifier, particularly if the word 'new' only means the algorithm or feature has not been applied in the precise context before": "rejected without review".
- Three acceptable bases: (1) a new application context or a "very interesting experimental case study" with a data set having "some new aspect not addressed by existing data e.g. the Case Western Reserve benchmark data" (so CWRU is cited as the example of *existing* data that no longer qualifies as novelty), with principled hyperparameters and rigorous validation ("not enough training data and therefore generalisation is not confirmed" is the commonest validation complaint); (2) a new feature, benchmarked on more than one data set (at least one experimental) against state-of-the-art features, with "classifiers used with the old features ... demonstrably optimised"; (3) a new classifier/regressor benchmarked on more than one data set with all hyperparameters optimised "as far as possible".
- Principle: "if a paper based on machine learning is not principled enough to meet the standards of both a Machine Learning journal and MSSP, it is not principled enough for publication in MSSP." Authors "must always provide" (a) a clear explanation of why the approach is theoretically suitable for the MSSP application and (b) experimental evidence of superiority "and how/why (note that very high-level measures like accuracy are usually not sufficiently convincing as they depend on the choice of hyperparameters in the benchmark techniques)".

**Guidelines for MSSP Papers on Signal Processing (undated PDF), summarised:**
- "Direct application of an existing method to a database is considered as a case study, which is rarely accepted unless it evidences some breakthroughs"; "Case studies are usually not considered ... because of the difficulty of generalizing from the single case ... it should clearly demonstrate an increase of knowledge, a better understanding of a scientific problem, or an impetus for research."
- Novelty must be "conceptual"; "proving the feasibility of the approach ... is not sufficient per se".
- Experimental results on "industrial or laboratory data" strongly recommended; comprehensive benchmark, "analysis on at least two different datasets"; "The validation of a proposed method on only one example is often insufficient".
- Reproducible research "is an essential requirement" (applies to "simulated data and to the setups used in benchmarks").
- CWRU paragraph: CWRU data are "known for presenting various degrees of difficulty"; the Smith and Randall 2015 MSSP benchmark study is the reference "against which any new proposed method should be tested"; "Information on the signals which are processed in the database is compulsory"; method benefit is "all the more convincing as it is able to resolve several difficult cases" and demonstration "on at least one another data set is recommended".

**Editorials:** I searched for a standalone MSSP editorial on data-driven diagnosis papers and did not find one; the two guideline PDFs (the ML one is the 2024 revision of an older version at media.journals.elsevier.com/content/files/machine-learning-04180327.pdf) are the official statement. No separate "desk-reject CWRU-only" policy was found: the CWRU-specific text is in SP-G (above) and ML-G (CWRU as the example of a no-longer-novel dataset).

### 8.2 How this manuscript maps
| Guideline expectation | This paper |
|---|---|
| Not a "new classifier/feature on CWRU" paper | Correct: evaluation methodology, no new method; no CWRU-only data (Paderborn + HUST for adaptation; CWRU, UORED, JNU auxiliary). |
| More than one data set, at least one experimental | Two real rigs (Paderborn, HUST) for the main claims, plus CWRU/UORED for gates and slip. Meets "at least two datasets". |
| Rigorous validation / "generalisation confirmed" | Ten pre-registered bearing splits, split-level p-values with BH correction, A/A floor. Strong. |
| Hyperparameters of compared methods tuned "as far as possible" | **Exposure.** SDALR and SHOT are run "from their authors' released code" with the described adapters; the RF baseline is simple. For an evaluation paper this is defensible (the target is the protocol, not a ranking), but say so explicitly and show the RF/SHOT sensitivity if available. Reviewers applying ML-G will raise it. |
| Why theoretically suitable for MSSP application | Kinematics resolved per bearing, envelope gates, false-acceptance on 480 healthy recordings, cage-slip measurement: the signal-processing content that makes it an MSSP rather than an ML paper. Lead the introduction and cover letter with it. |
| "Conceptual novelty"; "innovative contributions clearly spelled out" (GfA MSSP guideline 6) | Intro says "The novelty is narrow ... We claim no new network, no new detector and no new adaptation algorithm". Honest and consistent with the project rules, but it hands an editor a desk-reject sentence. Frame the novelty as an "increase of knowledge" (SP-G's own criterion for case studies): measured mechanism (bearing identity recoverable in 508/508 recordings), a bound (oracle ceiling), and a safety measurement for physics gates. |
| "Very high-level measures like accuracy are usually not sufficiently convincing" | The paper's own subject (accuracy collapse) is consistent with this; keep mechanism evidence (probes, purity, decomposition) prominent. |
| Reproducibility "essential" | Ledger, frozen protocol, hashes: strong, but must be deposited at submission (section 5). |

## 9. Cover letter (`paper/cover_letter.md`)
- Content is strong on scope ("Why MSSP") and on honesty about failed hypotheses. Problems: (i) it is long (about 700 words); editors read the first paragraph; (ii) it does not map to ML-G/SP-G: add three sentences: not a new-classifier paper; two real rigs plus auxiliary rigs; reproducibility artifact deposited; (iii) "Research Paper" -> "Standard Research Article"; state subject area A; (iv) cover letter file contains "Suggested reviewers" table and an internal "Note for the authors": split those into a separate field or file; (v) the claim that the work "extends the bearing-wise evaluation argument published in this journal to the source-free setting, which that work explicitly placed out of scope" depends on what Vieira et al. wrote (round 4 of the project reportedly quoted it); re-verify the quote against the final version of record (MSSP 258, 114640); (vi) the line "all authors approve the submission" is a Submission-declaration item (GfA): fine.

## 10. Journal fit

### 10.1 MSSP precedents (verified)
- **Vieira, Bauler, Rosa, Silva, "Towards a more realistic evaluation of machine learning models for bearing fault diagnosis", Mech. Syst. Signal Process. 258 (2026) 114640, doi:10.1016/j.ymssp.2026.114640**: confirmed in MSSP (ScienceDirect page: article type "Full length article", online 8 July 2026, issue date 15 Aug 2026, open access; arXiv 2509.22267). Datasets CWRU, Paderborn, UORED-VAFCLS; bearing-wise split, multi-label reformulation, double cross-validation. Its Table 1 surveys 2025 ML bearing papers. This is the closest MSSP precedent and the nearest neighbour the paper already cites; it proves the editors accept leakage/evaluation-methodology papers.
- **Hendriks, Dumond, Knox, "Towards better benchmarking using the CWRU bearing fault dataset", Mech. Syst. Signal Process. 169 (2022) 108732**: in MSSP; first identified bearing-level leakage in CWRU splits.
- **Smith and Randall, "Rolling element bearing diagnostics using the Case Western Reserve University data: A benchmark study", MSSP 64-65 (2015) 100-131**: in MSSP; named in SP-G as the reference benchmark study.
- MSSP also publishes source-free DA for faults (e.g., "An adaptive source-free unsupervised domain adaptation method for mechanical fault detection", MSSP 228 (2025), S0888327025001761). So the topic is in scope; the delta is evaluation under bearing-disjoint targets.

### 10.2 Metrics (as displayed on the journal pages, 2 Oct 2026; IFs for IEEE/SHM from aggregator snippets, less reliable)
| Journal | IF | Notes |
|---|---|---|
| MSSP (Elsevier) | 10.2 (CiteScore 17.6) | 11 days to first decision (journal page); single anonymized review; open access optional; no stated page limit |
| Reliability Engineering & System Safety | 13.7 (CiteScore 21.9) | scope lists "methods and applications of automatic fault detection and diagnosis"; 7 days to first decision, 201 days to acceptance; OA APC USD 4,750 |
| IEEE Trans. Industrial Informatics | about 9.8 (aggregator, JCR 2025) | regular papers: 10 pages at submission, 12 final, overlength from p. 11 at USD 250/page (from search snippets; verify at IEEE-IES site) |
| IEEE Trans. Instrumentation and Measurement | about 7 (aggregator) | 8 free pages, overlength charges USD 265/page (search snippets) |
| Engineering Applications of AI (Elsevier) | 9.0 (CiteScore 11.7) | scope includes "intelligent fault detection... case studies or benchmarking exercises"; **desk-rejects** papers lacking a stated AI contribution, with undefined acronyms in title/abstract, or not single-column |
| Journal of Sound and Vibration | 5.8 (CiteScore 10.2) | fundamental sound/vibration; data-driven diagnosis/evaluation is peripheral |
| Structural Health Monitoring (Sage) | about 5.7 (aggregator) | civil/structural focus |

### 10.3 Assessment
MSSP is a defensible and probably the best first target, for these reasons:
1. Scope subject area A and the "signal processing in machine health monitoring" core; the paper's SP content (per-bearing kinematics, envelope gates, false-acceptance on healthy bearings, cage slip) is what lifts it above an ML application paper.
2. Direct precedent: Vieira et al. 2026, Hendriks et al. 2022 and Smith and Randall 2015 are all MSSP evaluation/benchmark papers on exactly these datasets; reviewers will include their authors' community.
3. Highest IF among the realistic bearing-diagnosis venues except RESS, fast first decision, no length cap.
4. Both guideline PDFs *favour* rigour, reproducibility and multi-dataset validation, which is this paper's strength.

Risks at MSSP: (a) the "no new method" posture and the "case study / feasibility is not enough" language; (b) ML-G hyperparameter-fairness complaint about SHOT/SDALR/RF; (c) a possible "belongs to ML venue" view because the headline is about SFDA protocols. Mitigation: cover-letter mapping (section 9), keep the SP content in the first two pages of the abstract/intro.

Alternatives, in order of preference if rejected:
- **RESS** (higher IF, fault diagnosis in scope; reliability framing: "does the diagnosis hold on an unseen unit"); Elsevier Article Transfer Service from MSSP is available (GfA, After receiving a final decision) and keeps the review history. Weakness: little bearing-signal-processing culture, so the kinematics/gating sections would be undervalued.
- **Engineering Applications of AI** (explicitly accepts "benchmarking exercises" and "intelligent fault diagnosis"): but its desk-reject conditions (acronyms undefined in title/abstract, abstract must state "the contribution in AI") need an abstract rewrite; evaluation/negative-result papers are in a grey zone.
- **IEEE TII / TIM**: large readership for SFDA diagnosis papers, but a 10-page (TII) or 8-free-page (TIM) double-column format would force cutting a 24-page paper by more than half; TIM's measurement/instrumentation framing fits the kinematics and signal-statistics parts; negative-results acceptance is lower.
- **JSV** and **SHM**: poor fit (fundamental vibration; civil SHM).

## 11. Pre-submission checklist (ordered)
1. Cut abstract to <= 235 words; expand or remove SDALR/SHOT.
2. Create `highlights.docx` with the 5 bullets (or revised).
3. Deposit data/code/ledger (private reviewer link ok), add `[dataset]` reference and the link to Data availability; reconcile tex vs `data_availability.md` (add JNU).
4. Add model ID/version to the AI Methods paragraph and declaration; retitle the section "Declaration of generative AI and AI-assisted technologies in the manuscript preparation process"; add caption/Methods lines for script-drawn schematics and the graphical abstract; say whether references were AI-assisted.
5. Fill authors, affiliations, corresponding e-mail, ORCIDs; fix CRediT for every author; run Elsevier's declaration-of-interests tool and upload the .docx.
6. Replace `rpm` with Hz equivalents; apply LTWA journal abbreviations and fix `lessmeier2016`.
7. Rename figures `Figure_1..7`; confirm multi-panel files are acceptable; convert supplements S1-S4 from Markdown to PDF.
8. Rewrite the cover letter (<= 1 page, article type, subject area A, ML-G/SP-G mapping); move reviewers to the Editorial Manager field; drop the internal note.

## 12. What I could not verify
- No standalone MSSP editorial on data-driven diagnosis was found (guideline PDFs only).
- Whether Editorial Manager for MSSP currently requires suggested reviewers (not in the guide).
- IF values for TII, TIM, SHM come from aggregator search results; the Elsevier journals' IFs (MSSP 10.2, RESS 13.7, EAAI 9.0, JSV 5.8) come from the journal pages. IEEE page limits come from search-engine snippets of IEEE pages.
- The DOI for Lessmeier et al. 2016 (not added; verify at the PHM Society site).
