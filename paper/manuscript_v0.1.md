<!--
DRAFT v0.1 (2026-09-15). Target: Mechanical Systems and Signal Processing (C67).
Rule 8: every number carries a source tag [src: path]. Values awaiting C83 are written as `null` and must not be filled by hand.
Scope (C84): cross-condition, cross-bearing source-free adaptation on Paderborn; gate safety on PU/CWRU/UORED.
Do NOT describe M1/M2 as cross-machine.
-->

# Do source-free adaptation gains survive bearing-wise evaluation? Leakage, bearing-identity labelling and physics-gated pseudo-labels in rolling-bearing diagnosis

## Highlights

- Bearing-wise splitting removes about 37 points of source-free adaptation accuracy.
- Without leakage, the adapted model assigns one label per physical bearing.
- Envelope physics gates are safe on real healthy bearings; a raw-spectrum rule is not.
- A strict envelope threshold beats a statistical comb test across the full ROC.
- At one closed-form slip, 6203 outer and inner race lines both hit shaft harmonics.

<!-- Elsevier limit: 3–5 highlights, ≤ 85 characters each. Check lengths before submission. -->

## Abstract

<!-- ≤ 250 words. Numbers pending C83 are null. -->
Source-free domain adaptation (SFDA) reports near-ceiling accuracy for rolling-bearing diagnosis, but evaluation protocols
routinely place the same physical bearings on both sides of a transfer task. We re-evaluate a published SFDA method (SDALR)
under a paired design in which only bearing overlap changes. On Paderborn, bearing-wise splitting lowers mean accuracy from
94.7% to 57.8% (−36.9 points, Wilcoxon p = 0.0002), while adaptation itself adds 2–5 points and target-label checkpoint
selection 1–2. Saved predictions show that the adapted model labels each physical bearing as a whole (per-bearing label purity
1.000). We then ask whether physics-based gating of pseudo-labels can help, measuring each gate's false acceptance on 480 real
healthy records rather than on synthetic noise. Envelope-domain kinematic gates accept at most 2% of healthy records; a
raw-spectrum band rule of the kind used in recent physics-guided SFDA accepts 45%. Across the full operating curve, a strict
threshold on the squared envelope spectrum dominates a surrogate-null comb test and its shaft-alias-guarded variant. Inside SDALR,
envelope gates raise mean accuracy by null points (null seeds) and close null of the oracle pseudo-label gap, whereas the
raw-spectrum rule lowers it. We derive a closed-form slip at which the outer- and inner-race lines of a 6203 bearing coincide
with shaft harmonics simultaneously, and report dataset-level corrections: per-manufacturer Paderborn geometry, unreliable
logged speed in UORED-VAFCLS, and measurable cross-end fault contamination in CWRU healthy channels.

**Keywords:** rolling bearing; source-free domain adaptation; data leakage; envelope analysis; pseudo-label gating; shaft harmonics

---

## 1. Introduction

<!-- Anchor per C41: physics priors are common; calibrated/validated ones are not. Claims in C65 order. -->

Data-driven bearing diagnosis increasingly relies on domain adaptation to transfer a model trained under one operating
condition, or on one machine, to another without target labels. Source-free domain adaptation (SFDA) goes further: only the
trained source model and unlabelled target data are available during adaptation. Reported accuracies on public benchmarks are
high — above 94% in every one of 18 bearing-diagnosis papers from 2025 surveyed by Vieira et al., with six reporting 100%
[src: notes/vieira_2026.md]. None of those 18 used bearing-wise splits.

Two developments make this worth re-examining now. First, bearing-wise evaluation has been shown to change conclusions in
supervised, single-test-bench settings (Hendriks et al.; Vieira et al.), but it has not been applied to SFDA, which Vieira et al.
explicitly place out of scope. Second, physics priors — fault characteristic frequencies computed from bearing geometry and
speed — are now routinely used to gate or weight pseudo-labels during adaptation (e.g. Bio-SFDA's EAGLE module; PCTL's
physics-consistency validator). Such gates are usually justified by end accuracy; their false acceptance on real healthy
bearings is rarely reported.

We make three contributions.

1. **A leakage-controlled evaluation of SFDA.** Using a paired design in which the source model and target conditions are fixed
   and only bearing overlap changes, we measure how much of SDALR's reported performance survives bearing-wise splitting, and we
   show from saved predictions how the model fails when it does not (Section 6.1–6.3).
2. **A safety evaluation of physics gates on real healthy records.** We compare four gates — a surrogate-null comb test, a
   shaft-alias-guarded variant, a strict envelope threshold rule, and a raw-spectrum band rule — by realised false acceptance and
   detections across their full operating curves on Paderborn, and test whether gating inside SDALR helps (Sections 6.4–6.5).
3. **Mechanism and dataset hygiene.** A closed-form slip condition explains when 6203 fault lines coincide with shaft harmonics;
   we also report per-manufacturer Paderborn geometry, logged-speed errors in UORED-VAFCLS, and cross-end contamination in CWRU
   (Section 6.6).

We do not claim a new network architecture or a new detector; statistical thresholds on the squared envelope spectrum are
established (Borghesani et al.; Antoni), and harmonic-coordinate features closely related to ours were published by Matania et
al. We claim the evaluation, the measured safety comparison and the mechanism.

## 2. Related work

**Evaluation of data-driven bearing diagnosis.** Hendriks, Dumond and Knox [hendriks2022] showed that condition-wise splits of
the CWRU data place the same physical bearings in training and test sets and proposed splits by fault size. Vieira et al.
[vieira2026] generalised the argument to bearing-wise partitioning on CWRU, Paderborn and UORED-VAFCLS, reformulated diagnosis as
multi-label detection with macro-AUROC, and measured the inflation caused by bearing- and segmentation-level leakage under a
controlled design. Their study is supervised and restricted to a single test bench; cross-domain and source-free settings are
stated as out of scope. We adopt their bearing-wise principle and extend it to source-free adaptation with a paired design in
which the source model is shared between leaky and clean targets.

**Source-free domain adaptation for bearings.** SHOT [liang2020shot] established the source-hypothesis-transfer template —
frozen classifier, information maximisation and centroid pseudo-labels — on which most later methods build. Jeong et al. [jeong2025] combine speed-normalised order spectra, a
U-Net variational autoencoder and test-time training, and find that order normalisation alone accounts for most of their target
gain. SDALR [sdalr2025]
separates reliable from unreliable target predictions and reports 96.8% mean accuracy across Paderborn operating conditions; He
et al. [he2026] propose a two-stage pseudo-supervised framework for cross-machine transfer. None of these reports targets made of
bearings disjoint from the source. We reproduce SDALR from its released code before re-evaluating it, and repeat the key
experiment with SHOT.

**Physics priors in adaptation.** Physics-guided methods increasingly use fault characteristic frequencies to steer adaptation.
PCTL [pctl2026] compares predicted classes against envelope-spectrum energy at characteristic frequencies computed from a reconstructed
spectrum, and uses the score to train a confidence predictor with labelled target data. Bio-SFDA [yoon2026biosfda] gates and
weights pseudo-labels with band-energy predicates at BPFO, BPFI and BSF on a short-time Fourier transform, with thresholds adapted
online from unlabelled target statistics. Such modules are evaluated through end accuracy; their false acceptance on healthy
bearings is not reported. Because the Bio-SFDA task definition for Paderborn cannot be reconstructed from the article (a ball class
is listed, and Paderborn contains no rolling-element damage; the split is not described), we compare gating mechanisms, not
reported accuracies.

**Statistical envelope analysis and invariant features.** The squared envelope spectrum is the standard carrier of
second-order cyclostationary bearing signatures [randall2011]; Borghesani et al. [borghesani2013] derived its statistics under
coloured noise and thresholds for testing cyclostationarity. We do not claim a new detector: a surrogate-null comb test is one of
four gates evaluated. Matania et al. [matania2025] project order-domain envelope spectra onto kinematic harmonic peaks to obtain a
machine-invariant representation for zero-fault-shot classification; our harmonic coordinates follow the same idea and are not
claimed as a contribution.

**Shaft-harmonic proximity of 6203 bearings.** Smith and Randall [smith2015] observed, in their CWRU benchmark, that the
characteristic frequencies of the fan-end 6203 bearing lie close to integer shaft orders and "appear to lock onto" shaft
harmonics. Industrial practice holds that such lines can be separated given enough spectral lines [patent10168248]. We give the
closed-form slip at which lock becomes exact for the outer- and inner-race lines simultaneously and show why finer resolution does
not remove it.

## 3. Data and bearing kinematics

### 3.1 Datasets

| Dataset | Bearings used | fs | Record | Role |
|---|---|---|---|---|
| Paderborn (PU) | 6 healthy, 5 outer, 6 inner real-damage; 12 artificial (gate evaluation only) | 64 kHz | 4 s | SFDA evaluation; gate evaluation |
| CWRU | 6205 drive end; 6203 fan end | 12 kHz | ~10 s | gate evaluation, contamination audit |
| UORED-VAFCLS | 20 bearings, healthy / developing / faulty | 42 kHz | 10 s | gate evaluation on natural faults |

### 3.2 Geometry — from each rig's own documentation

Characteristic orders follow from ball count n, ball diameter d, pitch diameter D and contact angle θ. A bearing designation
does not determine geometry. Paderborn's per-bearing damage profiles give pitch diameter 29.05 mm for 26 bearings (IBU, MTK)
and 28.55 mm for 6 FAG bearings, with 8 balls of 6.75 mm [src: configs/bearings.yaml; data/pu/<ID>/<ID>.pdf]; BPFO is 3.0706 and
3.0543 orders respectively, not the 3.0531 of CWRU's SKF 6203 that is commonly reused. UORED's article gives 8 balls, 6.77 mm,
pitch 28.50 mm for both manufacturers used (BPFO 3.0498) [src: configs/bearings.yaml C54].

### 3.3 Speed

PU and CWRU speeds are taken per file. UORED's logged speed is a single Hall reading per file; it disagrees with the cage-comb
estimate by −5.2% to +25% in several files and a spectral peak near 29.7 Hz is not the shaft rate [src:
results/b7_uored/B7_UORED_RESULT.md §5; PROTOCOL C74]. UORED results are therefore reported only where speed is measured from
the cage comb, and UORED is excluded from headline claims for inner-race faults.

## 4. Evaluation protocol

<!-- Adopt/differ table: notes/vieira_2026.md. -->

**Paired leakage design (M1).** PU real-damage bearings are divided into two disjoint folds (3 healthy, 3 outer, 3 inner in fold A;
3, 2, 3 in fold B) [src: configs/splits.yaml]. For each source fold F and each of the six ordered pairs of operating conditions
A1 (N15_M01_F10), A2 (N15_M07_F04) and A3 (N15_M07_F10), one source model is trained and adapted to (i) the same bearings at the
target condition (leaky) and (ii) the other fold's bearings at the target condition (clean). The leaky–clean difference is
therefore attributable to bearing overlap alone. Windows are 2048 samples, 2000 per class, balanced; label space {normal, inner,
outer}.

**Adaptation variants.** `as_released` selects the adapted checkpoint using target labels, as SDALR's released code does;
`final_checkpoint` uses the last iterate and touches no target labels [src: notes/sdalr_code_audit.md A1].

**Gate evaluation.** Gates are evaluated per record on 2,319 PU single-fault and healthy records (3.9 s), with false acceptance
measured on the 480 healthy records [src: results/h6_c35/].

**Statistics.** Paired one-sided Wilcoxon signed-rank tests over tasks; records within a bearing are correlated, so real-data
intervals are also reported as bearing-cluster bootstraps [src: PROTOCOL C56]. Hypotheses and decision rules were committed to
version control before the corresponding runs; deviations are listed in the supplementary change log.

## 5. Physics gates

All gates operate on per-record spectra and return {normal, inner, outer} (ball where the label space has it). A verdict of
"normal" means the gate is silent, not that the record is healthy.

- **Comb test (C30).** Cepstrum pre-whitening, fast-kurtogram band, squared envelope spectrum; for each family a harmonic comb
  (K = 5, sidebands J = 2 for the inner race) is scored over a common slip offset within ±2% and ranked against 499 surrogate
  orders; a family is admissible if its surrogate p-value passes α/n_families and at least two positions carry unmistakable lines.
- **comb_v2 (C72).** As C30, rejecting a family when half or more of its lit positions lie within 1.5 bins of integer shaft
  orders, and arbitrating by aligned-line fraction.
- **Envelope threshold rule (PCV-style).** Squared envelope spectrum without pre-whitening; a harmonic is present if the
  median-normalised spectrum exceeds z in its slip window; a family is declared if at least two of three harmonics are present.
- **Raw-spectrum band rule (EAGLE-style).** Our reimplementation of the mechanism described for Bio-SFDA: STFT band energy and
  peak-to-neighbourhood ratio at BPFO/BPFI/BSF, robust z-scored across records.

## 6. Results

### 6.1 Reproduction

SDALR reproduces on JNU (mean 98.03% vs 98.50% reported) [src: results/M0_JNU_RESULT.md] and on Paderborn within seed variability:
mean 96.20% vs 96.78%; the two tasks into A2 bracket the published values over four seeds (A3→A2 93.9 ± 4.7%, published 97.84%;
A1→A2 90.3 ± 4.9%, published 87.03%) [src: results/M0_PU_RESULT.md; PROTOCOL C80]. Seed standard deviation on these tasks (~5
points) exceeds the differences commonly reported between methods.

### 6.2 Bearing-wise splitting

Over the 12 paired tasks, SDALR `as_released` reaches 94.7% on leaky targets and 57.8% on clean targets (−36.9 points, one-sided
Wilcoxon p = 0.0002); `final_checkpoint` 94.1% vs 56.8% (−37.3 points) [src: results/M1_RESULT.md]. Source-only accuracy measured
before adaptation drops from 93.3% to 54.0%. Adaptation adds 2.2–5.4 points on clean targets and target-label checkpoint
selection 1.0–2.0 points, so neither explains the gap. With fold B as source, all six leaky tasks exceed 99.7% while all six
clean tasks lie between 55.27% and 55.33%.

### 6.3 One label per bearing

Saved predictions on the fold B → A clean tasks give per-bearing label purity 1.000: every window of a physical bearing receives
the same label. Healthy bearings are labelled correctly; among fault bearings, one outer (KA15) and one inner (KI16) are correct,
KA04 and KA16 are labelled inner, KI04 normal and KI14 outer [src: results/M2_SINGLE_RUN.md]. The exact 33/67% class splits in M1
follow directly from three bearings per class. This is the bearing-identity memorisation described by Vieira et al., observed
directly in an adapted model.

### 6.4 Safety of physics gates on real healthy records

At the pre-registered operating points, healthy false acceptance is 1/480 for the envelope threshold rule, 0/480 for comb_v2,
9/480 for the comb test and 214/480 for the raw-spectrum band rule [src: results/h7/H7_RESULT.md; results/comb_v2/COMB_V2_RESULT.md].
Sweeping each gate's parameter (Fig. ROC) [src: results/roc/ROC_RESULT.md], the envelope threshold rule lies on or above every other
gate at every false-acceptance level: 351 correct fault verdicts at zero false acceptance versus 312 for comb_v2; comb_v2
dominates the comb test; the raw-spectrum rule is dominated everywhere. No gate exceeds 24% correct fault verdicts before false
acceptance passes 10%: envelope gates engage about 6 of 23 faulty PU bearings.

### 6.5 Gating inside SDALR

<!-- Headline numbers are null until C83 (3 seeds) completes. Single-seed values are in results/M2_SINGLE_RUN.md and must be labelled
single-seed if quoted. -->

Inserting each gate at SDALR's pseudo-label stage (keeping a pseudo-label only if it agrees with a non-silent gate verdict) on the
12 clean tasks gives mean accuracy null (none), null (comb_v2) and null (envelope rule) over null seeds [src: pending C83]. The oracle
filter, which keeps only correct pseudo-labels, reaches 82.7% against 56.0% without gating in the single-seed run, so pseudo-label
noise is the dominant bottleneck [src: results/M2_SINGLE_RUN.md]. Gates close null of that gap. The raw-spectrum band rule lowers
accuracy (−3.9 points single seed) [src: results/M2_SINGLE_RUN.md]. Where gates engage a bearing, they break its single-label lock
(KA04 purity 0.56, accuracy 55.3% → 69.9% on one task) [src: results/M2_SINGLE_RUN.md]. Gates cannot help targets they never engage:
coverage of the A2 condition is 0–4% of records [src: PROTOCOL C81].

### 6.6 Mechanism and dataset findings

**Proposition (slip lock).** Under the cage-slip model the cage frequency is (1−s)·FTF·f_r, so BPFO(s) = (1−s)·BPFO₀ and
BPFO(s) + BPFI(s) = n for all s. If BPFO₀ = m + δ with integer m, both lines reach integer shaft orders at the same slip
s* = δ/BPFO₀: 1.63% (UORED), 1.74% (CWRU fan end), 1.78% (PU FAG), 2.30% (PU IBU/MTK) — within the range of slip usually reported
[src: PROTOCOL C75]. Because the relative offset and the slip window both scale with harmonic order, longer windows narrow the
confusion band but do not remove s*. This contrasts with the view that such lines "can be separated" with sufficient spectral
lines (US 10,168,248 B1), which holds for slip-free lines. The 6205 cannot lock at physical slip.

**Evidence and limits.** On UORED, a strong shaft-harmonic comb lit both the outer- and inner-race families and the sparse outer
comb won arbitration [src: PROTOCOL C71]; on PU, inner-race bearing KI16 was called outer in 57/80 records without pre-whitening
[src: results/h6_c35/H6_C35_RESULT.md]. A within-CWRU control (fan-end 6203 vs drive-end 6205) did not support a population-level
effect (confusions 6/33 vs 3/44, p = 0.12; 5 of 6 fan-end confusions not shaft-aliased) [src: results/c78/C78_RESULT.md].

**Cross-end contamination.** CWRU fan-end channels recorded during drive-end faults pass the gate for the correct drive-end fault
family in 13 of 52 runs (bearing-cluster 95% interval 11.5–40.4%), while the fan-end bearing's own families never do
[src: results/b6a/B6A_RESULT.md], supporting the exclusion of those signals from healthy test sets.

## 7. Limitations

- One published SFDA method; one dataset for the paired leakage design; two bearing folds; seeds as in Section 6.5.
- Envelope gates engage a minority of faulty bearings; ball faults were not detected on CWRU or UORED under any gate variant
  tested [src: results/c77/C77_RESULT.md; results/c79/C79_RESULT.md].
- The comb test's surrogate p-value is anti-conservative on synthetic noise; false-acceptance control rests on the multiplicity
  rule and on real healthy records [src: results/calibration/NULL_DRS_RESULT.md].
- UORED speed is resolved only where a cage comb exists (15/60 files).
- Harmonic-coordinate representations and alternative backbones were not evaluated (deferred, PROTOCOL C84).

## 8. Conclusion

<!-- Write after C83. -->

## Declarations

- CRediT: see paper/credit.md. Data availability: see paper/data_availability.md. Competing interests: paper/coi.md.
- Generative AI: an AI assistant was used for code, analysis scripting and drafting; all results trace to retained artifacts and
  were checked by the authors. <!-- confirm wording with the authors and Elsevier policy -->
