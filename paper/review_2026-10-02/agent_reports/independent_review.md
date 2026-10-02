# Referee report: "Bearing-wise evaluation of source-free domain adaptation: leakage and the limits of physics gating"

Submitted to: Mechanical Systems and Signal Processing
Reviewer expertise: vibration-based bearing diagnostics, envelope analysis, transfer learning / SFDA, experimental statistics
Material read: `paper/tex/main.tex`, `sections/00_abstract.tex` to `10_conclusions.tex`, `99_declarations.tex`, `tables/t1`–`t7`, and figures 2 and 5. Line references are file:line in `paper/tex/`.

---

## 1. Summary

The paper re-evaluates a published source-free domain adaptation (SFDA) method for bearing diagnosis (SDALR) on Paderborn. It uses a paired design: one source model trained on 3/3/3 healthy/outer/inner specimens is adapted both to the same specimens at another operating condition ("leaky") and to the complementary specimens ("clean"). Accuracy falls from 94.1 % to 56.8 % on two fixed folds, and by a median of 36.2 pp over ten random 3/3/3 splits. The loss reappears for SHOT (21.7 pp), for non-adaptive random forests, on a second rig (HUST, 33.5 pp, where bearing size changes as well), and in a same-condition random-forest control (29.7 pp). The authors attribute the collapse to a specimen-level shortcut. Within-class linear probes separate individual bearings almost perfectly from source features (507/508) and from ten time statistics (508/508), and the adapted model gives one label to each unseen specimen. An oracle pseudo-label filter recovers a median 82 % of the collapse. Envelope-based kinematic gates have very low false acceptance (0–9/480 healthy recordings, against 214/480 for a raw-spectrum band rule) but certify only about 20–24 % of faulty recordings. Inside the loop the envelope gate adds a median 4.5 pp, and its gain correlates with coverage across splits (ρ = 0.95). A cage-slip measurement and a list of seven reporting recommendations complete the paper.

## 2. Significance and fit

The central empirical message matters and is well supported: same-specimen evaluation hugely inflates the accuracy of cross-condition SFDA on Paderborn. The effect is large (median 36 pp), it is positive in every one of 10 splits, it appears for two adaptation methods and several non-adaptive baselines, and it is reproduced on a second rig. The paired design, the target-label-free checkpoint policy, the A/A determinism check, the reporting of a failed hypothesis and a strong shallow baseline are all above the usual standard of this literature. A reviewer from the diagnostics community will welcome them. The reporting checklist (Section 8) is useful.

The novelty is narrower than the abstract suggests, and the paper says so (01:63–70). That bearing overlap inflates accuracy is established by Hendriks, Wheat, Vieira and Knap. What is new:
- (a) the result for SFDA specifically;
- (b) the oracle pseudo-label reference;
- (c) false-acceptance characterisation of physics gates;
- (d) the same-condition control.

Of these, (a) is weakened by the paper's own evidence that the collapse is not SFDA-specific (Major 4). (b) and the coverage analysis are in part accounting identities rather than findings (Majors 5, 6). (d) uses only a random forest. The mechanistic claims ("identity", "the shortcut is in the signals", "a representation-level remedy cannot address the root cause") go beyond what the probes show (Major 2).

On fit with MSSP, the signal-processing content is thin and in one respect works against the paper. The classifier input (2048 samples, 0.8 shaft revolutions) cannot carry the kinematic signature that the paper frames as the alternative to "identity" (Major 3). The envelope detector is described as deliberately simple, yet its coverage is presented as "a property of the data" (Major 8).

With the remedies below the paper could be a strong benchmarking contribution of the kind MSSP publishes (cf. Smith & Randall 2015). In its current form the mechanistic and SFDA-specific claims are not identified by the design, and the manuscript has too many internal contradictions to accept.

---

## 3. Major concerns (ranked by severity)

### M1 [critical]. The leaky–clean difference and the oracle decomposition are not identified as stated

**Where.**
- 01:42–43 and 04:19–21 ("so the leaky–clean difference … is attributable to bearing overlap alone").
- Fig. 1 caption (04:9–10, "their difference isolates bearing overlap").
- 02:26–27 ("differ in bearing overlap and nothing else").
- Eq. 1 and 04:72–77.
- 06:154–155 ("half the collapse lies in the source representation").
- 10:23–24 ("the remainder lies in the representation and is beyond any filter").

**Why it matters.**
1. `a_leaky` is measured on the source specimens and `a_clean` on different specimens. The difference therefore contains (i) the effect of having seen the specimen and (ii) the difference in intrinsic difficulty between the two specimen sets: damage mechanism, damage extent, manufacturer and recording session.
2. The paper concedes this in 07:60–62 and 09:25–27 ("The design controls the operating condition exactly, not the mechanism or the difficulty of the individual specimen"). That concession directly contradicts the "overlap alone" sentences above.
3. The manufacturer confound is real and is not discussed. By 03:29–34, KA04, KA15, KI16 and KI21 are FAG (28.55 mm pitch) and the remainder are IBU/MTK (29.05 mm). A random split therefore also changes the manufacturer mix of each class.
4. Damage extent (Lessmeier et al. give a severity level per specimen) is never mentioned anywhere in the manuscript.
5. For a single split, Δ_leak is not attributable to overlap. Averaged over uniformly random draws, the difficulty term averages out, but only approximately. Outer-race specimens are in the source with probability 3/5 and in the clean target with probability 2/5, so the averaging is not balanced.
6. The decomposition has the same flaw in a sharper form. `a_leaky − a_oracle` subtracts an accuracy on specimen set S from an accuracy on specimen set C. It therefore contains the S-vs-C difficulty difference, not only "what the source representation carries".
7. The negative values of this term show it is not a representation quantity: on S04 the share is 222 %, and on fold A it is 101 %, i.e. a_oracle > a_leaky. A quantity that can be negative because the clean specimens are easier than the source specimens cannot be read as "damage in the representation".

**Remedy (all from saved per-window predictions; no new training).**
- **Within-specimen contrast.** Across the 10 splits plus 2 folds, every one of the 17 specimens appears in the source set in some splits and in the clean target in others. For each specimen b, compute accuracy on b when b was in the source (leaky arm) and when it was unseen (clean arm), averaged over splits. The paired difference per specimen is a seen-vs-unseen effect that holds the specimen, and therefore its mechanism, extent and manufacturer, fixed. Report it per specimen and per class, and test it with specimens as the unit (17 units; sign test or Wilcoxon). This also answers M7: it generalises to a population of specimens, not of overlapping splits.
- Rewrite every "overlap alone" sentence as an estimand averaged over random source draws, and state the difficulty term explicitly.
- For Eq. 1, rename the second term ("residual not recovered by the oracle filter on this specimen set"). Drop "lies in the source representation" (06:155, 07:19, 10:24). Better, compute the decomposition per specimen with the contrast above (oracle on b when unseen vs leaky on b when seen).
- Tabulate damage extent, mechanism and manufacturer per specimen in the main text (not only S3), and show Δ per specimen against these covariates.

### M2 [critical]. "Identity" is shown to be identifiable, not to be what the classifier uses; the alternative of under-sampled damage-signature variability is not excluded

**Where.**
- 00:7–9 ("The shortcut is in the signals").
- 01:21–24, 01:48–51.
- 06:130–139 ("assigning one identity-level label to each specimen").
- 06:269–292; 07:4–12 ("identity … is a perfect one").
- 10:14–17; highlights 3 (main.tex:35); 10:37 ("learned which bearing it is listening to").

**Why it matters.**
1. A within-class probe that separates three specimens shows that between-specimen variance is large relative to within-specimen variance. It does not show that the decision rule uses specimen-specific features *instead of* fault physics.
2. Two hypotheses predict the same block labelling (purity 1.0) and the same collapse:
   - (A) the classifier latches onto specimen- or session-specific features (a shortcut);
   - (B) with three specimens per class, the class-conditional distribution of the genuine damage signature (extent, location, mechanism, impulse content) is under-sampled. An unseen specimen's damage signature then falls in another class's region.

   Hypothesis B is not "leakage" in the Geirhos sense; it is a sample-size problem in specimens.
3. Purity 1.0 (06:130–139) is also what a *correct* fault classifier produces, since one label per specimen is the right answer. Only the wrongness of the label is informative, and that is what Δ_leak already measures. The purity analysis is therefore descriptive. KI04 labelled "normal" is just what B predicts for a low-extent inner-race damage.
4. The paper's own evidence argues against A as the whole story:
   - Unseen *healthy* specimens transfer almost perfectly (recall 99.9 → 98.2 %, 06:106). The probe is per class (06:270–271), so presumably healthy specimens are equally identifiable. If they are, identifiability coexists with perfect transfer, which falsifies "identifiable ⇒ shortcut". Report the probe result per class.
   - The forest on the ten time statistics, the feature set with *perfect* identity (508/508), has the *best* clean accuracy of the forests (63.6 % vs 52.6 % for spectral bands, Table 4). The probe narrative predicts the reverse.
   - The paper itself moves to "specimen-level damage signature … not a generic identity of every bearing" (06:112–113). That is hypothesis B. The abstract, introduction, highlights, discussion and conclusions still argue A.
5. One of the ten statistics is the signal **mean** (06:279). For an AC-coupled piezoelectric accelerometer through a charge amplifier, the DC mean is a property of the acquisition chain and the session, not of the bearing. A perfect probe may be partly a DC-offset or gain fingerprint, which would make "identity" a session artefact. This needs checking before "property of these signals" (06:281) is asserted.
6. The binomial p < 10^-200 (06:280) treats 508 recordings as independent. 04:104–105 states that recordings of one bearing are not independent. The effective sample for "specimens are separable" is the number of specimens.

**Remedy.**
- (i) Report the probe accuracy per class (healthy / outer / inner), at window level as well as recording level, and say how windows are aggregated to a recording.
- (ii) Probe ablations: drop `mean`; each statistic alone; amplitude-normalised statistics only (kurtosis, skewness, crest, shape, impulse). This is light CPU work.
- (iii) A within-specimen negative control: probe separability of arbitrary groups of recordings *within* one specimen at one condition. If those are also separable, the probe measures session/recording heterogeneity rather than specimen identity.
- (iv) Discriminate A from B with a specimen learning curve on the random forest (cheap, CPU or Kaggle CPU). Use leave-k-specimens-out with 1, 2, 3, 4 (and 5 for healthy/inner) source specimens per class, and plot clean accuracy against k.
  - Under B, clean accuracy rises with k.
  - Under A, it rises little, because identity remains a perfect shortcut at any k.

  This is also the experiment 08:43–45 calls "the obvious next experiment". It is feasible on Paderborn and would convert the main mechanistic claim from rhetoric into a measurement.
- (v) Relate probe strength to collapse across the three forest feature sets.
- (vi) Make the framing consistent throughout: "between-specimen variability that three specimens per class do not span", not "identity" or "memorisation".

### M3 [critical for MSSP]. The classifier input cannot represent the kinematic fault signature, so "identity vs physics" is not a fair contest

**Where.** 04:24–30 (2048-sample windows); 06:71–72 (forest on "envelope-spectrum features"); 01:20–24; 07:9–10.

**Why it matters (compute the governing quantities).**
- At 64 kHz a 2048-sample window lasts 32 ms. At 1500 rpm (25 Hz) that is **0.8 shaft revolutions**, about **2.5 outer-race impacts** (BPFO ≈ 3.07 × 25 = 76.8 Hz) and about 3.9 inner-race impacts.
- Envelope-spectrum resolution is 1/0.032 s = **31 Hz**. BPFO (77 Hz) falls near bin 2.5, and BPFO and BPFI (123 Hz) are about 1.5 bins apart. The ±2-shaft-order sidebands that identify inner-race damage are unresolvable.
- A model fed such windows cannot learn the periodicity that defines the fault classes. It can only learn spectral shape, resonance excitation and amplitude statistics, and those are precisely the features that differ between specimens and sessions.
- If the "envelope-spectrum" forest features are computed on the same 2048-sample windows, the 33.5 pp collapse of that forest says nothing about whether kinematic envelope physics transfers across specimens.
- The gates, by contrast, use the full 4 s record (0.25 Hz resolution). The paper therefore compares a physics-blind classifier with a physics detector and attributes the classifier's failure to "identity".
- The window contract is SDALR's (04:26–27), which is legitimate for re-evaluating SDALR. The general conclusions ("any source-trained classifier", 06:281–282; "the mechanism … sits in the data", 10:14) are then unsupported.

**Remedy.**
- (i) State these quantities in Section 4.
- (ii) Say on what window the forest envelope-spectrum features are computed.
- (iii) Run the bearing-disjoint split once with a forest (or logistic regression) on **record-length, order-domain envelope features**: amplitudes at the first harmonics of BPFO/BPFI/shaft in orders, from the full 4 s record. This is cheap and needs no GPU.

If that classifier also collapses, the paper's thesis is greatly strengthened. If it does not, the conclusion becomes "the collapse is a property of short-window, physics-blind inputs", which is a different and very useful MSSP message.

### M4 [critical for the framing]. The SFDA-specific motivation is never tested, and the evidence points the other way

**Where.** 01:27–31 ("SFDA deserves separate scrutiny … the procedure sharpens a decision that was never about the fault"); the title; 00:1–2; 10:17–18 ("Adaptation cannot correct this, because it refines the source model's own decisions"); 09:42–44.

**Why it matters.**
- The introduction motivates the study by a mechanism specific to SFDA: adaptation amplifies a source shortcut.
- The results show the opposite or nothing:
  - adaptation *adds* 2.2–5.4 pp on clean targets (06:48);
  - non-adaptive forests collapse by similar amounts and beat SDALR on clean targets (07:40–45);
  - the same-condition control was run only with a forest (09:42–44, "whether adaptation amplifies, preserves or reduces the loss … is not measured").
- No deep source-only arm appears in Table 4.
- The phenomenon is therefore about source training on few specimens. SFDA is affected by it but does not cause it.
- The oracle arm also contradicts 10:17–18: when given correct labels, adaptation recovers 82 % of the gap. Adaptation *can* move the representation; what fails is the label signal.

**Remedy (from existing logs).**
- 04:63–64 says the pre-update target accuracy is logged for every arm. That is the source-only accuracy on the leaky and clean targets for every split and fold.
- Report source-only Δ_leak beside SDALR and SHOT Δ_leak (Table 3/4). Report the difference Δ_leak(SFDA) − Δ_leak(source-only) as "amplification by adaptation", with a split-level test.
- Then rewrite the introduction motivation (01:27–31) and the conclusions to match the measured answer. If amplification is near zero, say so in the abstract. That is an important result, and it should also reshape the title (e.g. "Bearing-wise evaluation of cross-condition bearing diagnosis with source-free adaptation …").

### M5 [major]. The coverage–gain correlation (ρ = 0.95) is close to an accounting identity, depends on target labels, and is driven by four specimens

**Where.** 00:12–13; highlight 4 (main.tex:36); 06:194–207; 06:258–264; 07:25–31 ("a quantity that can be computed from the target recordings alone, before adapting anything"); 08:26–27; 10:28–29; Fig. 5b.

**Why it matters.**

1. **Mechanical relationship.** The evaluation is transductive: accuracy is measured on the very target windows whose pseudo-labels the gate filters. The gate only acts on recordings it certifies, and it is right 96–100 % of the time when it speaks (06:199–200). The gain is therefore approximately (share of target windows on certified recordings that the ungated model mislabels) × (fraction corrected), plus any spill-over to uncertified recordings. A strong correlation between "share certified" and "gain" is close to guaranteed. It is not evidence that coverage is "what sets the size of the gain" in any explanatory sense. The headroom-partialling analysis (06:204–207) does not address this, because headroom is not the competing explanation; the identity is.
2. **Not label-free.** Coverage is defined as the share of *faulty* target recordings certified (06:198, Fig. 5b axis). Computing it requires knowing which target recordings are faulty, i.e. target labels. The claim that it "can be computed from the target recordings alone" (07:30, 10:29) is false as defined. The label-free analogue is the share of *all* target recordings receiving any fault verdict, which includes false acceptances.
3. **Not ten independent points.** Only five real-damage specimens are ever certified at the adaptation conditions, and four of them more than once (KA04, KA16, KI16, KI18; 06:196–198). Coverage of a split is essentially a count of how many of these four sit in its clean target. The ten splits share specimens, so ρ = 0.95 with p = 2 × 10^-5 (and partial ρ = 0.98, p = 1.5 × 10^-6) treats as exchangeable ten points that are largely determined by membership of four specimens. Partial-Spearman p-values at n = 10 are also approximate at best. The precision reported is not warranted.
4. **Noise floor.** Section 4 shows that adding one data-loader iterator moved the ungated clean accuracy by 1.6 pp (04:107–117). The gated arm almost certainly consumes the RNG differently from the ungated arm once pseudo-label sets differ, so the "paired" difference includes a trajectory-change component of the same order (between-seed SD of the per-task gain 1.7–2.4 pp, 06:251). The small split gains (S07 +0.7, S00 +3.1, S04 +3.6, S09 +4.3) and the S03 −1.5 are within that envelope, and they occupy the low end of Fig. 5b. Sign-flip testing remains valid, but the low-coverage end of the regression is noise.

**Remedy (from saved per-window predictions).**
- (i) Decompose each split's gain into the contribution from windows on certified recordings and from uncertified ones. If almost all of it is on certified recordings, say plainly that the gain is local and the correlation is expected. If there is spill-over, that is the interesting finding.
- (ii) Report label-free coverage (share of all target recordings with any fault verdict) and its correlation, and correct 07:30 and 10:29.
- (iii) Show which specimens drive each split's coverage, and replace p-values with a description: e.g. "the two splits with gains > 20 pp are the two whose clean target contains both KA04 and KA16 while the ungated model mislabels them".
- (iv) Optional, and new runs: a placebo gate that withholds a random subset of pseudo-labels at matched coverage separates "correct verdicts" from "withholding".
- (v) Remove "properties of the data" (06:262), because coverage is a property of data × detector × operating point (see M8 and the off-rig calibration, 06:221–235).

### M6 [major]. The oracle is not shown to be an upper bound on keep-or-withhold filters, and its exact action inside SDALR is under-specified

**Where.** 00:10 ("bounding keep-or-withhold filters"); 01:52–54 ("bounds every pseudo-label filter, physical or statistical"); 01:68; 04:58–60, 04:76–77; 06:159–164; 10:23–24.

**Why it matters.**
1. Adaptation is a non-convex, iterative procedure. Nothing guarantees that "keep all correct, withhold all incorrect" maximises final accuracy over all keep/withhold subsets. Withholding some *correct* labels (e.g. to rebalance classes or to avoid reinforcing an easy specimen) can produce a better trajectory. The bound is a conjecture and should be stated as one. S04 and fold A show the oracle can even exceed the same-specimen arm, which the authors acknowledge (06:161–163). By the same token the oracle's position relative to other filters is unknown.
2. SDALR uses the reliable subset as supervision and the unreliable subset through an entropy term (02:32–34). The paper does not state whether pseudo-labels withheld by the oracle (or the gate) still enter the entropy term. If they do, the oracle is not a "perfect filter" of the training signal.
3. The oracle uses true labels of the *evaluation windows* during training (transductive). a_oracle is therefore partly a fit to test labels, not an estimate of what a correctly pseudo-labelled model achieves on new recordings of unseen specimens. That is acceptable for a within-protocol reference, but "82 % recoverable" will be read as a generalisation statement.
4. On the folds, the decomposition takes a_leaky from the fold job and a_oracle from the gating job (Table 3 footnote, t3:26). That crosses jobs, contrary to the rule stated at 04:117–119 and 06:43 ("arms are never crossed between jobs").

**Remedy.**
- Call it an "oracle-filter reference", not a bound, everywhere (abstract, 01:53, 01:68, 06:160, 10:23).
- State precisely what happens to withheld samples in SDALR's loss.
- From saved masks/predictions, report the fraction of windows the oracle keeps, and the oracle accuracy separately on kept and withheld windows.
- Either drop the fold rows of the decomposition or flag them as cross-job.

### M7 [major]. Statistical inference: unit, dependence, population, and promised intervals that never appear

**Where.** 04:81–96; 04:104–105; 06:53–55, 06:78, 06:280; t3:26; t4:23; t5; Fig. 5 caption.

**Points.**
1. **Sign-flip validity.** The exact sign-flip test assumes independent clusters with distributions symmetric under H0. The ten splits are drawn from 17 specimens and overlap heavily (Table 2: e.g. KA16 is in 8 of 10 source sets, KI04 in 7). 06:82–83 says the tests "make no claim of independence beyond" treating each draw as a cluster, but the sign-flip null *is* an independence claim.

   With 10/10 positive splits and a minimum of 8.2 pp the conclusion will not change. However, the stated p = 0.001 is not exact, and the inferential population is "random 3/3/3 source draws from *these 17 specimens*", not bearings in general. Say so. The specimen-level analysis in M1 gives a test whose unit (the specimen) is the one a reader wants to generalise over.
2. **Bootstrap intervals promised, not delivered.** 04:83 promises "a bootstrap that resamples whole clusters" for every primary effect. 04:104–105 promises bearing-cluster bootstrap intervals on record-level rates. No interval appears anywhere in the manuscript or tables.

   This matters most for the false-acceptance rates. "0/480" and "1/480" come from **6 healthy specimens**, and with 6 clusters a bearing-level interval on false acceptance is wide (rule-of-three on 6 units gives an upper bound of order 40 % at the specimen level). The headline safety claim must carry that uncertainty.
3. **Naming inconsistency.** Table 3's footnote calls the ten-split test a "one-sided Wilcoxon" (t3:26); the text calls it a cluster-level permutation test (06:54). Both give 1/1024 here, but the paper should name one primary test and use it consistently.
4. **The BH/BY family.** 04:95–96 says the family's members are given "at every stage of revision", so the family grew as experiments were added (C104 etc.). A multiplicity family assembled after results accumulate is not a pre-specified family. State this.

   More generally, the multiplicity apparatus (BH, BY, cluster vs task) takes a lot of space for effects that are 10/10 positive. It would be better spent on effect sizes with intervals and on the gate-gain inference, the one place where the statistics are delicate.
5. **Pseudo-precision.** p < 10^-200 (06:280), p = 1.5 × 10^-6 for a partial correlation on n = 10 (06:207), and "agree to 0.000 points" (04:111) should go.
6. **Seeds.** The ten splits use a single seed (2024). The seed-to-seed range of fold-mean clean accuracy is 1.9–3.2 pp (04:104). That is irrelevant for Δ_leak but not for gate gains of 0.7–4.7 pp (see M5.4).

### M8 [major for MSSP]. Low envelope-gate coverage is attributed to the data, but the detector design is a plausible cause and is not benchmarked

**Where.** 05:23–27; 06:186–219; 06:262–264 ("properties of the data … tuning the gate is not where the remaining points are"); 09:48–50; Fig. 5a.

**Why it matters.**
1. The envelope rule has no band selection, no pre-whitening and no discrete/random separation (05:23). On Paderborn the full-band envelope at 64 kHz is likely dominated by low-frequency structural and electrical content (inverter-driven motor). Removing those is the standard first step of envelope diagnosis (Randall & Antoni 2011; Smith & Randall 2015, which the paper cites).
2. A 20 % detection rate on real damage at near-zero FA is plausible for a crude detector, but it is not established as a property of these recordings.
3. The comb tests do use the kurtogram and get *lower* coverage. They also have a stricter surrogate test (α/n_families, K = 5, two "unmistakable" lines), so the comparison does not isolate band selection.
4. The definition of the threshold is inconsistent: "median-normalised squared envelope spectrum exceeds a threshold z" (05:24–25) vs "a within-recording robust z-score" (06:222). A ratio to the median and a robust z-score (median/MAD) are different statistics with different null distributions (for an exponential SES ordinate, median ≈ 0.69 × mean). The reader cannot reproduce the operating point.
5. The ±2 % slip search window (05:6–8) is more than twice the largest slip measured (95th percentile 0.88 %, 06:321–322). At the third harmonic of BPFO it spans about ±18 bins of 0.25 Hz, which inflates the max-statistic under H0 for no benefit.
6. Fig. 5a: the envelope curve saturates at 373/1839 from about 1.7 % to 12 % FA. A threshold sweep should keep increasing detections as FA rises. The flat segment suggests either a coarse sweep grid or a structural cap from the 2-of-3 rule or the window. Report the grid and extend the x-axis well past 12 %.
7. "Unmistakable line" (05:15) is undefined.

**Remedy (Kaggle CPU, no GPU).**
- (i) Run a standard benchmark envelope pipeline on the 880 real-damage + 480 healthy recordings and report its operating curve beside the four gates: e.g. cepstral pre-whitening + fast-kurtogram/SK band + SES, with the CWRU-benchmark diagnostic rule.
- (ii) Report detectability per specimen against Lessmeier damage extent and mechanism. Section 9 already notes that the plastic-deformation specimens are essentially never certified. Is coverage simply tracking damage size?
- (iii) Fix the z definition and justify the ±2 % window.
- (iv) Replace "properties of the data" with "properties of these recordings under this detector family".

### M9 [major, cumulative]. Internal contradictions that a reader will find

Each item is small; together they undermine trust in a paper whose selling point is rigour.

| # | Statement | Contradicted by |
|---|---|---|
| a | "Nor would a representation-level remedy address the root cause, since the information is present before any representation is learned" (10:18–19); "a representation-level fix aimed at 'memorisation' would be aimed at the wrong level" (06:288–289) | 09:56–58: a class-conditional adversary "which the probe … motivates directly … the obvious next experiment"; 02:64–73 devotes a subsection to that remedy. The argument at 10:18–19 is also logically wrong: information present in the input is exactly what invariant representation learning removes, and the oracle arm shows the representation *can* be moved substantially. |
| b | "Identity" framing in 00:7, 01:21–24, 06:139, 07:9, 10:14–17, 10:37, highlight 3 | "specimen-level damage signature … not a generic identity of every bearing" (06:111–113) and the session caveat (06:285–289) |
| c | "false acceptance predicted the sign of the effect in every case we tested" (08:26–27); "essentially never costing anything" (07:15–16); "essentially never harmful" (08:41) | S03: envelope gate (FA 1/480) has a −1.5 pp gain (t3:14; Fig. 5b); Table 6 shows negative per-task effects for both safe gates in every seed (min −0.70; only 7–10 of 12 tasks > 0). The "sign" claim rests on three gates' fold means. |
| d | Table 1 Paderborn "Conditions 4 (2 used)" (t1:11) | Three conditions are used for adaptation (03:9–11) and all four for gates/slip |
| e | Highlight 2: "The loss replicates … at a fixed operating condition" (main.tex:34), where "the loss" refers to SFDA accuracy (highlight 1) | Only a random forest was run at fixed condition (06:114–115; 09:42–44) |
| f | "The adaptation methods are run from their authors' released code … no numerical component of the released training pipeline is modified" (99:30–31) | SHOT is "our implementation" (04:50); the gated arms modify the pseudo-label step; the gating runner changes the RNG trajectory (04:113–117) |
| g | "CWRU and UORED-VAFCLS appear in the slip measurement and in the supplementary gate study" (03:14–15) | "UORED is excluded from the slip analysis" (09:52); Table 1 gives UORED only "gate safety (suppl.)"; yet the off-rig calibration with UORED is in the main text (06:224–235) |
| h | "The gates that are safe … deliver a median 4.5 points over the ten splits" (07:14–15) | Only the envelope gate was run on the splits (06:254–255) |
| i | "add a median 4.5 points over the ten splits, in every seed and in 9 of 10 splits" (10:26–27) | The ten splits were run with one seed; "every seed" refers to the folds |
| j | HUST excluded from gating because a 0.58 % pitch-diameter error is "enough to move a gate window off its line" (03:39–44) | Every gate searches a common offset within ±2 % (05:6–8), which absorbs a 0.58 % error. Either the exclusion rationale or the search window is wrong. Ironically, the error is "ten times" the median slip, which is itself below the estimator's resolution (see m1). |
| k | "the loss grows rather than shrinks, so condition shift is not what the leaky–clean difference measures" (07:65–67) | 06:101–102: the cross-condition comparison is "the only comparison this forest-internal control licenses". The two designs also differ in training-set size (half the recordings) and metric (balanced accuracy vs accuracy). |
| l | "the deterministic hash split divides the 1080 source recordings 508/572" (06:273–274) | Six source models = 3 × fold A (9 specimens × 20 = 180) + 3 × fold B (8 specimens, two outer-race, × 20 = 160) = **1020**, not 1080. The quoted chance level 0.35 matches 1020 (fold B's outer class has chance 1/2), not 1080. Please reconcile. |
| m | "Measured cage slip on these rigs is about 0.06 %" (10:29–31) | The CWRU residual is −0.3 % (06:325–327); the FAG median is −0.07 % |
| n | 01:42–43 "attributable to that overlap alone" | 09:25–27 and 07:60–62 (see M1) |
| o | Abstract/highlight: coverage is "the share of target recordings a gate can speak on" (00:12; main.tex:36) | The quantity actually used is the share of *faulty* target recordings (06:198; Fig. 5b) |

**Remedy.** Fix each item. Run a single consistency pass with the "identity → specimen-level signature" decision applied everywhere.

### M10 [moderate]. "Pre-registration" in a self-controlled repository

**Where.** 04:129–140; repeated "pre-registered" (00:5, 01:44, 04:40, 06:79, 06:87, 06:95, Table 2, etc.); 04:111.

A versioned protocol in a repository controlled by the authors is good practice. It is not pre-registration in the accepted sense: there is no third-party time stamp, and git history and commit dates can be rewritten. "The ordering is verifiable rather than merely asserted" (04:134–135) overstates. Several "pre-registered" items were also specified after related results had been seen: C103-style diagnostic runs, the same-condition control added in revision, the growing BH family, and comb_v2's guard, which was motivated by observed failures (05:20–21).

**Remedy.** Use "protocol fixed in advance in version control". Provide externally time-stamped evidence (e.g. a public archive snapshot such as Software Heritage/Zenodo, or signed/remote-pushed commits with server timestamps) if the claim is kept. List which analyses were added after which results, and use "pre-registered" only for those with external timestamps.

---

## 4. Minor concerns

- **m1. Slip section (06:294–327; 01:58–60; 10:29–31).**
  - The estimator recovers injected slip "to within 0.17 %" (06:319). The measured median of 0.06 %, the 5–95 % range of −0.31 to +0.22 % and the FAG median of −0.07 % are therefore all indistinguishable from zero and from estimator error.
  - Negative "slip" is not cage slip. It reflects a pitch-diameter or contact-angle error (θ = 0 is assumed; diametral clearance under radial load is not modelled), speed-channel bias, or estimator bias. The quantity measured is "apparent deviation of fault order from nominal kinematics".
  - Slip is measured only on recordings with ≥ 2 lit harmonics (16 %, 09:51). If "lit" is decided by a detector with a slip search window, the sample is selected towards lines near nominal.
  - The lock analysis is correct arithmetic (s* = 2.30/1.78/1.74 % checks), but it does not bear on the thesis.
  - Recommendation: move the whole section to the supplement, keep one sentence justifying the search window, and drop the patent citation (06:314–315). Citing a patent "as one documented instance of [a view] rather than as evidence for it" is not appropriate in a journal article.
- **m2. 06:221–235, off-rig calibration.** 24 healthy recordings, 4 of them from CWRU's single baseline specimen at four loads, is a very small number of specimens. Say how many distinct specimens are involved. "Truncated to the sample count that reproduces Paderborn's spectral resolution" also changes the number of averages and therefore the variance of the SES. State the effect.
- **m3. Raw-spectrum band rule.** Its operating point (z = 2, 45 % FA) is a single choice, and its in-loop effect (−3.9 pp, 06:255–256) appears in no table: which folds, which seeds, how many tasks? Report it in Table 6. Also report an in-loop run at a safer operating point, or drop the inference that FA "predicts the sign".
- **m4. Table 3 / Fig. 2, fold rows.** These mix jobs: clean 58.4 (fold job) is shown next to gated 61.2 and gain +4.4 (computed against the gating job's 56.8). A reader computing 61.2 − 58.4 = 2.8 will be confused. Use separate columns or separate rows per job, or omit the fold rows from Table 3. In Fig. 2 the fold-A gate tick sits against a different-job baseline dot.
- **m5. 04:24–30.** Only about 27 % of each record is used (34 × 2048 of about 256 800 samples). Justify this, or show that the result is insensitive to hop or start offset (cheap with a forest).
- **m6. Class balance is per class, not per specimen.** Fold B outer gets 1000 windows per specimen, other classes 680/660/660. This makes the 55.33 % arithmetic depend on window allocation (06:135–138). Report balanced-by-specimen accuracy as a sensitivity check.
- **m7. Same-condition control (06:93–115).** It uses balanced accuracy, while everything else uses accuracy, and trains on half the recordings. State the training-set sizes of both designs.
- **m8. Gate verdict space.** The comb tests score a ball family (05:12), but the gate returns only {silent, inner, outer} (04:55). What happens when the ball family wins?
- **m9. 03:8–9.** "the only public combination of several physical bearings per class and several operating conditions per bearing" is a strong universal claim. Soften it, or support it with a survey table.
- **m10. 01:14–16.** "eight split at random and nine by condition" totals 17 of 18 papers. Account for the 18th.
- **m11. 02:38–39.** "Published audits of SFDA stability in this field address other failure modes, such as collapse under industrial noise" has no citation.
- **m12. Missing literature.**
  - SFDA viewed as learning with noisy pseudo-labels (e.g. Yi et al., ICLR 2023, "When source-free domain adaptation meets learning with noisy labels"). This is the nearest neighbour for the oracle/pseudo-label-noise analysis, and a delta sentence is needed.
  - Bearing-diagnosis SFDA methods published in MSSP/RESS/ISA Trans. beyond SDALR.
  - Cross-specimen generalisation work on Paderborn, including Lessmeier et al.'s own artificial-to-real transfer experiments, which are an early specimen-disjoint evaluation.
  - Envelope-analysis benchmarks beyond CWRU.

  32 references is light for MSSP.
- **m13. 06:7–18, reproduction.** The six SDALR "condition pairs" on its 8-class task and the A1–A3 naming need clarification. The SDALR conditions may not coincide with the authors' A1–A3. The "bracket" language (06:12–13) is loose; give the seed mean ± SD against the published value for all six tasks in the supplement.
- **m14. 06:28–33 and Fig. 2.** HUST rows have no forest or gate marks; say why in the caption. In Fig. 2 the fold rows lack the forest diamond.
- **m15. Fig. 5a.** The y-axis starts at 292, which visually exaggerates the 366 vs 312 vs 309 differences (all about 17–20 % of 1839). Show the full 0–1839 range (or 0–30 %) in an inset or second panel.
- **m16. HUST (06:85–91; t7).** Six of the ten possible 3-of-5 type splits were used. Say how they were chosen. Also state HUST's speed and window/revolution count (C19-type quantities).
- **m17. 04:46–48.** "as_released … consults target labels" is a strong charge against published code. Quote or cite the line of the released code.
- **m18. 04:98–105.** The A/A determinism result ("0.00 points") belongs in the supplement. Only its consequence (seed variation, not run-to-run variation, is the relevant null) needs to be in the text.
- **m19. 04:107–119, 06:39–43, 09:16–18, t3:26.** The 1.6 pp cross-job discrepancy story appears four times. State it once, in the supplement, with one sentence in the main text.
- **m20. Abstract (00:10).** "An oracle pseudo-label filter recovers a median 82 %" needs "of the collapse" (82 % of what?).
- **m21. 01:59.** "a measured cage-slip distribution that settles when 6203 fault lines can lock" is ungrammatical (presumably "settles whether").
- **m22. AI-assisted execution (04:121–127; 99:33–39).** Disclosure is welcome and Elsevier policy asks for it. However:
  - (i) "It did not choose hypotheses, decision rules or operating points" is an assertion the authors, not the tool, must attest. Phrase it as the authors' statement and say who did choose them.
  - (ii) "The authors verified the analyses" should say *how*, e.g. which headline numbers were independently recomputed by a named author without the assistant.
  - (iii) Move the paragraph to the end of Section 4 or to a "Research process" subsection; at present it interrupts the statistics.
  - (iv) The writing declaration says the tool was used to "draft" text. Editors may ask for more detail.
- **m23. Highlights.** Highlight 1 uses the fold-based 37 pp rather than the inferential ten-split 36.2 pp. Highlight 5's "a calibration bar, not a remedy" is jargon. Highlight 4 has the coverage definition problem (M9-o). Check the 85-character Elsevier limit (highlight 2 is close).
- **m24. Recommendations item 3 (08:16–18).** "the difference carries 0.4 and 0.7 of the variance rather than a fixed fraction" is unclear: (1.7/2.8)² ≈ 0.37 and (2.4/2.8)² ≈ 0.73. State the implied correlation between paired arms, or drop the sentence.
- **m25. Specimen session/mounting (06:285–289; 09:41–42).** In Paderborn, are recordings of a specimen at different operating conditions made in the same mounting? If so, the *leaky* target shares session and mounting with the source, and part of Δ_leak is a mounting effect. That is deployment-relevant (a permanently installed bearing shares its mounting) and should be discussed in "Is this leakage …" (07:47–58).
- **m26. 06:271, "a task that carries no class information at all".** True of the labels, but the probe features were trained for class discrimination. Say "a within-class task".

---

## 5. Presentation and writing

1. **Length and density.** About 24 pages with roughly 300 numbers in the main text. The abstract alone carries about 20 numbers and is hard to parse at first reading. Target an abstract with 5–6 numbers: the ten-split median collapse, the HUST and SHOT replication, the forest bar, the oracle share, the gate FA contrast and the median gain.
2. **Structure.**
   - The paper carries three papers' worth of material: (i) a leakage audit of SFDA, (ii) a gate safety/coverage study, (iii) kinematic housekeeping (geometry, slip, 6203 lock).
   - (iii) should go to the supplement, apart from the per-manufacturer geometry. That geometry matters, and it should be linked to M1 (manufacturer confound).
   - Section 2.5 (invariance to nuisance) motivates an experiment that was not run. Cut it to one sentence in Limitations, which also removes contradiction M9-a.
   - The statistics/reconciliation material in Section 4 (A/A floor, cross-job diagnosis, BH/BY family composition, the AI paragraph and the pre-registration paragraph) takes about 45 lines. Half could move to S1.
3. **Tone.** The manuscript is defensive and self-referential in places:
   - "the honest cluster-level test" (06:45), "the honest unit" (t4:23, t6:20);
   - "we state it as such" (01:63);
   - "labelled as such" (06:105–106);
   - "it is not; …" (06:204);
   - "a bar, not a remedy" (00:7);
   - "the evidence a result in this area should carry before it is believed" (01:76).

   Replace these with neutral statements. Claims of rigour persuade less than the analyses themselves.
4. **Jargon.** "speak on", "certify", "lock", "engages", "housekeeping", "collapse" (used for both accuracy loss and specimen block labelling), "leaky/clean" (fine, but define once and stop re-explaining). "Gate" vs "filter" vs "validator" is used inconsistently.
5. **Tables.**
   - Table 3 mixes jobs in the fold rows (m4).
   - Table 4 mixes fold rows (no inference) and ten-split rows (means, while the text reports medians); add a median column.
   - Table 1 has the condition-count error.
   - Table 5 should add bearing-cluster intervals and the per-specimen coverage counts now buried in 06:196–198.
   - Table 6 omits the raw-spectrum rule.
   - Add a per-specimen table (manufacturer, mechanism, extent, seen-vs-unseen accuracy, gate coverage). It would carry M1, M2 and M8 at once.
6. **Figures.**
   - Fig. 2 is good. Add an explicit legend note that fold-row gate ticks are from a different job.
   - Fig. 3 (purity) adds little beyond one sentence once the arithmetic is given. Replace it with per-specimen seen-vs-unseen accuracy (M1).
   - Fig. 5a: axis truncation (m15). Fig. 5b: label all points with split IDs and colour by which coverable specimens are in the clean target (M5.3).
   - Fig. 7 belongs in the supplement.
7. **Title.** If M4 shows no amplification by adaptation, the title should not single out SFDA as the object whose results "do not survive". Consider "Specimen-disjoint evaluation of cross-condition bearing diagnosis: source-free adaptation, shallow baselines and the coverage limit of physics gating".
8. **Conclusions (10:4–12).** They restate results with all numbers again. Cut to the claims that survive the revisions, and state the scope ("on Paderborn, with 2048-sample inputs and three specimens per class") in the first sentence.

---

## 6. Recommendation: **Major revision**

**Justification.** The core empirical finding is strong, well controlled for this literature and practically important: specimen-disjoint targets cut cross-condition SFDA accuracy on Paderborn by roughly 35 pp, consistently across splits, methods and a second rig. The reporting practices are exemplary in several respects (target-label-free checkpointing, paired arms, A/A check, reporting of failed hypotheses, a strong shallow baseline).

However, several of the paper's distinctive claims are not identified by the design or are contradicted by its own evidence:
- that the effect is attributable to "overlap alone" and that the residual "lies in the representation" (M1);
- that the mechanism is an identity shortcut rather than under-sampled damage-signature variability, which the inputs may be unable to represent in any case (M2, M3);
- that the problem is SFDA-specific (M4);
- that coverage is a label-free, explanatory predictor rather than a near-identity (M5);
- that the oracle bounds all filters (M6).

The statistics promise intervals they do not deliver and overstate independence (M7). The envelope-gate coverage limit is attributed to the data without benchmarking a standard diagnostic pipeline (M8). There are at least fifteen internal inconsistencies (M9).

None of this requires new GPU training. M1, M4, M5 and M6 can be addressed from saved per-window predictions and existing logs. M2, M3 and M8 need only random-forest, probe and envelope runs on CPU. I would expect the revised paper to make somewhat narrower claims, and to be stronger for it. I would be glad to see it again.
