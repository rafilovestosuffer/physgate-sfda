# SESSION 2 — Data layer, with a blocking re-derivation first

> Read order unchanged: `KICKOFF.md` → `ADDENDUM_A.md` → `PLAN.md` → `PROTOCOL.md`.
> This file is a **§13 change-log input plus a session brief**. It does not change any `[FROZEN]`
> item. Where it contradicts `PLAN.md` §0.4/§0.6, this file wins, because `PLAN.md` §0 was computed
> at `T_A = 2.0 s` and `T_A` has since moved to 3.0 s (C21) without §0.6 being re-derived.
>
> **Everything below carries a verification status. Do not upgrade a status without a primary source.**

---

## 0. Why this session starts with arithmetic, not code

C19 says: compute a component's governing quantities and assert a workable range **before**
implementing it. The dataset loader's window contract *is* `T_A`. `T_A` changed after the sample
counts that justified it were computed. So S2.0 below is a **halt condition**, not a warm-up.

An external audit of the plan (2026-09-13) found four factual errors and two novelty exposures.
Section 1 is the change log. Section 2 is the work.

---

## 1. Change-log entries — append to `PROTOCOL.md` §13

### C27 — `PLAN.md` §0.6 is void. Track A PU window counts must be re-derived. `[VERIFIED by arithmetic]`

PU records are **4.0 s**. §0.6 computed per-class window counts at `T_A = 2.0 s` with 50 %
within-record overlap and no record-boundary crossing, giving 3 windows/record. C21 then moved
`T_A` to 3.0 s. At 3.0 s with the same rule the hop is 1.5 s and **only one window fits per record**.

| | `T_A` = 2.0 s | `T_A` = 3.0 s |
|---|---|---|
| windows / PU record | 3 | **1** |
| healthy (6 bearings) | 1440 | **480** |
| outer (12 bearings) | 2880 | **960** |
| inner (11 bearings) | 2640 | **880** |
| CWRU windows / ~10 s record | 9 | 5 |

`PLAN.md` §8 still shows *"~~Track A sample counts too small~~ **Resolved §0.6**"* with the 2.0 s
figures. **That strike-through is withdrawn.** The risk returns to open at Med.

Note the 50 % rule is what forces 1 window. Windows at `[0,3]` and `[1,4]` fit at **66.7 %**
overlap, giving 2/record. That is a legitimate option but it is a *change to a declared quantity*
and must be logged in `DECISIONS.md` with the before/after, not made silently.

### C28 — CWRU healthy-class split: our stated limitation is weaker than published practice. `[VERIFIED]`

`PROTOCOL.md` §3.2 and `PLAN.md` §3.1.2 state CWRU "has effectively one healthy configuration and
cannot be split bearing-wise." Vieira et al. (MSSP 2026, 258:114640) — the paper we already cite —
construct a leakage-free CWRU healthy split: they **exclude the healthy/healthy configuration
entirely**, treat each sensor as monitoring its co-located bearing, and then either train on the
drive-end healthy bearing and test on the fan-end healthy bearing, or the reverse.

Two things follow:

1. We must **engage with this construction explicitly**, not restate the limitation. Citing a paper
   and then ignoring its solution is a reviewer's free shot.
2. Their construction rests on an assumption worth testing: that a sensor at a healthy location
   reports a healthy bearing even when a faulted bearing sits at the other end of the same shaft.
   Vieira themselves flag the analogous concern for the healthy/healthy configuration. **This is a
   free, CPU-only, publishable experiment for us**: gate the CWRU fan-end healthy signals from
   faulted configurations at level α and report the realised acceptance rate. If cross-end
   contamination is measurable, we have improved a 2026 MSSP protocol using our own gate. Log as
   candidate experiment **B6**; do not promise it in the abstract until it runs.

### C29 — Claim ordering changes. `[DECISION — requires researcher sign-off]`

Evidence:

- Vieira et al., MSSP 2026, 258:114640 proposes leakage-free bearing-wise partitioning, evaluates
  on CWRU / PU / UORED-VAFCLS / HUST bearing, surveys 18 papers from 2025, and runs the controlled
  leaky-vs-clean experiment (model fixed, test set varied) which they claim as a first.
- Rosa, Braga & Silva (arXiv 2407.14625), same group: multi-label CWRU benchmark, identifies
  residual leakage in Hendriks and Abburi, uses Smith & Randall to explain errors.
- **However**, Vieira explicitly scopes themselves out of our territory: *"The present work…focuses
  on a simpler yet fundamentally critical problem: training and testing within a single testbench."*
  They name inter-testbench / cross-domain work as the alternative they are **not** doing.

So claim 1 is **not** taken — but it cannot be worded as *"a leakage-safe evaluation protocol."*
That wording is now occupied. New ordering:

| # | Claim | Wording discipline |
|---|---|---|
| **1** | The physics screen as a **record-level, FAR-controlled pseudo-label gate for source-free domain adaptation**, with an exact family-sum null, multiplicity control across records, and realised-vs-nominal FAR reported on real data. | Claim the **gate**, never the **test** — see C30. |
| **2** | External validation of that gate against Smith & Randall's per-record diagnosability categories, under domain shift. | Cite `predictive-maintenance-mcp` and differentiate: ours is under shift, theirs is in-domain and rule-based. |
| **3** | **The first leakage-safe evaluation of SFDA methods for bearing diagnosis**, applying Vieira et al.'s bearing-wise methodology to the cross-machine source-free setting, and measuring how much published SFDA gain survives it. | Vieira is the **methodology source**, cited as such. Our delta is SFDA + cross-machine + stratification. |

### C30 — Claim 1 must be narrowed: CFAR on the SES is prior art. `[VERIFIED — corrects an earlier audit claim]`

An earlier audit note said the FAR-controlled test was "not pre-empted anywhere." **That is too
strong.** CFAR thresholding of the squared envelope spectrum already exists in condition
monitoring — e.g. an adaptive Autogram approach using a CFAR detector on the square-envelope
spectrum for incipient cavitation, and CFAR-derived condition indicators in US Army helicopter
HUMS. Borghesani et al. (2013) and Antoni before them already give statistical CS2 thresholds.

**What we may claim:** the *use* of such a test as a **record-level pseudo-label gate inside
source-free domain adaptation**, sharing harmonic coordinates with the network input, with
Benjamini–Hochberg control of expected false accepts across records. Not the detector.
Add a "TAKEN" row to `PLAN.md` §2.1 for CFAR-on-SES.

### C31 — H4 risk is High, not Medium, on published evidence. `[VERIFIED]`

Jeong et al. (*Sensors* 2025, 25(14):4383) — the paper we cite as the F1 ≈ 0.47 anchor — has as its
**first stated contribution** an order-frequency preprocessing method that normalises rotational
variation across machines. Their own ablation, target domain:

| configuration | target F1 |
|---|---|
| baseline (no order transform) | 0.23 |
| **+ order-spectrum preprocessing** | **0.46** |
| + reconstruction | 0.46 |
| + test-time training (full method) | 0.50 |

Order normalisation alone carries **0.23 → 0.46**; everything learned adds 0.04. That is direct
published evidence for the exact failure mode H4 is designed to catch: *the gain is order tracking.*

Consequences, all mandatory:

- `PLAN.md` §8 row "H4 fails — all gain is order tracking": **Med → High**.
- **L3 (angular resampling alone) runs before any KNEOS-HC code is written.** If L4/L5 do not beat
  L3, we have reimplemented computed order tracking and the architecture claim dies there —
  cheaply, on CPU-cached features, before GPU hours are spent.
- Jeong et al. enters `PLAN.md` §2.1 as prior art for **order normalisation inside SFDA**, not only
  as an F1 anchor.

### C32 — Prior-art ledger gaps. `[VERIFIED]` Add all five, each with a stated delta.

| Work | Why it matters |
|---|---|
| Vieira, Bauler, Rosa & Silva, *MSSP* 258:114640 (2026) | Owns leakage-safe bearing-wise evaluation. Our methodology source. |
| Rosa, Braga & Silva, arXiv 2407.14625 | Multi-label CWRU benchmark + Smith & Randall error analysis. |
| Zhao, Zio & Shen, *RESS* 245:109964 (2024) | Cross-domain fault-diagnosis benchmark **in our primary target journal**. Not currently cited anywhere. |
| He B. et al., *EAAI* 166:113585 (2026), "Source-free cross-machine fault diagnosis in a two-stage pseudo-supervised framework" | Source-free **and** cross-machine, with adaptive pseudo-label refinement. Nearest competitor. |
| Jiao, Zhang & Cao, *EiN* 28(2):211797 (2026) + the 2026 *Sci. Rep.* physics-guided cross-domain framework | Physics priors + order analysis + pseudo-label self-training already published. |

Also: the "physical priors are rarely studied" Introduction anchor comes from a 2019 preprint
(Zhao Zhibin et al., IEEE TIM 2021). The quote is accurate but **the claim is stale in 2026**. Do
not open the paper on it. Anchor instead on: *physics priors are now common; calibrated ones are not.*

### C33 — The gate null was calibrated without DRS in the loop. `[GAP — must close before any real-data gate result]`

C24 calibrated CA-CFAR on synthetic white and AR(2) backgrounds. But C11 makes cepstrum
pre-whitening (DRS) **mandatory pipeline step 1.5**, and Borghesani et al. (2013) note that cepstral
pre-whitening removes spectral-energy fluctuation along the frequency axis, i.e. it changes the SES
background statistics. **A null calibrated before step 1.5 is not the null the gate will face.**

Required: re-run `test_gate_null.py` with DRS applied to the synthetic backgrounds, same grid
(N ∈ {20,45,95}, α ∈ {0.10,0.05,0.01}, both backgrounds). If realised FAR moves outside ~2 SE of
nominal, the reference/guard bandwidth must be re-fixed on synthetic noise **before any real signal
is gated**, and logged as a C23-style pre-registration. This is a Session 6 blocker; noted now so it
is not discovered late.

---

## 2. Session 2 work

### S2.0 — Feasibility re-derivation. **BLOCKING. No loader code until this passes.**

Extend `physics/feasibility.py` and `tests/test_feasibility.py` to certify the *window contract*,
not just spectral separation. For each (dataset, bearing, operating condition) tuple emit and assert:

```
record_length_s, T_A, overlap_frac, windows_per_record,
windows_per_class, est_train_windows_per_class,
delta_f_hz, bpfo_hz, sep_from_nearest_shaft_harmonic_bins,
pooled_family_bins_N, revolutions_per_window,
raw_input_samples_per_window          # <- new, see S2.3
```

Assertions that must hold, or the tuple is **not certified** and the loop halts:

- `sep_from_nearest_shaft_harmonic_bins >= 2.0` on every certified condition
- `pooled_family_bins_N >= 20`
- `revolutions_per_window >= 5`
- `windows_per_record >= 1`
- `est_train_windows_per_class >= 250` — **new**, added because C27 removed the margin

Then produce `results/feasibility/T_A_sweep.csv` over `T_A ∈ {2.0, 2.5, 3.0, 3.5, 4.0}` ×
`overlap ∈ {0.0, 0.5, 0.667, 0.75}`, and **surface the trade-off to the researcher as a decision**.
Do not pick `T_A` autonomously. C21 derived 3.0 s from resolution alone; the sample-count constraint
was not in that derivation, so the derivation is incomplete, not wrong. The researcher chooses, and
`DECISIONS.md` records window count and separation before and after.

**Acceptance:** sweep CSV exists; every shipped tuple certified; `pytest tests/ -q` green in < 60 s
on CPU; a `results/FAILURE_S2.0.md` written instead if no (T_A, overlap) pair satisfies all five.

### S2.1 — Loaders: CWRU DE and PU

Per `PLAN.md` §4.1, plus:

- Every window carries `bearing_id` as a **first-class field**, not derivable-on-demand. Session 3's
  hard-fail assertion reads this field; if it is reconstructed later from filenames it will be wrong.
- `record_id` too — gate verdicts are per record (C17) and must be joinable.
- CWRU: use **per-file RPM**, never nominal. Assert the RPM field is present and in 1700–1800.
- CWRU healthy: emit `sensor_location ∈ {DE, FE}` and `config_type ∈ {healthy_healthy, faulted}` so
  the C28 / Vieira split is *constructible in Session 3* without reloading. Cheap now, expensive later.
- PU: assert 4.0 s per measurement, 64 kHz, and the 32-bearing roster from `KICKOFF.md`.
- **Do not** load JNU for Track A. C25 stands: JNU is Track R only. Worth noting the structural
  finding is stronger than C25 states — Li et al. (2013) assign *normal, outer and roller* to the
  N205 and *inner* to the NU205, so JNU contains two bearing **types**, not four physical bearings.
  Verify against the files and, if confirmed, C25's justification upgrades from "one bearing per
  class" to "three classes share one bearing type."

### S2.2 — Per-record manifest

`data/manifests/<dataset>.csv`, one row per **record**:

```
record_id, dataset, bearing_id, bearing_model, class_L3, class_L4,
operating_condition, rpm, rpm_source, fs_hz, duration_s, n_windows,
sha256, licence, redistribution
```

`rpm_source ∈ {measured, nominal, unknown}` — H4's confound is declared from this column, not from
prose. `licence`/`redistribution` per C15, before anything is uploaded.

### S2.3 — Ladder input-dimension audit. **New, CPU-only, run this session**

At `T_A = 3.0 s` and 64 kHz, an L0 window is **192,000 raw samples**; an L5 KNEOS-HC tensor is
`(5, K=5, 2J+1=5, M=9)` = **1,125 values**. `resnet18_1d` from `ZhaoZhibin/UDTL` is used in that
literature at ~1024–2048-sample inputs. With a few hundred training windows per class, **L0 is not a
floor — it is a strawman**, and H1 ("KNEOS-HC > plain SES > raw 1D") inherits the defect.

Write `results/feasibility/ladder_input_dims.csv` with, per rung: input shape, parameter count,
receptive field, and windows-per-class. Then surface the design choice, do not resolve it silently:

- (a) fix `T_A` across rungs and report L0's dimensional disadvantage as a stated limitation; or
- (b) give L0/L1 the Track R 2048-sample window and **forbid cross-rung claims** between Track R and
  Track A rungs, consistent with C17's "cross-track comparisons never made silently"; or
- (c) decimate the L0 input and declare the decimation.

Whichever is chosen goes in `DECISIONS.md` **before** any ladder result exists.

### S2.4 — Literature reconciliation. NO CODE.

Four notes, each with section references and direct quotations under 15 words:

1. `notes/vieira_2026.md` — full read of MSSP 258:114640. Required: their exact CWRU/PU bearing-wise
   split construction; their CVM-CV hyperparameter protocol; their multi-label + macro-AUROC
   formulation; their controlled leakage experiment design. Then a section headed
   **"What we adopt, what we differ on, and why"** — this is the text that goes in our §Evaluation
   Protocol and it must be written before we run M1, not after.
2. `notes/jeong_2025.md` — the order-preprocessing ablation table (C31), verbatim numbers, and a
   statement of how our L3 differs from theirs (if it does).
3. `notes/POSITIONING.md` — rewritten to the C29 claim order.
4. Bio-SFDA full text remains open. It is now **second** priority behind Vieira.

**Acceptance:** four files exist; `POSITIONING.md` states which claims survive; no claim of novelty
appears anywhere in the repo without a named nearest-neighbour work and a one-sentence delta.

### S2.5 — Kaggle datasets

Only after S2.0 passes and S2.2 manifests validate. Private, versioned, checksummed, T4 path
untouched. `kaggle/preflight.py` clean before any push.

---

## 3. Halt conditions added this session

Append to `PLAN.md` §6:

- `feasibility.py` cannot certify a (dataset, condition, `T_A`, overlap) tuple → halt.
- `est_train_windows_per_class < 250` on any Track A class → halt, surface as a decision.
- A window lacks `bearing_id` or `record_id` → hard fail, not a warning.
- A novelty claim appears in any repo file without a named nearest-neighbour work → halt.

---

## 4. Open items for the human — updated

| # | Item | Blocks | Change |
|---|---|---|---|
| 1 | Transcribe `smith_randall_cwru.csv` | S9 | unchanged |
| 2 | JNU roller count `Z` | JNU kinematics | unchanged; JNU is Track R only regardless |
| 3 | HUST 6204/6206/6207/6208 geometry | H2, B4 | **Softened.** HUST includes **6205**, whose geometry we already hold. NTN and similar publish ball count / ball diameter / pitch diameter for 62-series bearings; C13 already tells us how to validate them (assert against the closed-form formula, record the convention). One more resolved model makes a held-out-model test possible. Manufacturer is unstated in the BMC paper, so treat any catalogue value as `verified: false` until the formula reproduces a published multiplier. |
| 4 | HUST per-load shaft RPM | HUST tasks | unchanged |
| 5 | **Sign off `T_A` and overlap after the S2.0 sweep** | all Track A | **NEW, blocking** |
| 6 | **Sign off the C29 claim reordering** | Introduction, abstract | **NEW, blocking** |
| 7 | Bio-SFDA full text | H7 | demoted below Vieira |
| 8 | Dataset licences | S2.5 | unchanged |

---

## 5. What was checked and found correct — do not re-litigate

Independently reproduced or verified against primary sources on 2026-09-13:

- **Kinematics.** 6205 and 6203 reproduce CWRU's published table to ≤ 2.8e-4; worst case is 6203
  BPFO at 1.19e-4, matching `DECISIONS.md`. `n = 9` on the 6203 gives BPFO 3.4348 and fails. The
  `atol` 2e-4 / 5e-4 split is correct.
- **The 6203 lock (§0.2).** +1.77 % (BPFO vs 3·f_r), −0.31 % (BPFB vs 4·f_r), −1.06 % (BPFI vs
  5·f_r); offset is exactly scale-invariant for k = 1…5. The smallest slip reaching 3·f_r from BPFO
  is s = 0.0174; BPFB collides at any width. **Caveat:** Smith & Randall state the lock verbatim in
  2015. Ours is the *consequence*, not the observation. Word it that way.
- **C24.** Independent Monte-Carlo (20,000 trials, white exponential null): CA-CFAR with an
  F(2n,2m) threshold realises 0.0516 / 0.0500 / 0.0498 at nominal 0.05 for N ∈ {20,45,95}. The
  median-normalised Gamma(N,1) predecessor realises 0.068 / 0.091 / 0.127 and degrades as N grows.
  The switch was correct. Subject to C33.
- **C4 (JNU).** Li et al. (2013) verbatim assign the separable-outer-race N205 to normal, outer and
  roller states, and the separable-inner-race NU205 to the inner-race state. ClassBD
  (arXiv 2404.15341) does state the reverse. Our correction stands.
- **C3 / HUST.** 99 signals, 6204–6208, 3 loads (0/200/400 W), 51,200 Hz for 10 s, Hanoi University
  of Science and Technology, BMC Res. Notes 16(1):138. The 25.6 kHz / 20 s figure in arXiv 2504.11581
  is an error. Trust BMC. Note the dataset is missing ball and inner+ball cases for the 6204.
- **C20.** Fully confirmed from the full text. Jeong et al. use VAT, DXAI, VBL-VA001 and MaFaulDa;
  none of CWRU/PU/JNU/HUST appears; classes are {normal, misalignment, unbalance, bearing} with the
  bearing class merging BPFO, BPFI and cage faults; target-domain F1 is 0.47. **Withdrawing the
  "99.0 % vs 0.47 cannot both be true" framing was the right call and must not be reinstated.**
- **Bio-SFDA.** Real. *Results in Engineering* 30:111105 (2026), PII S259012302602133X, SKKU.
  99.0 % accuracy / 98.5 % macro-F1 / 99.0 % mAP on strict CWRU→PU.
- **SDALR.** PU 8-class where classes are individual bearing IDs (K001, KA04, KA15, KA22, KA30,
  KI14, KI17, KI21); 2048 windows; 2000 samples/class; domains A1/A2/A3 at 1500 rpm. Our structural
  finding — that a bearing-wise split is impossible without redefining their task — is sound.
- **Smith & Randall.** Y1/Y2/P1/P2/N1/N2 across three methods confirmed, and their Method 2
  (pre-whitening) does yield more Y1+Y2 than Method 3, whose spectral kurtosis they report as
  vulnerable to impulsive noise. C11's justification holds.
- **Borghesani et al. 2013.** MSSP 40:38–55, doi 10.1016/j.ymssp.2013.05.012. Derives SES statistics
  under coloured noise, a CS2 threshold test, and the effect of CS1 contamination. The right null.
- **`predictive-maintenance-mcp`.** Real, by L. G. Di Maggio, with an *Applied Sciences* 2026
  paper. 44/44 frequency detection and 34/44 (77.3 %) correct-first-rank on Y1+Y2. Our
  characterisation is accurate. It is a software proof-of-concept, so claim 2 survives with a delta.
- **UDTL survey.** "Physical priors" is genuinely listed among rarely-studied open issues. Accurate
  quote, stale claim — see C32.
- **Venue.** Protocol and benchmark papers do publish in RESS: Zhao, Zio & Shen (245:109964, 2024)
  is one. RESS remains the right primary target under the C29 ordering.

---

## 6. Standing instruction for this session

The plan's integrity apparatus is working — it caught four of its own errors before this audit and
its arithmetic survived independent reproduction. The failure mode it did **not** catch is
positioning drift: the literature moved between the freeze and now. So, for the rest of the project:

> Before any component is built, state its nearest published neighbour and the one-sentence delta.
> If you cannot name the neighbour, you have not searched hard enough — that is a halt, not a green light.

Reporting that our method loses remains authorised and expected.
