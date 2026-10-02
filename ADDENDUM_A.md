# ADDENDUM A — Architecture, Integrity Protocol, and Autonomous Execution

> Layers on top of `KICKOFF.md`. Read `KICKOFF.md` first. Where the two conflict, `KICKOFF.md` wins
> on facts; this document wins on architecture, experiment strategy, and paper assembly.

---

## A0. READ THIS BEFORE ANYTHING ELSE — what "winning" means here

Success on this project is defined operationally, and not as headline accuracy:

> We win by being the only method in the comparison table whose numbers survive bearing-wise
> splitting, and by being able to say exactly how much everyone else loses when it is applied.

If you ever find yourself considering a change that would raise a headline number — a different
split, a longer window, dropped hard classes, a reselected seed, a hyperparameter tuned after
seeing test performance — **stop and surface it to the researcher as a decision, never make it
silently.** Log it in `DECISIONS.md` with the number before and after.

**You are authorised, and expected, to report that our method loses.** A well-executed negative
result with the diagnostic analysis explaining why is publishable in this field and is our
pre-registered fallback. Fabricating or flattering a result is the one failure mode from which
this project cannot recover.

---

## A1. Architecture prior-art ledger — `[VERIFIED]`

Before designing anything, know what is occupied. These are all real and must be cited.

| Idea | Status | Reference |
|---|---|---|
| Differentiable / learnable time-frequency front-end for cross-machine bearing transfer | **TAKEN** | pyDSN — modulated differentiable STFT with learnable windows + physics-informed balanced spectrum metric, *Adv. Eng. Informatics* (arXiv 2406.11917) |
| Parameterised filter kernels (SincNet-style, wavelet kernels) in bearing CNNs | **TAKEN** | WaveletKernelNet; SincNet (Ravanelli & Bengio 2018) applied in diagnostics |
| Resampling signals by characteristic frequency for cross-system transfer | **PARTLY TAKEN** | Rong & Lee, *Structural Health Monitoring*, 2025 (resamples the **time signal**, e.g. 51.2 kHz → 10 kHz) |
| Generalising across many bearing designs via simulated training data | **TAKEN** | Kiakojouri & Wang, *Sensors* 25(8):2378, 2025 |
| Envelope spectrum as a cross-device alignment representation | **TAKEN** | Cross-machine envelope spectrum + conditional kernel Bures metric learning (Sensors/PMC11085194) |
| Dual 1D-signal / 2D-spectrogram encoder for bearing SFDA | **TAKEN** | Bio-SFDA, *Results in Engineering* 30:111105, 2026 |
| Physics-guided reliability functional gating pseudo-labels in SFDA | **TAKEN** | Bio-SFDA (EAGLE module) — internals UNVERIFIED, see Session 0 |
| Rule-based physics validator supervising a confidence predictor | **TAKEN** | PCTL, *Eksploatacja i Niezawodność* 28(2):211797, 2026 |
| FiLM / hypernetwork conditioning on bearing kinematic parameters | **NOT FOUND** — thin on its own | — |
| FAR-controlled statistical test (Borghesani et al. 2013) as a pseudo-label gate in DA | **NOT FOUND** | — |
| Envelope-spectrum axis normalised to fixed fault-order positions across geometries | **NOT FOUND — VERIFY IN SESSION 0** | — |

**Do not claim novelty for anything in the top block.** Two searches are not a literature review;
treat the bottom three rows as hypotheses to be falsified in Session 0, not as established gaps.

---

## A2. The architecture: KNEOS — Kinematics-Normalised Envelope Order Spectrum

### A2.1 The physical argument it rests on

Cross-machine transfer fails partly for a reason nobody has to learn: **the fault lines are not in
the same place.** CWRU drive-end is a 6205 at ~1772 rpm sampled at 12 kHz; Paderborn is a 6203 at
1500 rpm sampled at 64 kHz. BPFO for the 6205 sits at 3.5848·f_r; for the 6203 at 3.0531·f_r. In
Hz, after different sampling rates and different shaft speeds, the outer-race signature lands at a
different bin index in every dataset. A convolutional network trained on one is being asked to
recognise, in the other, a pattern that has been translated and rescaled by an amount determined
entirely by known bearing kinematics.

This is a *solvable* misalignment, and the information needed to solve it — element count, ball
diameter, pitch diameter, contact angle, shaft speed — is available for every dataset we use.
The network should not be spending capacity learning a coordinate transform we can write down.

### A2.2 The transform

Given a raw window, its bearing's kinematics, and its measured shaft speed:

1. **Angular resampling.** Resample to constant angular increment using the measured/estimated
   shaft speed, producing a signal in shaft orders rather than Hz. Removes speed dependence.
2. **Band selection.** Fast kurtogram (baseline) or IESFOgram (upgrade), per sample, per dataset.
   Never a fixed band — resonance bands differ by rig.
3. **Squared envelope spectrum** of the band-passed analytic signal, on the order axis.
4. **Kinematic warping — the novel step.** Warp the order axis by a monotone map `φ` such that the
   four fault families land at **fixed canonical positions independent of bearing geometry**:

   ```
   φ(BPFO_order) = 1.0
   φ(BPFI_order) = 2.0
   φ(BPFB_order) = 3.0        # BPFB = 2·BSF, see KICKOFF §C1
   φ(FTF_order)  = 0.5        # optional anchor
   ```

   Use a monotone piecewise-linear (or monotone cubic / PCHIP) interpolant through the anchor
   points, with harmonics mapping automatically to integer multiples of their anchor. Resample the
   SES onto a fixed canonical grid.
5. **Slip band.** Carry `s_max = 0.02` through the warp so each anchor becomes an interval, not a
   point, with the asymmetry derived per bearing (BPFO biased low by exactly `s_max`; BPFI biased
   high by `s_max·(BPFO/BPFI)`).

**Result:** every sample from every machine and every bearing presents its outer-race evidence at
canonical position 1.0, inner-race at 2.0, ball at 3.0, with harmonics at integer multiples. A
convolutional kernel that learns "energy at 1.0 and its harmonics ⇒ outer race" transfers across
bearing geometry by construction rather than by adaptation.

### A2.3 Why this is the right novelty for *this* paper

- **It is derived, not bolted on.** It follows from the same kinematics as the gate. The gate and
  the representation become one object: the gate is a hypothesis test at canonical positions on
  the same axis the network sees. Reviewers reward that kind of coherence.
- **It attacks the paper's own subject.** Our thesis is about cross-machine shift. This is a
  mechanism for part of that shift.
- **It is cheap.** A preprocessing transform, computed once per dataset on CPU and cached. Costs
  no GPU-hours, which matters against a 30 h/week quota and 9 h sessions.
- **It makes a falsifiable prediction** (see A2.4). Untestable architectures get rejected;
  testable ones get discussed.
- **It degrades gracefully.** If it fails, the failure is interpretable and reportable.

### A2.4 The falsifiable hypotheses — pre-register these before running

**H1 (zero-shot alignment).** If cross-machine failure is substantially a representation
misalignment problem, then a source model trained on KNEOS should transfer to a new machine
**with no adaptation at all** better than the same model trained on a plain envelope spectrum.
*Test:* source-only accuracy, CWRU→PU, KNEOS vs plain SES vs raw 1D, no SFDA.
**This is the single most important experiment in the architecture track.** It is cheap, it runs
early, and if H1 fails the architecture claim should be dropped rather than defended.

**H2 (geometry generalisation).** A model trained on a subset of HUST's five bearing models
(6204–6208) and tested on held-out models should degrade less under KNEOS than under a plain
spectrum. HUST is the only dataset that gives a clean within-rig test of geometry generalisation —
use it for exactly this.

**H3 (gate–representation coherence).** Gate acceptance rate and classifier confidence should be
more strongly associated under KNEOS than under a plain spectrum, because both now read the same
coordinates.

**H4 (the null that must be beaten).** KNEOS must beat **angular resampling alone** (shaft-order
normalisation without kinematic warping). If the entire benefit comes from order tracking, we have
reimplemented computed order tracking and must say so. **This ablation is mandatory and must be
reported even if unflattering.**

### A2.5 Optional second component — only if H1 passes

**Kinematic conditioning (FiLM).** Condition normalisation layers on the bearing's kinematic
signature vector `[n, Bd/Pd, cos α, BPFO, BPFI, BPFB, FTF]`. Apparently unpublished for bearings,
but **thin as a standalone contribution** and it risks the "unmotivated complexity" rejection.
Add it only as an ablation row, only after KNEOS is established, and only if it earns its place.
**Do not lead with it. Do not add anything else.** No attention modules, no Transformers, no KANs.

### A2.6 Known limitations to state in the paper, not hide

- Requires known bearing geometry and measured shaft speed. Available in all four of our datasets
  and normally available industrially from spec sheet plus tachometer, but it is a real deployment
  constraint. State it.
- Roller bearings (JNU N205/NU205) are blocked on roller count `Z`; KNEOS cannot be applied there
  until resolved.
- The warp assumes the fault lines are where kinematics say they are, within the slip band.
  Smith & Randall proved that for many CWRU records they are not present at all — which is exactly
  why the stratification analysis is in the paper.
- Compound faults (PU KB\*, HUST 2-combinations) excite multiple anchors at once. Out of scope for
  the main tables; report separately.

---

## A3. Experiment discipline

### A3.1 Pre-registration is binding

Before any experiment runs, `PROTOCOL.md` must contain: the hypothesis, the metric, the split, the
seeds, and the decision rule. After results are seen, **the protocol does not change** — only the
change log grows, with justification. If a result suggests a better experiment, that is a *new*
pre-registered experiment, not a revision of the old one.

### A3.2 The mandatory ablation ladder

Every architectural claim climbs this ladder in order. A rung may not be skipped because it is
expected to be unflattering.

```
L0  raw 1D signal, ResNet-18-1d                       (the floor)
L1  plain envelope spectrum (SES), fixed band
L2  SES + per-sample band selection (fast kurtogram)
L3  L2 + angular resampling (shaft-order axis)        ← H4's null
L4  L3 + kinematic warping = KNEOS                    ← the contribution
L5  L4 + IESFOgram band selection
L6  L4 + log-envelope spectrum                        (non-Gaussian robustness)
L7  L4 + FiLM kinematic conditioning                  (only if L4 wins)
```

Report every rung, on every task, with the same seeds. If L4 does not beat L3, say so in the
abstract.

### A3.3 Seeds and statistics

Five seeds minimum, fixed in advance (`[0,1,2,3,4]`), never reselected. Report mean ± std, never
best-of. Paired Wilcoxon signed-rank across tasks for pairwise comparisons; Friedman with post-hoc
when comparing more than two methods across many tasks. **A method that wins on the mean but fails
the significance test is reported as not significant.**

### A3.4 Hyperparameters

Take SDALR's published hyperparameters unchanged for the SFDA components (SGD, batch 64, source
lr 7e-3 / 10 epochs, target lr 5e-4 / 20 epochs, decay `lr₀·(1+10p)^(−0.75)`). Any tuning happens
on a **source-domain validation split only**, never on target data, and is logged. If you tune on
target performance, the paper is dead and so is the finding.

### A3.5 Experiment ledger

Every run appends one row to `results/ledger.csv`: run id, git SHA, config hash, task, method,
ablation rung, seed, split type, all metrics, wall-clock, GPU-hours, Kaggle kernel URL. **No
number enters the manuscript that is not traceable to a ledger row.** Nothing is hand-copied.

---

## A4. Autonomous execution loop

You may run this loop without asking permission for each step, provided every guard holds.

```
while milestones remain:
    1. read PROTOCOL.md; select the next unblocked milestone
    2. verify preconditions (tests green, no kernel queued, quota remaining)
    3. write/modify code; run unit tests locally on CPU
    4. push to Kaggle (T4 enforced in code); poll; pull
    5. append rows to results/ledger.csv
    6. evaluate the milestone's decision rule
    7. if PASS  -> commit, tag, advance
       if FAIL  -> STOP. Write results/FAILURE_<milestone>.md and surface to researcher.
    8. update PROTOCOL.md change log if and only if a [VERIFY] item was specified
```

**Guards — any one of these halts the loop and requires a human decision:**

- A milestone decision rule fails.
- Reproduction of a published baseline misses its reported number by more than 2 percentage points.
- Remaining weekly GPU quota drops below 3 hours.
- A result would require changing a `[FROZEN]` item.
- A result is *better than expected* by a wide margin — treat suspiciously high numbers exactly as
  you treat failures, and check for leakage before celebrating. **This guard is not optional.**
  Our whole paper is about numbers that were too good.
- Any dataset file fails a checksum or class-count assertion.

**Budget discipline.** Before each session, print projected GPU-hours for the planned matrix.
If it exceeds remaining quota, reduce scope and say which experiments were deferred — never
silently shorten training or drop seeds.

---

## A5. Paper assembly

### A5.1 Scope fit — RESS specifically

RESS is a **reliability and safety** journal, not a machine-learning venue. A paper framed purely
as "better accuracy on CWRU" is out of scope and will be desk-rejected. Frame throughout as:
**trustworthiness of automated diagnosis under deployment conditions** — the gate is a screening
mechanism that controls false acceptance at a stated rate; leakage-safe evaluation is about whether
reported reliability claims hold when the monitored machine is not the one you trained on. Use the
vocabulary of false-alarm rates, screening, and deployment validity. That framing is not spin; it
is what the work actually is.

If the leakage/protocol result dominates and the gate underperforms, **Measurement** or **MSSP**
become better fits than RESS — MSSP especially, since Smith & Randall, Hendriks, and Vieira all
live there and the framing is native to that readership.

### A5.2 Structure to write toward

1. **Introduction** — anchor on Zhao et al.'s UDTL survey naming *physical priors* as a rarely
   studied open issue; state the Bio-SFDA 99.0% vs benchmark F1 ≈ 0.47 tension as the motivating
   puzzle; state the three claims.
2. **Related work** — PIUDA, PCTL, Bio-SFDA, SDALR each with an explicit stated delta. Cite
   `predictive-maintenance-mcp` for Smith & Randall stratification. Do not hope reviewers miss any
   of these.
3. **Method** — kinematics; KNEOS; the gate as a Borghesani-threshold hypothesis test with
   false-alarm rate α; the slip model with its closed form.
4. **Evaluation protocol** — bearing-wise splits; label spaces L3/L4; the leaky-split secondary
   table; diagnosability strata. **This section is a contribution, so give it the space of one.**
5. **Results** — ablation ladder; oracle-gap closure; noise transition matrices; per-class with
   ball/roller separate; stratified gate precision/recall; the leaky-vs-clean delta table.
6. **Discussion** — where the gate fails and why; the artificial-vs-real fidelity axis; limitations
   from A2.6 stated plainly.
7. **Conclusion** — no overclaiming. If the gate closed 40% of the oracle gap, say 40%.

### A5.3 Figures that earn their place

- Ablation ladder as a single grouped bar chart with error bars.
- **The leaky-vs-clean delta table** — likely the most-cited object in the paper.
- Gate ROC as α sweeps (Type I vs Type II on a physically defined null).
- Gate precision/recall by Smith & Randall stratum.
- One worked envelope-spectrum figure showing the KNEOS warp aligning CWRU and PU fault lines.
  This single figure carries the architecture argument; make it excellent.
- t-SNE, last, small. It is expected in this literature but proves nothing.

### A5.4 Reproducibility package

Public repo, frozen split files, the `smith_randall_cwru.csv` transcription, the ledger, and a
one-command reproduction script. In a paper arguing that this field's evaluation is unreliable,
the artefact is not decoration — it is the argument.

---

## A6. Honest probability assessment

Say this to the researcher once, then get to work.

- **Likeliest strong outcome:** the leakage/protocol result holds, the gate closes a meaningful but
  not spectacular share of the oracle gap, KNEOS gives a real but modest zero-shot gain. That is a
  solid Q1 paper in RESS, Measurement, or MSSP. Headline numbers will be *below* published SOTA and
  the paper will explain why.
- **Plausible weaker outcome:** the gate overlaps almost entirely with confidence filtering (A7).
  Pivot to the protocol-and-stratification paper. Still Q1-viable, precedent exists for
  evaluation-critique papers in these venues.
- **Genuine failure mode:** neither the gate nor KNEOS helps and the leakage delta is small. Then
  the honest paper is a negative-results benchmark study — Q2-viable, and still worth publishing.
- **The outcome that must never occur:** a headline number obtained by relaxing the split policy.

Acceptance is not guaranteed by anything in this document. What is achievable is a paper whose
claims survive review because they were true when written.
