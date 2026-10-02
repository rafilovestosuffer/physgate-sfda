> **SUPERSEDED (2026-09-29).** This markdown draft stopped at v0.2 (2026-09-20) and predates both review rounds. It
> contains values that were later corrected or withdrawn (fold-level p-values, BH values, the probe framing). The
> manuscript is `paper/tex/`; do not cite, quote or submit this file.

<!--
DRAFT v0.2 (2026-09-15), restructured after supervisor review. v0.1 retained as paper/manuscript_v0.1.md.
Target: Mechanical Systems and Signal Processing (C67).
Rule 8: every number carries a source tag [src: path]. Pending values are `null` (C83 three seeds; C88 ten splits; C85 SHOT;
C93: BIST-W cut) and must not be filled by hand.
Scope: cross-condition transfer with bearing-disjoint targets on TWO rigs (Paderborn primary, HUST replication). Never cross-machine.
Structure (supervisor review): one thread — collapse → mechanism → can physics fix it (partly; ceiling) → source-side test.
Gate ROC study → Supplementary S2. Dataset hygiene → Supplementary S3. Slip lock → remark with measured slip (C90).
-->

# Bearing-wise evaluation of source-free domain adaptation: leakage, bearing-identity memorisation and the ceiling of physics-gated pseudo-labels on two test rigs

## Highlights

- Bearing-disjoint targets cut source-free adaptation accuracy by 37 points.
- The collapse replicates on a second rig and for SHOT and a non-adaptive forest.
- Source features identify same-class bearings in 507 of 508 held-out recordings.
- Physics gates give paired gains of 4–7 points, bounded by a perfect-filter ceiling.
- A non-adaptive random forest beats the adapted model by a median 8.9 points.

<!-- ≤ 85 characters each; check before submission. Highlight 3 wording is final only after C88 (distribution over splits). -->

## Abstract

<!-- ≤ 250 words. -->
Source-free domain adaptation (SFDA) reports near-ceiling accuracy for rolling-bearing diagnosis, yet evaluation protocols place
the same physical bearings on both sides of a transfer task. We re-evaluate a published SFDA method (SDALR) for cross-condition
transfer on one test rig (Paderborn), using a paired design in which only bearing overlap changes. Bearing-disjoint targets lower
mean accuracy from 94.1% to 56.8% on two folds, and by a median 36.2 points (range 8.2–61.6, p = 0.001) over ten pre-registered
random bearing splits, and by a median 33.5 points on a second rig (HUST bearing, six splits). SHOT collapses likewise, and so
does a random forest on ten time-domain statistics that uses no adaptation at all; that baseline exceeds the adapted model on clean targets by a median 8.9 points. Saved predictions show the adapted model labelling each
physical bearing as a whole, and a probe recovers the individual bearing among same-class bearings in 507 of 508 held-out
recordings. An oracle filter that keeps only correct pseudo-labels
recovers a median 82% of the collapse, which bounds what any pseudo-label filter can achieve. Kinematic envelope gates, selected by their false acceptance on 480 real
healthy recordings (at most 2%, against 45% for a raw-spectrum band rule of the kind used in recent physics-guided SFDA), add
4–7 points in paired comparisons and close a median 19% of that gap, while the raw-spectrum rule lowers accuracy. We argue that bearing-disjoint, multi-split evaluation with paired
differences, oracle ceilings and shallow baselines should precede accuracy claims for source-free bearing diagnosis.

**Keywords:** rolling bearing; source-free domain adaptation; data leakage; bearing-wise evaluation; pseudo-label gating; envelope analysis

---

## 1. Introduction

Data-driven bearing diagnosis relies increasingly on domain adaptation to transfer a model trained under one operating condition
to another without target labels. Source-free domain adaptation (SFDA) goes further: only the trained source model and unlabelled
target data are available during adaptation. Reported accuracies on public benchmarks are high. Vieira et al. surveyed 18
bearing-diagnosis papers from 2025: all reported above 94% and six reported 100% [src: notes/vieira_2026.md]. None of the 18
used bearing-wise splits.

Bearing-wise evaluation has changed conclusions in supervised settings on a single test bench (Hendriks et al.; Vieira et al.).
It has not been applied to SFDA, which Vieira et al. explicitly place out of scope. The question matters for SFDA in a specific
way. Adaptation refines the source model's own pseudo-labels, so if the source model has learned to recognise the individual
bearings it was trained on, adaptation has nothing correct to refine on bearings it has never seen. Physics priors (fault
characteristic frequencies computed from geometry and speed) are now used to filter those pseudo-labels (Bio-SFDA's EAGLE module;
PCTL). Whether such filtering can repair a leakage-induced collapse, and how much it could repair at best, has not been measured.

This paper follows one thread.

1. **Collapse.** With a paired design that fixes the source model and target conditions and changes only bearing overlap, we
   measure how much of SDALR's performance survives bearing-disjoint targets, over two folds and ten random bearing splits on
   Paderborn (Section 5.1) and six splits on a second rig (Section 5.4c).
2. **Mechanism.** Saved predictions show the adapted model labelling each physical bearing as a whole. An oracle pseudo-label
   filter splits the collapse into a part that any filter could in principle recover and a part carried by the source
   representation (Sections 5.2–5.3).
3. **Can physics fix it, and how far?** We select gates by their false acceptance on real healthy recordings, insert them into
   SDALR, and report paired per-task gains against the oracle ceiling (Section 5.4). The slip condition under which 6203 fault
   lines coincide with shaft harmonics is checked against measured slip (Section 5.5).
4. **Where the identity lives.** A within-class probe shows that the source representation identifies individual bearings almost
   perfectly (Section 5.6).

We do not claim a new architecture or detector. Statistical thresholds on the squared envelope spectrum are established
(Borghesani et al.), harmonic-coordinate features closely related to ours were published by Matania et al., and class-conditional
adversarial invariance is established in domain generalisation (Li et al.). We claim the evaluation, the decomposition and the
measured limits of physics gating.

## 2. Related work

**Evaluation of data-driven bearing diagnosis.** Hendriks, Dumond and Knox [hendriks2022] showed that condition-wise splits of the
CWRU data place the same physical bearings in training and test sets. Vieira et al. [vieira2026] generalised bearing-wise
partitioning to CWRU, Paderborn and UORED-VAFCLS, and measured inflation from bearing- and segmentation-level leakage over 100
evaluation splits. Their study is supervised and restricted to a single test bench; cross-domain and source-free settings are out
of scope. We extend the bearing-wise principle to SFDA with a design in which the source model is shared between leaky and clean
targets, and adopt random bearing splits for the variance axis. Two further studies isolate leakage without adaptation: Wheat et
al. [wheat2024leakage] compare run-to-run, day-to-day and part-to-part splits for PCA/LDA pipelines, and Knap et al.
[knap2026leakagesafe] publish a leakage-safe cross-domain benchmark on CWRU and Paderborn that enforces recording-level
separation over six fixed source–target scenarios. Recording-level separation removes window leakage but still allows the same
physical bearing on both sides, which is the leakage this paper measures, and neither study evaluates source-free methods.

**Source-free domain adaptation for bearings.** SHOT [liang2020shot] established the source-hypothesis-transfer template: a frozen
classifier, information maximisation and centroid pseudo-labels. Jeong et al. [jeong2025] combine speed-normalised order spectra,
a U-Net variational autoencoder and test-time training. SDALR [sdalr2025] separates reliable from unreliable target predictions
and reports 96.8% mean accuracy across Paderborn operating conditions. Audits of SFDA
stability exist for other failure modes, for instance collapse under industrial noise, but not for bearing-disjoint targets. None
of these methods is evaluated on targets made of bearings disjoint from the source. We reproduce SDALR from its released code before re-evaluating it,
and repeat the key experiment with SHOT.

**Physics priors in adaptation.** PCTL [pctl2026] scores predicted classes against envelope-spectrum energy at characteristic
frequencies and trains a confidence predictor with labelled target data. Bio-SFDA [yoon2026biosfda] gates and weights
pseudo-labels with band-energy predicates at BPFO, BPFI and BSF on a short-time Fourier transform. Such modules are evaluated
through end accuracy; their false acceptance on healthy bearings is not reported. The Bio-SFDA task definition for Paderborn
cannot be reconstructed from the article, so we evaluate the mechanism as described, as we implemented it, and do not compare
reported accuracies.

**Invariance to a nuisance correlated with the label.** Enforcing invariance to a variable that carries label information
conflicts with classification [liu2021labelshift]. Class-conditional adversaries restore
compatibility [li2018ciddg], and subject-adversarial training plays the same role in EEG decoding [ozdenizci2020eeg]. In a bearing source set, class is a function of physical bearing, which is the extreme case.

## 3. Data and bearing kinematics

**Paderborn (PU)** real-damage bearings (6 healthy, 5 outer-race, 6 inner-race; 64 kHz) are used for all adaptation experiments.
Gate false acceptance is measured on all 480 healthy PU recordings at four conditions, and slip on all single outer- and
inner-race recordings. CWRU is used only for the slip measurement and in the supplementary material. HUST bearing (five bearing types, three loads)
provides the second-rig replication of Section 5.4c; it contributes raw windows only, since its pitch diameter is unpublished.

Characteristic orders follow from ball count, ball and pitch diameters and contact angle, and a bearing designation does not fix
them. Paderborn's per-bearing documentation gives pitch diameter 29.05 mm for 26 bearings (IBU, MTK) and 28.55 mm for 6 FAG
bearings (8 balls, 6.75 mm) [src: configs/bearings.yaml]. BPFO is therefore 3.0706 and 3.0543 orders, not the 3.0531 of CWRU's
SKF 6203 that is commonly reused. Shaft speed is the in-file measured speed channel.

## 4. Protocol

**Paired leakage design.** Each source bearing set holds 3 healthy, 3 outer-race and 3 inner-race bearings. For each ordered pair
of operating conditions (A1 N15_M01_F10, A2 N15_M07_F04, A3 N15_M07_F10), one source model is trained at the source condition.
It is then adapted to (i) the same bearings at the target condition (leaky) and (ii) the complementary bearings at the target
condition (clean). The leaky–clean difference is attributable to bearing overlap alone. Windows are 2048 samples, 2000 per class
and balanced; the label space is {normal, inner, outer}.

**Splits.** Two mechanical folds (M1: A→B and B→A; fold B's source has 2 outer-race bearings) [src: configs/splits.yaml], and ten
random 3/3/3 source draws. The random draws are uniform without replacement from the 4,000 possible, excluding fold A, with the
RNG seed fixed before any run [src: configs/splits_k10.yaml; PROTOCOL C88]. The split is the statistical unit.

**Adaptation variants.** `final_checkpoint` uses the last iterate and touches no target labels; `as_released` selects the
checkpoint with target labels, as the released code does, and is reported only in Section 5.1.

**Gating and pairing.** A gate returns a per-recording verdict {normal (silent), inner, outer}. Inside SDALR's pseudo-label step,
a pseudo-label is kept only if it agrees with a non-silent verdict. The oracle filter keeps only correct pseudo-labels. All arms
of one comparison run in one job on the same source checkpoint and seed. This is verified from identical pre-update target
accuracy in every adaptation log [src: experiments/paired_gating.py], and differences are reported per task.

**Decomposition.** Total collapse = leaky − clean; filter-recoverable = clean with oracle filter − clean; not filter-recoverable =
leaky − clean with oracle filter.

**Statistics and pre-registration.** One-sided Wilcoxon signed-rank tests on paired units (tasks within a fold, or splits). With
12 tasks the smallest attainable p-value is 2⁻¹² ≈ 0.00024. Every hypothesis, decision rule and budget was committed before its
run. Deviations are listed in Supplementary S1 as a pre-registered-versus-changed table.

## 5. Results

### 5.1 Reproduction and collapse

SDALR reproduces on JNU (98.03% vs 98.50% reported) and on Paderborn within seed variability (96.20% vs 96.78%; the two hardest
tasks bracket the published values over four seeds) [src: results/M0_PU_RESULT.md; PROTOCOL C80].

On the two mechanical folds, `final_checkpoint` reaches 94.1% on leaky and 56.8% on clean targets (−37.3 points, p = 0.00024 over
12 tasks); `as_released` gives 94.7% vs 57.8% [src: results/M1_RESULT.md]. Adaptation adds 2.2–5.4 points on clean targets, and
target-label checkpoint selection adds 1.0–2.0. A random forest on ten time statistics, trained on the same source windows
without adaptation, shows the same pattern (88.8% leaky, 63.6% clean; per-bearing purity 0.95) and exceeds SDALR's clean
accuracy by 6.7 points; frequency-band and envelope-spectrum forests collapse by 41 and 34 points [src: results/c91/C91_RESULT.md].
SHOT, a second SFDA method, falls from 87.2% to 65.1% (−22.1 points, p = 0.001) [src: results/C85_RESULT.md]. The collapse is
therefore a property of source-trained classifiers on this rig, not of SDALR. Over the ten pre-registered random bearing splits,
the split-level collapse has median 36.2 points (range 8.2–61.6; one-sided Wilcoxon p = 0.001), so the leak generalises well
beyond the two mechanical folds [src: results/c88/C88_RESULT.md].

### 5.2 One label per bearing

On clean targets every window of a physical bearing receives the same label (per-bearing purity 1.000). Healthy bearings are
labelled correctly. Some fault bearings are labelled entirely as another class: KA04 and KA16 as inner, KI04 as normal, KI14 as
outer [src: results/M2_SINGLE_RUN.md]. This is bearing-identity memorisation observed directly in an adapted model.

### 5.3 Decomposition

On the two folds (seed 2024, matched variant), the oracle filter lifts clean accuracy from 56.0% to 82.7% against a leaky 94.1%.
Of the 38.1-point collapse, 26.6 points (70%) are filter-recoverable and 11.5 (30%) are not [src: results/PAIRED_GATING.md]. The
split is fold-dependent. With fold A as source the oracle filter recovers the whole collapse. With fold B, whose source has two
outer-race bearings, it recovers 48% [src: experiments/c88_eval.py, M1 rows]. Over the ten splits the filter-recoverable share has median 82% (interquartile range 68–90%); in one split (S04, the smallest
collapse at 8.2 points) the oracle filter exceeds the leaky accuracy itself [src: results/c88/C88_RESULT.md].

### 5.4 Physics gating: safety, paired gains and ceiling

**Choice of gates.** At pre-registered operating points, healthy false acceptance on 480 PU recordings is 1/480 for the envelope
threshold rule, 0/480 for the shaft-alias-guarded comb test (comb_v2), 9/480 for the comb test and 214/480 for the raw-spectrum
band rule [src: results/h7/H7_RESULT.md; results/comb_v2/COMB_V2_RESULT.md]. Full operating curves are in Supplementary S2. The
envelope threshold rule dominates at every false-acceptance level. Envelope gates engage about 6 of 23 faulty bearings, which
bounds what any of them can contribute.

**Paired gains.** Per-task gains (gated − ungated, same source model) on the 12 fold tasks [src: results/PAIRED_GATING.md]:

| gate | seed | mean | median | min | max | tasks > 0 | p |
|---|---|---|---|---|---|---|---|
| comb_v2 | 2024 | +3.73 | +3.67 | −0.05 | +8.07 | 8/12 | 0.007 |
| comb_v2 | 0 | +3.79 | +3.33 | −0.08 | +11.01 | 7/12 | 0.008 |
| comb_v2 | 1 | +4.56 | +3.28 | −0.08 | +15.45 | 8/12 | 0.007 |
| envelope threshold | 2024 | +5.70 | +5.59 | −0.05 | +14.52 | 10/12 | 0.001 |
| envelope threshold | 0 | +7.44 | +7.57 | −0.01 | +18.02 | 9/12 | 0.002 |
| envelope threshold | 1 | +7.99 | +6.65 | −0.70 | +19.44 | 10/12 | 0.002 |

No gated task loses more than 0.70 points. Across seeds, the per-task gain varies by 1.7 (comb_v2) and 2.4 (envelope) points,
against 2.8 points for ungated per-task accuracy. Over three seeds the mean paired gain is +4.03 points for comb_v2 (p = 0.007) and
+7.05 for the envelope threshold gate (p = 0.0007), positive in every seed; both meet the pre-registered robustness rule
[src: results/C83_RESULT.md]. Over the ten splits the median paired gain is +4.5 points (range −1.5 to +22.6), positive in 9 of
10, one-sided Wilcoxon p = 0.003, which meets the pre-registered rule [src: results/c88/C88_RESULT.md]. The raw-spectrum rule
lowers accuracy (−3.9 points, single seed) [src: results/M2_SINGLE_RUN.md].

**Ceiling.** The envelope gate closes a median 19% of the oracle gap across splits [src: results/c88/C88_RESULT.md]. Where a gate engages a bearing it breaks the
one-label lock (KA04 purity 0.56; task accuracy 55.3% → 69.9%) [src: results/M2_SINGLE_RUN.md]. It cannot act on bearings it
never engages, nor on the non-filterable part of Section 5.3.

### 5.4b A non-adaptive baseline under the same splits

Random forests trained on ten time-domain statistics of the same windows, with no adaptation and no target data, reach a median
of 8.9 points **above** adapted SDALR on the clean targets of the ten splits (ahead in 8 of 10; −2.0 points in the worst case)
[src: results/c88/C88_RESULT.md; results/c91/C91_RESULT.md]. They collapse in the same way when bearings are disjoint (25–41
points on the two folds) and label bearings almost as wholes (purity 0.76–0.95). Two conclusions follow. The collapse is a
property of source-trained models on this rig rather than of a particular adaptation algorithm, and reported gains for
source-free methods should be checked against a shallow baseline under the same bearing-disjoint split before they are read as
progress.

### 5.4c Replication on a second rig

The Paderborn design transfers to HUST bearing, which has one physical bearing per class for each of five bearing types
(6204–6208) and three load domains, giving the same three-domain, six-task, {normal, inner, outer} structure. Source sets of
three bearing types were adapted to the same types at the target load (leaky) and to the other two types (clean), for six
pre-registered splits. Mean leaky accuracy is 98.7% and mean clean accuracy 59.6%; the split-level loss has median 33.5 points
(range 25.8–61.1, one-sided Wilcoxon p = 0.016), which meets the pre-registered replication rule [src: results/c94/C94_RESULT.md].
On this rig a disjoint target changes bearing size as well as identity, so the shift is stronger than Paderborn's and the
result is stated as bearing identity *and* geometry. No gate is computed for HUST: its pitch diameter is unpublished, so its
kinematics cannot be verified (Supplementary S3.5).

### 5.5 Remark: shaft-order lock of 6203 lines and measured slip

Under the cage-slip model, BPFO(s) = (1−s)·BPFO₀ and BPFO(s) + BPFI(s) = n. If BPFO₀ = m + δ with m an integer, both race lines
reach integer shaft orders at the same slip s* = δ/BPFO₀. This gives 2.30% for PU IBU/MTK, 1.78% for PU FAG and 1.74% for CWRU
fan-end bearings [src: PROTOCOL C75]. Smith and Randall observed such lock-like behaviour on CWRU [smith2015]. We measured slip
from fault lines with in-file speed, and the estimator recovers injected slips of 0.1–4% to within 0.17% [src:
results/c90/c90_synthetic.txt]. Measured slip on Paderborn has median 0.06% (5–95%: −0.31 to +0.22%, 294 recordings). Of 304
measurable 6203 recordings, 3 are within tolerance of s*, and all 3 disappear once shaft-order bins are masked [src:
results/c90/C90_RESULT.md]. At these operating points the lock is therefore not a practical failure mode. The residual −0.3% offset
on CWRU bounds how precisely fixed-kinematics windows can be placed.

### 5.6 Bearing identity in the source representation

We test directly whether the source representation encodes individual bearings beyond their class. A logistic-regression probe
is trained on frozen source features using record-disjoint halves, with one probe per class that must tell same-class bearings
apart. It identifies the physical bearing in 507 of 508 held-out recordings (0.998; pooled chance about 0.35), consistently across
all six source models (two folds × three source conditions) [src: results/c87/N1_RESULT.md]. The features that adaptation starts
from therefore separate bearings within a class almost perfectly. On a rig with three bearings per class, such features can carry
the source classes without any fault physics, which is consistent with the one-label-per-bearing behaviour of Section 5.2.

## 6. Discussion

**Why the physics gain is modest.** The oracle filter separates the collapse into a part a pseudo-label filter could recover and a
part it cannot. Physics gates act only on the first part, only on bearings whose fault lines they detect, and never on ball faults.
A three-seed gain of 4–7 points on a 38-point collapse is therefore close to what such a filter can deliver on this rig, not a
failure of tuning. The same ceiling applies to any pseudo-label filter, physical or statistical, and the oracle gap should be
reported alongside any claimed gain.

**Why the collapse is not method-specific.** SDALR, SHOT and random forests without adaptation all lose 22–41 points on
bearing-disjoint targets, and all assign near-uniform labels to each physical bearing [src: results/C85_RESULT.md;
results/c91/C91_RESULT.md]. The within-class probe shows why: the source model can tell same-class bearings apart almost
perfectly, so a feature that identifies the bearing is available to the classifier at no cost. On a rig with three bearings per
class, that feature separates the source classes as well as fault physics does. Adaptation cannot remove it, because it only
refines the source model's own decisions.

**What an SFDA evaluation on bearings should report.** (i) Targets made of bearings disjoint from the source. (ii) A distribution
over bearing splits, not one split, because the collapse and its decomposition vary strongly between splits (fold A: fully
filter-recoverable; fold B: half) [src: results/PAIRED_GATING.md; results/c88/C88_RESULT.md]. (iii) Paired differences on a shared
source model for any add-on module. (iv) The oracle pseudo-label ceiling. (v) A non-adaptive shallow baseline under the same split,
which on our folds reached or exceeded SDALR on bearing-disjoint targets.

**Physics priors.** Kinematic envelope gates are safe on real healthy recordings, while a raw-spectrum band rule of the kind used
in recent physics-guided SFDA accepts 45% of them. Gate safety should be measured on healthy data from the target rig before a gate
is trusted inside adaptation. The shaft-order lock of 6203 lines is exact algebra but was not observed at the slips measured here.

## 7. Limitations

- Cross-condition transfer with bearing-disjoint targets on two rigs; no cross-machine transfer is claimed. The second rig
  (HUST) confounds bearing identity with bearing size, and its unverifiable geometry excludes it from the gating analysis.
- Ten random bearing splits plus two folds, one seed per split; seeds are studied on the folds only.
- Envelope gates engage a minority of faulty bearings, and ball faults are absent from the Paderborn label space.
- Slip was measurable in 16% of 6203 fault recordings (those with at least two lit lines); UORED is excluded for lack of an
  independent speed.
- The Bio-SFDA gate is our implementation of the published description; the authors' code was not available.

## 8. Conclusion

On Paderborn, source-free adaptation results for rolling bearings do not survive bearing-disjoint evaluation. SDALR loses 37
points and SHOT 22, and a random forest without adaptation collapses in the same way. The adapted model assigns one label per
physical bearing, and the source features identify individual bearings within a class almost perfectly. A perfect pseudo-label
filter would recover much, but not all, of the loss. Kinematic envelope gates, selected for low false acceptance on real healthy
recordings, recover a consistent 4–7 points in paired comparisons across seeds and never cost more than 0.7 points on a task,
while a raw-spectrum rule makes adaptation worse. Across ten pre-registered random bearing splits the median collapse is 36.2 points and the median gate gain +4.5; the source features identify same-class bearings in 507 of 508 recordings. Removing that identity during
source training, for example with a class-conditional adversary, is the natural next step. The same collapse appears on a second rig, where six type-disjoint splits lose a median 33.5 points. These results concern
cross-condition transfer within a rig; they argue for bearing-disjoint, multi-split evaluation with paired differences, oracle
ceilings and shallow baselines before accuracy claims for source-free bearing diagnosis are accepted.

## Supplementary material

- **S1** Pre-registered versus changed (paper/supplementary_S1_changes.md, generated from PROTOCOL.md; 90 changes).
- **S2** Gate safety and full operating curves on PU, CWRU and UORED (v0.1 §6.4, results/roc, results/h7, results/comb_v2).
- **S3** Dataset hygiene: per-manufacturer Paderborn geometry, UORED logged-speed errors, CWRU cross-end contamination (13/52),
  and the within-CWRU fan-end/drive-end control (C78, null).

## Declarations

- CRediT, data availability, competing interests: to be completed.
- Generative AI: an AI assistant was used for code, analysis scripting and drafting; all results trace to retained artifacts and
  were checked by the authors. <!-- confirm wording with the authors and Elsevier policy -->
