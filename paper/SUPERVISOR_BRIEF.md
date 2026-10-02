# Project brief for supervisor — Physics-gated source-free domain adaptation for rolling-bearing fault diagnosis

Status date: 2026-09-15. Target venue: Mechanical Systems and Signal Processing (MSSP), Q1; fallbacks Measurement, RESS, IEEE TIM.
All numbers below trace to retained artifacts and a pre-registered protocol (83+ logged protocol changes).

---

## 1. One-paragraph summary

Published source-free domain adaptation (SFDA) methods for bearing diagnosis report 94–100% accuracy, but their evaluations put the
same physical bearings on both sides of a transfer task. We re-evaluated a recent, reproducible SFDA method (SDALR, Neurocomputing
2025) with a paired design in which only bearing overlap changes. On the Paderborn dataset, bearing-wise splitting lowers mean
accuracy from 94.7% to 57.8% (−36.9 points, Wilcoxon p = 0.0002). Saved predictions show the adapted model assigns one label to each
whole physical bearing (label purity 1.000), i.e. it memorises bearing identity. We then evaluated physics-based gating of
pseudo-labels on real healthy recordings, found which gate designs are safe, showed that safe gates recover part of the lost
accuracy inside SFDA (+3.7 to +7.4 points, two seeds so far), derived a closed-form condition under which 6203-bearing fault lines
lock onto shaft harmonics, and corrected several dataset-level errors common in the literature. A mechanism-targeted remedy
(bearing-identity-adversarial source training) and a second SFDA method (SHOT) are running now.

---

## 2. Research questions (as the paper answers them)

- **RQ1.** How much of SFDA's reported performance survives when target bearings are physically disjoint from source bearings?
- **RQ2.** What does the adapted model actually learn when it fails?
- **RQ3.** Which physics-based pseudo-label gates are safe (low false acceptance on real healthy bearings), and does gating help SFDA?
- **RQ4.** Why do envelope-based gates fail on 6203 bearings, and when?
- **RQ5.** Can a source-side remedy that removes bearing identity recover clean-target accuracy?

---

## 3. Data and verified bearing geometry

| Dataset | Content used | Sampling | Role |
|---|---|---|---|
| Paderborn (PU) | 6 healthy, 5 outer-race and 6 inner-race real-damage bearings (SFDA); +12 artificial-damage (gate study); 4 operating conditions, 20 records each, 4 s | 64 kHz | main SFDA evaluation; gate safety |
| CWRU | drive end (6205) and fan end (6203), 12 kHz fault files | 12 kHz | gate study, cross-end contamination, within-rig control |
| UORED-VAFCLS (Ottawa) | 20 bearings × healthy/developing/faulty, naturally developed faults | 42 kHz | gate study on natural faults |
| JNU | reproduction only (one bearing per class; geometry unpublished) | 50 kHz | SDALR reproduction |
| HUST | not used for gating: pitch diameter unpublished | 51.2 kHz | — |

**Geometry corrections found during the project (each from the dataset's own documentation):**
- **Paderborn uses two 6203 geometries by manufacturer**: pitch diameter 29.05 mm (26 bearings, IBU and MTK) and 28.55 mm (6 FAG
  bearings), ball Ø 6.75 mm, 8 balls. The CWRU SKF 6203 geometry that is commonly reused for Paderborn matches neither.
- **UORED** article gives 8 balls, Ø 6.77 mm, pitch 28.50 mm.
- **UORED logged shaft speed is unreliable** (a single Hall reading per file, off by −5% to +25% in several files); a raw-spectrum
  peak near 29.7 Hz is *not* the shaft rate. Speed was measured instead from the cage-frequency harmonic comb (15/60 files), with
  independent agreement from ball-pass sidebands (30.21 Hz in one file).
- **HUST** publishes ball count and diameter but not pitch diameter, so its kinematics stay blocked (pitch is never inferred).

---

## 4. Methods and evaluation protocol

**SFDA methods.** SDALR (released code, reproduced first), SHOT (faithful reimplementation on SDALR's backbone, running).
Variants: `as_released` (checkpoint picked using target labels, as SDALR's code does) and `final_checkpoint` (no target labels).

**Paired leakage design (M1).** PU real-damage bearings split into two disjoint folds (fold A 3/3/3, fold B 3/2/3 healthy/outer/inner).
For each source fold and each of 6 ordered pairs of operating conditions, one source model is adapted to (i) the same bearings at the
target condition ("leaky") and (ii) the other fold's bearings ("clean"). The difference isolates bearing overlap. Windows 2048 samples,
2000 per class, balanced; classes {normal, inner, outer}.

**Physics gates (per recording).**
1. *Comb test (C30)*: cepstrum pre-whitening, kurtogram band, squared envelope spectrum, harmonic comb over a common slip offset,
   ranked against 499 surrogate orders, multiplicity rule (≥ 2 lines).
2. *comb_v2 (C72)*: C30 plus rejection of families sitting on integer shaft orders and arbitration by aligned-line fraction.
3. *Envelope threshold rule (PCV-style)*: strict z-threshold on the median-normalised squared envelope spectrum in slip windows.
4. *Raw-spectrum band rule (EAGLE-style)*: our reimplementation of the gate mechanism described in Bio-SFDA (Results in Engineering 2026).

**Gating inside SFDA (M2).** At SDALR's pseudo-label step, a pseudo-label is kept only if it agrees with the recording's gate verdict
when the gate speaks; silent recordings are untouched. An oracle filter (keeps only correct pseudo-labels) gives the upper bound.

**Statistics and integrity.** One-sided paired Wilcoxon over tasks; bearing-cluster bootstrap for real-data intervals (records within a
bearing are correlated); every hypothesis and decision rule committed to version control before its run; negative results
reported; every number traceable to a retained artifact and a ledger row.

---

## 5. Results to date

### 5.1 Reproduction (M0)
- SDALR on JNU: mean 98.03% vs 98.50% published.
- SDALR on PU: mean 96.20% vs 96.78% published; the two hardest tasks bracket the published values across 4 seeds
  (A3→A2 93.9 ± 4.7% vs 97.84%; A1→A2 90.3 ± 4.9% vs 87.03%). Seed standard deviation ≈ 5 points — larger than many reported
  method-to-method differences.

### 5.2 Bearing-wise splitting (M1) — headline
| | leaky (same bearings) | clean (unseen bearings) | Δ |
|---|---|---|---|
| SDALR as released | 94.7% | 57.8% | −36.9 pp (p = 0.0002) |
| SDALR final checkpoint | 94.1% | 56.8% | −37.3 pp |
| source model before adaptation | 93.3% | 54.0% | −39.2 pp |

Adaptation adds only 2–5 points; target-label checkpoint selection adds 1–2 points. With fold B as source, all six clean tasks land at
55.3% while all leaky tasks exceed 99.7%.

### 5.3 Mechanism: one label per bearing (M2 predictions)
On clean targets every window of a physical bearing receives the same label (per-bearing purity 1.000). Healthy bearings are right;
among fault bearings some are labelled entirely as the wrong class (e.g. an outer-race bearing labelled inner race). This is bearing-
identity memorisation observed directly in an adapted model.

### 5.4 Safety of physics gates on 480 real healthy PU recordings
| Gate | healthy false acceptance | correct fault verdicts (of 1,839) |
|---|---|---|
| Envelope threshold rule | 1/480 | 366 (351 at 0 false acceptance) |
| comb_v2 | 0/480 | 312 |
| Comb test (C30) | 9/480 | 309 |
| Raw-spectrum band rule (Bio-SFDA-style) | 214/480 (45%) | 429 |

Across the full ROC, the simple envelope threshold rule dominates at every false-acceptance level; comb_v2 dominates C30; the raw-spectrum
rule is dominated everywhere. Envelope gates engage only ≈ 6 of 23 faulty PU bearings (coverage ceiling) and detect no ball faults on
CWRU or UORED.

### 5.5 Gating inside SDALR (M2, bearing-wise clean tasks)
| Arm | seed 2024 | seed 0 |
|---|---|---|
| no gate | 56.0% | 56.6% |
| comb_v2 gate | 59.8% (+3.7) | 60.4% (+3.8) |
| envelope threshold gate | 61.7% (+5.7) | 64.0% (+7.4) |
| raw-spectrum gate (single seed) | 52.1% (−3.9) | — |
| oracle filter (single seed) | 82.7% | — |

Pseudo-label noise is the bottleneck (oracle gap 26.6 points); safe gates close ≈ 19–30% of it; the unsafe gate makes adaptation worse.
Gates break the one-label-per-bearing lock on the bearings they engage (e.g. 55.3% → 69.9% on one task). Seed 1 is running; the
pre-registered decision needs all three seeds.

### 5.6 Mechanism of gate failure and the slip–lock proposition
- Under the cage-slip model, BPFO(s) + BPFI(s) = n for every slip s. If BPFO₀ = m + δ, both outer- and inner-race lines reach integer
  shaft orders **at the same slip** s* = δ/BPFO₀: 1.63% (UORED), 1.74% (CWRU fan end), 1.78% (PU FAG), 2.30% (PU IBU/MTK) — inside the
  normal slip range. Longer windows narrow the confusion band but never remove s*. This refines Smith & Randall's (2015) observation
  that 6203 frequencies "lock onto" shaft harmonics, and contrasts with industry patent claims that such lines separate with more
  spectral lines.
- Measured failure on UORED: a shaft-harmonic comb lit both fault families and the sparse outer-race comb won arbitration.
- A within-CWRU control (fan-end 6203 vs drive-end 6205) did **not** support a population-level effect (p = 0.12); reported honestly.

### 5.7 Dataset hygiene findings
- CWRU fan-end channels recorded during drive-end faults carry the correct drive-end fault signature in 13/52 runs (bearing-level 95% CI
  11–40%), supporting exclusion of those signals from "healthy" test sets.

### 5.8 Negative results reported (credibility)
- Pre-registered H6 (pre-whitening rescues the lock) and H7 (position rules fail while the statistical test succeeds): not supported.
- Ball-fault misses are neither a sideband problem nor a band-selection problem (two pre-registered fixes rejected).
- A fault-frequency-informed band search raised false alarms on UORED to 25–80% even with the search inside the null.

---

## 6. Novelty positioning (nearest work and delta)

| Contribution | Nearest published work | Delta |
|---|---|---|
| Leakage-controlled evaluation of SFDA | Vieira et al., MSSP 2026 (bearing-wise evaluation, supervised, single bench, SFDA out of scope); Hendriks et al., MSSP 2022 | first bearing-wise, paired leaky/clean evaluation of SFDA, with the failure mechanism measured |
| Safety evaluation of physics gates | Bio-SFDA (EAGLE gate), PCTL (physics-consistency validator), Borghesani et al. 2013 (SES statistics) | false acceptance on real healthy bearings and full ROC; no new detector claimed |
| Slip–lock proposition | Smith & Randall, MSSP 2015 (observation); US patents 10,168,248 / 10,598,568 | closed-form simultaneous lock condition and scaling argument |
| Remedy (BIST, running) | DANN / domain-adversarial generalisation over conditions or machines | nuisance variable = physical bearing identity, motivated by measured memorisation, evaluated leakage-safe |
| Not claimed | Matania et al., MSSP 2025 (harmonic-peak invariant features) | our harmonic-coordinate representation is the same idea |

A literature sweep on 2026-09-15 found no competing leakage-safe SFDA evaluation.

---

## 7. Experiments running now (co-author Kaggle account, T4)

1. **C83 — seed 1** for gating (both folds): decides whether gating gains are robust across 3 seeds
   (rule: mean gain ≥ 1 pp, Wilcoxon p < 0.05, positive on every seed).
2. **C85 — SHOT** on the paired leakage design: decides whether the collapse generalises beyond SDALR (rule: Δ ≥ 5 pp, p < 0.05).
3. **C86 — BIST remedy** (bearing-identity-adversarial source training, λ fixed at 1.0): decides whether removing bearing identity recovers
   clean accuracy by ≥ 5 pp (p < 0.05) for SDALR and for SHOT, with a bearing-ID probe and per-bearing purity as mechanism checks.

---

## 8. Limitations (stated in the paper)

- The paired leakage design fits only Paderborn (other public sets lack enough bearings per class across conditions).
- Transfer is cross-condition, cross-bearing on one rig — not cross-machine.
- Two bearing folds; one to three seeds; single SFDA method until SHOT completes.
- Envelope gates engage a minority of faulty bearings and miss ball faults.
- UORED speed resolved for 15/60 files only.

---

## 9. Questions for the supervisor's deep-research review

**Positioning and venue**
1. Is MSSP the right primary venue for an evaluation-plus-mechanism paper with a modest remedy, or would RESS/Measurement be a safer fit?
2. Does any 2025–2026 work (journals, arXiv, PHM conferences) already evaluate SFDA or domain adaptation with bearing-disjoint targets?
3. Has "physical bearing identity" been used as an adversarial or invariance target in any fault-diagnosis or domain-generalisation work?
4. Has the closed-form simultaneous BPFO/BPFI shaft-harmonic lock condition (BPFO + BPFI = n under slip) appeared in the
   bearing-diagnostics literature (Randall, Antoni, Borghesani, Smith groups)?

**Experimental design**
5. Is a paired two-fold design on Paderborn sufficient, or will reviewers require more bearing-level splits (e.g. ≥ 10 permutations)?
6. Which additional SFDA methods beyond SHOT would reviewers expect (NRC, AaD, a 2025 bearing-specific SFDA)?
7. Is there a public dataset other than Paderborn with enough physical bearings per class and multiple conditions to replicate M1
   (e.g. XJTU-SY, IMS run-to-failure, MFPT, newer 2024–2026 datasets)?
8. Are three seeds adequate given measured seed SD ≈ 5 points, or should more seeds be run on the headline tables?

**Method and interpretation**
9. For the remedy, should a stronger baseline (e.g. condition-adversarial training, mixup, or feature whitening) be compared against
   bearing-identity adversarial training?
10. How should cage slip on the PU and UORED rigs be measured or bounded to test the slip–lock proposition directly?
11. Is reimplementing the Bio-SFDA gate mechanism, without their code, acceptable, and how should that comparison be worded?

**Presentation**
12. Is an 80+ entry pre-registration change log an asset (supplementary) or a risk for engineering reviewers?

---

## 10. Next steps and timeline

| Step | Owner | When |
|---|---|---|
| Finish C83 seed 1, C85 SHOT, C86 BIST (running) | automated | next ~14 GPU-h |
| Apply pre-registered decisions; update results and figures | analysis | on completion |
| Finalise manuscript sections 6.5, remedy section, conclusion | writing | this week |
| Supervisor review of positioning questions (section 9) | supervisor | parallel |
| Preprint (arXiv/SSRN) | authors | by 2026-10-18 |
| References, author details, declarations | authors | before submission |
| Submit to MSSP | authors | after preprint |

---

## Update 2026-09-16 — response to supervisor review

1. **C86 stopped before it ran** (no GPU used). Replaced by C87: a class-conditional bearing adversary (BIST-W). It runs only
   if a within-class bearing-ID probe first shows identity is decodable (N1, queued).
2. **Ten random 3/3/3 bearing splits (C88)** are drawn, built and queued. Each split runs leaky, clean, clean + envelope gate and
   clean + oracle filter. Groups 1–2 run on the co-author account; groups 3–4 run on the primary account after Saturday's reset.
3. **Gating comparison is paired**, verified from logs (identical pre-adaptation accuracy). Three seeds (C83, decided):
   comb_v2 +4.03 pp (p = 0.007), envelope threshold gate +7.05 pp (p = 0.0007), positive in every seed, worst task −0.70 pp.
4. **Decomposition** (matched variant): 70 % filter-recoverable, 30 % not. The share is fold-dependent (fold A 101 %, fold B
   48 %), so the abstract will report the distribution over the 10 splits.
5. **Measured slip (C90):** median 0.06 % on Paderborn. Recordings within the lock tolerance: [0, 0.99 %] of 304. The slip
   proposition becomes a remark, and "within normal slip" is withdrawn.
6. **Manuscript v0.2** is restructured into a single thread. Gate ROC moves to S2, hygiene to S3, and the title owns the
   single-rig scope.
7. **New, running on Kaggle CPU (C91):** random-forest baselines on the same paired design, testing whether the collapse is
   SDALR-specific. SHOT (C85) is running on GPU.
