# Physics-Gated SFDA for Cross-Machine Bearing Fault Diagnosis — Definitive Execution Plan

**Rev 5 — FINAL. Approved after three external reviews. Frozen design, zero experiments run.**
**Governing order:** `KICKOFF.md` (facts) → `ADDENDUM_A.md` (architecture, experiments, paper) → this file (execution).
**Target:** RESS primary; MSSP / *Measurement* / AEI secondary.
**Start date:** 2026-09-13. Target submission: **December 2026**.

---

## 0. Verified numerical foundations

Everything in this section was computed this session, not asserted. Four blockers were found across
three review rounds; all are closed. The two that survive into the paper as *findings* are §0.2 and §0.3.

### 0.1 Kinematics — reproduced to 4 dp

`r = (Bd/Pd)·cos α`; `BPFO = (n/2)(1−r)`, `BPFI = (n/2)(1+r)`, `FTF = ½(1−r)`,
`BSF = (Pd/2Bd)(1−r²)`, **`BPFB = 2·BSF`** (the searched defect line).

| | 6205 (`n=9, Bd=0.3126″, Pd=1.537″`) | 6203 (`n=8, Bd=0.2656″, Pd=1.122″`) |
|---|---|---|
| BPFO | **3.5848** | **3.0531** |
| BPFI | **5.4152** | **4.9469** |
| FTF | **0.3983** | **0.3816** |
| BSF (spin) | **2.3567** | **1.9938** |
| BPFB (2×BSF) | **4.7134** | **3.9877** |

**Identities, exact for every geometry:** `FTF = BPFO/n`; `BPFB` lies between the race lines iff
`2/(n+2) < r < 2/(n−2)` — holds for both, so `BPFO < BPFB < BPFI`. **6203 requires `n = 8`**; `n = 9`
gives BPFO 3.4348 and fails. **Never infer pitch diameter from bore and OD** — 6203's Pd happens to
equal (17+40)/2 but 6205's is 39.04 mm against a 38.5 mm mean.

**BSF assertions go against the formula, never a table.** Smith & Randall report 1.994 for the 6203
(true spin); CWRU's table reports 3.9874 (2× spin). Both are correct under their own convention,
which is why table-picking failed twice. `configs/bearings.yaml` records each source's convention.

### 0.2 The 6203 shaft-harmonic lock — **FINDING, keep in the paper**

Smith & Randall, verbatim:

> "Three of the bearing characteristic frequencies for the SKF 6203-2RS JEM deep groove bearing are
> close to integer multiples of shaft speed, with values of 4.947, 3.053 and 1.994 (×fr) for BPFI,
> BPFO and BSF… In some of the results, the bearing frequencies appear to lock onto these shaft
> harmonics, making it difficult to establish a definite diagnosis."

Orders are speed-independent, so the lock is **intrinsic to the geometry**:

```
6205 (CWRU drive end)            6203 (CWRU fan end / PADERBORN)
BPFO  −10.38% from 4·f_r         BPFO   +1.77% from 3·f_r   COLLISION
BPFB   −5.73% from 5·f_r         BPFB   −0.31% from 4·f_r   COLLISION
BPFI   +8.30% from 5·f_r         BPFI   −1.06% from 5·f_r   COLLISION
FTF   −60.17% from 1·f_r         FTF   −61.84% from 1·f_r   clear
→ 0 of 4 collide                 → 3 of 4 collide
```

**BPFB sits 0.31% from 4·f_r — even `s_max = 0.005` collides. No window width separates them.**
Harmonics do not help: the offset is relative, constant at +1.77% for k = 1…5. The only available
discriminant is **cyclostationary order**, not frequency position. Paderborn is our headline dataset,
so this hits B2, B3, M0 and M1.

**Consequence — the mandatory fix and the mechanism claim.** Discrete/random separation before
envelope analysis is now step 1.5. It was a real omission: Smith & Randall's own benchmark method is
built on DRS, and their **Method 2 (cepstrum pre-whitening) achieved the highest success rate of the
three**. Shaft harmonics are CS1 (phase-locked); bearing faults are CS2 (slip destroys phase
coherence). Borghesani et al. 2013 is *"Testing second order cyclostationarity…"* and analyses CS1
contamination of the SES directly — **our null was already the right null for this failure mode.**

### 0.3 Resolution feasibility — **FINDING, keep in the paper**

At the 2048-sample window inherited from SDALR, the slip window contains no native bins:

```
              T        revs   Δf=1/T     BPFO      slip win   native bins
CWRU @1772  170.7 ms   5.04   5.86 Hz   105.87 Hz   2.12 Hz     0.361
PU N15      32.0 ms    0.80  31.25 Hz    76.33 Hz   1.53 Hz     0.049
PU N09      32.0 ms    0.48  31.25 Hz    45.80 Hz   0.92 Hz     0.029
```

A PU window is **0.8 shaft revolutions**. Three consequences:

1. **`M = 9` per anchor is impossible on Paderborn at any window length.** Our BPFO window is
   *one-sided* (width `s·BPFO`), so `T ≥ M/(s·f_line)`: PU N15 needs 5.90 s and PU N09 needs 9.83 s
   against 4-second records. (A two-sided reading understates this by 2×.)
2. **The representation is degenerate at 2048, not only the gate.** At Δf = 31.25 Hz the fault
   channels land in the *same native bin* as the shaft channel: O k=1 and S k=3 → bin 2; B k=1 and
   S k=4 → bin 3; I k=1 and S k=5 → bin 4.
3. **The family statistic is what makes the fix feasible.** Window width scales with harmonic index,
   so bins accumulate: CWRU 68, PU N15 92, **PU N09 55**. The impossible constraint was `M` per
   anchor, never the record length — so **no operating condition needs to be dropped.**

### 0.4 The Track A window is **derived, not chosen**

Constraints: (a) BPFO/3·f_r separation ≥ 2 bins; (b) pooled family bins ≥ 20; (c) ≥ 5 revolutions.
Evaluated on the worst case (PU N09, 6203):

```
T=1.0s  sep 1.33  famN09 13.7   fail
T=1.5s  sep 1.99  famN09 20.6   fail
T=2.0s  sep 2.66  famN09 27.5   PASS   ← smallest feasible
T=4.0s  sep 5.31  famN09 55.0   PASS
```

**`T_A = 2.0 s`, pre-registered.** PU: 128,000 samples @ 64 kHz. CWRU: 24,000 @ 12 kHz.

### 0.5 Welch averaging is ruled out by arithmetic

```
1 seg: DOF 2  Δf 0.25 Hz  6.1 bins  OK      4 seg: DOF 8  Δf 1.00 Hz  1.5 bins  TOO FEW
2 seg: DOF 4  Δf 0.50 Hz  3.1 bins  OK      8 seg: DOF 16 Δf 2.00 Hz  0.8 bins  TOO FEW
```

**One segment, no Welch — pre-registered.** Variance reduction comes from the family sum instead:
Gamma(N,1) has CV = 1/√N, so N = 92 gives 10.4% against 100% for a single χ²₂ ordinate. **The family
sum is the averaging, and unlike Welch it preserves the resolution the windows depend on.** This
closes the only remaining post-hoc-tunable knob.

### 0.6 Track A sample counts and A7 power — both risks resolved

PU: 32 bearings × 4 conditions × 20 records × 4 s. At `T_A = 2.0 s` with 50% within-record overlap
(3 windows/record, never crossing a record boundary):

| class | bearings | windows | ~60% train split |
|---|---|---|---|
| healthy | 6 | 1440 | 864 |
| outer | 12 | 2880 | 1728 |
| inner | 11 | 2640 | 1584 |

Adequate. **Risk downgraded from Med-high.**

A7 Jaccard at record level, N ≈ 640 target records per task: SE ≈ 0.020, 95% CI half-width ≈ 0.039.
A Jaccard of 0.85 vs 0.60 is comfortably distinguishable. **Risk downgraded.**

### 0.7 Corrections carried forward

- My C/O dependency justification was **vacuous**: `C[k=n] ≡ O[k=1]` needs k = 8 or 9, but K = 5, so
  it is never sampled. The conclusion (union bound, not independence) stands; the real dependency is
  **bin collision at coarse resolution** (§0.3).
- Šidák is wrong for χ²₂ ordinates (100% CV) and discards the family structure. Replaced by a
  **family-sum statistic with an exact Gamma null**.
- PCTL verified from the full PDF: scores `s_pred = P_phy(E(x_t))` — its own reconstruction — is
  **not source-free**, and **requires labelled target data**.
- Bio-SFDA's "4-bit pattern" is **[VERIFIED]** from the published Highlights. My four *absence*
  claims (no FAR control, no null, no stratification, no leakage analysis) remain **struck** pending
  Session 0.
- "Withdrawn" must never appear for arXiv 2302.12533 — it is flagged, not withdrawn.
- The ADDENDUM's monotone warp is **impossible** (§0.1 ordering). Replaced by harmonic coordinates.

---

## 1. Change log C11–C19 → `PROTOCOL.md` §13

| ID | Change | Justification |
|---|---|---|
| C11 | Mandatory DRS (cepstrum pre-whitening) as step 1.5; rungs **L2.5**; hypotheses **H6, H7** | §0.2 — no window width separates the 6203's lines; DRS is Smith & Randall's own pre-processing and their best method |
| C12 | Gate snaps to native bins; **no interpolation**. `test_gate_null.py` verifies FAR empirically | Interpolation correlates bins and rescales variance, invalidating the null |
| C13 | `BSF`/`BPFB` asserted **against the formula only**; each source's convention recorded | "BSF" denotes two quantities across CWRU / Smith & Randall / mirrors |
| C14 | Multiplicity: exact Gamma within family → union bound across families → **BH across records**. `expected_false_accepts` is a ledger column | α was per-position only; false acceptances scale with N |
| C15 | Ledger gains `runner_id, kaggle_account, artifact_path`; append-only per-runner shards. `datasets.yaml` gains `licence`, `redistribution`; all Kaggle Datasets private | Multi-account co-authors; CSV merge conflicts; PU citation conditions |
| C16 | Session 0 adds *"did Bio-SFDA use PU artificial-damage bearings only, and at what window length?"*. H4 confound declared. `paper/` gains CRediT/DAS/COI stubs. Dated calendar | Reframes "their number is unsound" → "their task may be easier than it sounds" |
| **C17** | **Two-track design.** Track R: 2048 windows, SDALR as published, M0/M1 only. Track A: `T_A = 2.0 s` windows, KNEOS-HC, gate, L0–L8, H1–H7. **Gate verdicts are per record, inherited by child windows.** Cross-track comparisons never made silently | §0.3 — at 2048 both gate and representation are degenerate. Every window of a record shares one physical fault state, so a per-window physical verdict was never meaningful |
| **C18** | **Family-sum statistic** replaces per-position Šidák; exact Gamma(N_c,1) null; per-anchor `M` dropped from the gate (kept only for the representation tensor); **one segment, no Welch** | §0.5, §0.7 — more powerful, pre-registers the resolution trade-off, makes PU N09 feasible |
| **C19** | **Numerical feasibility gate.** Compute a component's governing quantities and assert workable range *before* implementing it. Standing halt condition; **first** Session-1 test | Blockers 1 and 4 were invisible in prose and appeared only on doing the arithmetic. Guards catch bad results, not bad specifications |

None changes a `[FROZEN]` item. C11/C12/C14/C17/C18 specify what was underspecified or infeasible;
C13 corrects an error; C19 adds a guard.

---

## 2. Architecture — KNEOS-HC

### 2.1 Novelty ledger — do not claim any TAKEN row

| Idea | Status | Reference |
|---|---|---|
| Sub-bands centred on fault frequencies + harmonics | **TAKEN** | Sadoughi & Hu, *IEEE Sensors J.* 2019; *EAAI* 103:104295, 2021 |
| Center-surround spectral filters at fault frequencies (RUL, one rig) | **TAKEN** | Muñoz Gutiérrez & Wotawa, SFRF, arXiv 2506.12375 |
| Resampling by characteristic frequency for cross-system transfer | **PARTLY TAKEN** | Rong & Lee, *SHM* 2025, doi 10.1177/14759217251363600 — resamples the **time signal**; confirm Session 0 |
| Cepstrum pre-whitening / DRS before envelope analysis | **TAKEN — standard** | Randall & Antoni *MSSP* 25(2) 2011; Smith & Randall 2015 Method 2 |
| Envelope spectrum as cross-device alignment representation | **TAKEN** | conditional kernel Bures metric learning, PMC11085194 |
| Physics-informed feature weighting in cross-machine UDA | **TAKEN** | PIUDA, *AEI* 62:102774, 2024 |
| Physics reliability functional gating pseudo-labels in SFDA | **TAKEN** | Bio-SFDA (EAGLE), *Results in Eng.* 30:111105, 2026 |
| **Geometry-independent multi-family harmonic coordinates carrying sidebands, shared by BOTH the network input AND a record-level FAR-controlled cyclostationarity-order test with an exact family-sum null, source-free** | **NOT FOUND** | — |

**Claim the conjunction, narrowly:** *the gate's null and the network's input occupy the same
harmonic coordinates, which is what lets a cyclostationarity-order test replace a frequency-position
rule where the two coincide.*

### 2.2 Pipeline

1. **Angular resampling** to constant angular increment → shaft-order axis.
2. **1.5 — Discrete/random separation `[C11, MANDATORY]`** — cepstrum pre-whitening (default),
   linear-prediction residual (alternative), TSA where a tacho exists.
3. **Band selection per record** — fast kurtogram (baseline) / IESFOgram (ablation) / fixed (floor).
4. **Squared envelope spectrum**, one segment, no Welch `[C18]`.
5. **Harmonic coordinates** — one channel per family:

   | Ch | Family | Positions | Purpose |
   |---|---|---|---|
   | `O` | Outer | `k·BPFO` | race line |
   | `I` | Inner | `k·BPFI + j·f_r` | shaft sidebands are the inner-race signature |
   | `B` | Ball | `k·BPFB + j·FTF` | cage sidebands; `BPFB = 2·BSF` |
   | `C` | Cage | `k·FTF` | independent of O at K=5 (§0.7) |
   | `S` | Shaft | `k·f_r` | CS1 residual; **asserted near-empty after step 1.5** |

   Pre-registered: `K = 5`, `J = 2`, `M = 9`, `s_max = 0.02`, `T_A = 2.0 s`.

6. **Two sampling rules for two purposes — state this explicitly in the paper:**
   - **Gate:** snap to native bins, pool across the family, exact Gamma null `[C12, C18]`.
   - **Representation:** interpolate onto `M = 9` sub-bins per anchor for fixed tensor shape
     `(5, K, 2J+1, M)`. *Interpolation is legitimate here because no statistical null is claimed for
     the network input.* The two share **anchor positions and windows**, differing only in
     discretisation within a window. **Do not overclaim them as identical.**

### 2.3 Slip windows — one pre-registered constant, `s_max = 0.02`

```
BPFO : [(1−s_max)·BPFO, BPFO]                   # one-sided, exactly −s_max, geometry-independent
BPFI : [BPFI, (1 + s_max·BPFO/BPFI)·BPFI]       # one-sided, geometry-dependent — compute per bearing
BPFB, FTF : symmetric ±s_max                     # UNVERIFIED under slip, documented as such
```

Never hard-code +1.32%; that is the 6205 value. **On the 6203 these windows contain shaft harmonics
at any width** — separation comes from step 1.5 and the CS2 null, never from window geometry.

### 2.4 Why harmonic coordinates, not the addendum's monotone warp

| Single monotone warp | Harmonic coordinates |
|---|---|
| Anchors non-monotone (`BPFO < BPFB < BPFI`) — no interpolant exists | No global map; no ordering assumption |
| Harmonic `k` lands at a geometry-dependent position | Harmonic `k` **is index `k`**, every bearing |
| No coordinate for sidebands | Sidebands are an explicit tensor dimension |
| Shaft content pollutes the axis | Channel `S` isolates it; asserted near-empty post-DRS |
| Warping distorts the noise floor, breaking the null | Native-bin pooling → **null preserved exactly** |

### 2.5 The gate `[C17, C18]`

**Granularity: per record.** Verdicts inherited by every child window.

```
T_c = Σ_{b ∈ S_c} SES(b)/σ²(b)          S_c = native bins in ∪ₖ window(k·f_c)
H₀ :  T_c ~ Gamma(N_c, 1)                σ²(b) = Borghesani non-white, CS1-aware variance scale
τ_c(α) = Gamma.ppf(1 − α, N_c)
```

Accept pseudo-label `c` iff `T_c > τ_c(α)` **and** no competing family carries greater normalised
evidence. Otherwise withhold from the supervised loss (A4 decides entropy-only use).
Max-statistic reported as a sensitivity.

**Multiplicity `[C14, C18]`:** exact Gamma within family → **union bound across the 5 families**
(they share native bins at coarse resolution — §0.7, *not* `C[k=n] ≡ O[k=1]`) → **Benjamini–Hochberg
across records**. `expected_false_accepts` on every ledger row.

### 2.6 Pre-registered hypotheses

| | Hypothesis | Decision rule |
|---|---|---|
| **H1** | Zero-shot: source-only CWRU→PU, KNEOS-HC > plain SES > raw 1D | **Fails ⇒ drop the architecture claim, do not defend it** |
| **H2** | Geometry generalisation on HUST held-out models | **[BLOCKED — geometry missing]** |
| **H3** | Gate acceptance ↔ classifier confidence associate more strongly under KNEOS-HC | Reported either way |
| **H4** | KNEOS-HC beats angular resampling alone (L3). **Confound declared:** CWRU carries nominal RPM with no tacho, so L3 is artificially weak there, biasing H4 *in our favour*. Run primarily on PU/JNU | Fails ⇒ say so in the abstract |
| **H5** | `J=2` beats `J=0` | Fails ⇒ drop sidebands, simplify |
| **H6** | Without step 1.5, PU outer-race gate precision is at chance; with it, materially above | Fails ⇒ report as a negative finding and lead with it |
| **H7** | On PU, a frequency-position rule (PCV-style, EAGLE-style — both our reimplementations) is at chance for the outer race while the CS2-order test is not | **The sharpest prediction in the paper** |

### 2.7 Ablation ladder — `[FROZEN]`, Track A

```
L0    raw 1D, resnet18_1d                            floor
L1    plain SES, fixed band
L2    L1 + per-record fast kurtogram
L2.5  L2 + discrete/random separation                ← C11; expected large effect
L3    L2.5 + angular resampling                      ← H4 null
L4    L3 + harmonic coordinates, J=0                 ← H5 lower arm
L5    L4 + sidebands J=2  =  KNEOS-HC                ← the contribution
L6    L5 + IESFOgram band selection
L7    L5 + log-envelope spectrum
L8    L5 + admissibility mask as input channel       only if L5 wins
```

FiLM **cut**. No attention, no Transformers, no KANs. Backbone `resnet18_1d` from
`ZhaoZhibin/UDTL`, input-adapted only.

### 2.8 Limitations to state plainly

Requires known geometry and measured shaft speed. JNU blocked on `Z`; HUST geometry blocked (H2
unavailable). **On the 6203 the lines are not separable from shaft harmonics by position at any
window width.** Track A uses 2 s windows with declared 50% within-record overlap, never crossing a
record boundary. Smith & Randall proved many CWRU records carry no fault signature at all. Compound
faults excite multiple channels; reported separately. `K, J, M, s_max, T_A` pre-registered, not
tuned; one appendix sensitivity sweep.

---

## 3. Evaluation protocol — a contribution, so it gets a section

### 3.1 Splitting — `[FROZEN]`

1. **Bearing-wise.** No physical bearing on both sides of any task. Enforced by a load-time
   assertion that hard-fails, itself tested with a deliberately leaky config.
2. **Healthy split bearing-wise too** (Vieira et al., *MSSP* 258:114640, 2026). PU has six healthy
   bearings. **CWRU has effectively one healthy configuration and cannot be split this way** —
   stated explicitly; prefer PU/HUST as the healthy source cross-machine.
3. Fixed-length windows; **no overlap across a split or record boundary**; within-record overlap
   declared (50%, Track A).
4. **Secondary table:** every method re-run under the conventional condition-wise (leaky) split.
   **The delta is the headline deliverable.**

### 3.2 Label spaces — `[FROZEN]`

`L3 = {Normal, Inner, Outer}` wherever PU is involved (PU has no ball class);
`L4` adds Ball/Roller for CWRU ↔ JNU ↔ HUST. Compound faults excluded from main tables, reported
separately as an out-of-label-space stress test.

### 3.3 Benchmark suite

| Block | Tasks | Track | Split | Space |
|---|---|---|---|---|
| **B0** reproduction | PU A1↔A2↔A3 (6), JNU B1↔B2↔B3 (6) | R | as published (leaky) | 8-class / 4-class |
| **B1** leakage delta | same 12 | R | bearing-wise | L3 / L4 |
| **B2** cross-machine | CWRU↔PU, CWRU↔HUST, PU↔HUST (6) | A | bearing-wise | L3 |
| **B3** fidelity | PU-artificial → PU-real | A | bearing-wise by construction | L3 |
| **B4** geometry | HUST held-out models | A | bearing-wise | L4 — **blocked** |
| **B5** stress | compound / out-of-label-space | A | bearing-wise | — |

Methods: `source-only`, `SHOT`, `SDALR`, one prototype/clustering SFDA, `confidence-threshold`,
**`PCV-style rule`, `EAGLE-style rule`** (our reimplementations, for H7), `gated (ours)`,
`oracle (SHOT-clean)`. Seeds `[0,1,2,3,4]`, fixed in advance, never reselected.

### 3.4 Metrics — `[FROZEN]`

1. **Oracle-gap closure** `(gated − ungated)/(oracle − ungated)` — the headline.
2. **Leaky-vs-clean delta** per method per task.
3. **Pseudo-label noise transition matrix**, before/after gating.
4. **Diagnosability-stratified gate precision/recall** per Smith & Randall stratum.
5. **Gate ROC** as α sweeps; **realised vs nominal FAR**.
6. **A7 Jaccard** — gate-rejected vs confidence-rejected. **Confidence aggregated to record level
   (mean and majority, both reported)** before comparison `[C17]`, with power reported alongside.
7. Per-class always, **ball/roller separate** (pre-registered weak). Macro-F1 with accuracy.
   Mean ± std over 5 seeds, never best-of.
8. **ECE and NLL** — Bio-SFDA reports these; we must too.
9. `expected_false_accepts`, `N_records`.

### 3.5 Statistics

Paired Wilcoxon signed-rank pairwise; Friedman + Nemenyi for >2 methods across many tasks. **A method
that wins on the mean but fails the test is reported as not significant.** No hyperparameter is ever
tuned on target data — tuning happens on a source-domain validation split and is logged in
`DECISIONS.md`.

### 3.6 Reliability scorecard — the table the paper leads with

`Acc_leaky | Acc_clean | Δ_leak | MacroF1_clean | OGC | ECE_clean | Gate-P@Y1Y2 | Gate-R@N1N2 | Sig`

A large `Δ_leak` means **less trustworthy**, not better. That framing makes this a RESS paper rather
than an accuracy paper.

---

## 4. Repository layout

```
KICKOFF.md  PROTOCOL.md  ADDENDUM_A.md  CLAUDE.md  DECISIONS.md  README.md
.gitignore  requirements.txt
notes/       bio_sfda.md  pctl.md  sensors_benchmark.md  pmmcp.md  rong_lee.md  POSITIONING.md
configs/     bearings.yaml  datasets.yaml  splits.yaml  tasks.yaml  ablations.yaml  windows.yaml
data_prep/   ingest.py  window.py  split.py  checksums.py
physics/     kinematics.py  feasibility.py  prewhiten.py  band_select.py  ses.py
             harmonic_coords.py  gate.py
models/      resnet18_1d.py  heads.py
sfda/        shot.py  sdalr.py  proto.py  gated.py  oracle.py  rule_baselines.py
eval/        metrics.py  strata.py  scorecard.py  stats.py  power.py
kaggle/      pack_repo.py  push.py  poll.py  pull.py  preflight.py  hello_t4.py  budget.py
metadata/    smith_randall_cwru.csv
tests/       test_feasibility.py  test_kinematics.py  test_harmonic_coords.py  test_splits.py
             test_gate_null.py  test_prewhiten.py
results/     ledger/<runner_id>.csv   runs/   artifacts/   FAILURE_*.md
paper/       figures/  tables/  credit.md  data_availability.md  coi.md
```

### 4.1 Component specs

**`physics/feasibility.py` `[C19]` — runs before anything else.** For every
`(dataset, condition, bearing, track)`: pooled family bins `N_c ≥ 20`; anchor/shaft-harmonic
separation `≥ 2` bins or flag `POSITION-DEGENERATE` and route to the DRS-dependent path;
revolutions per window `≥ 5`; one segment. **Emits `configs/windows.yaml` — window lengths are
derived, not chosen.**

**`configs/bearings.yaml`** — `n, Bd_in, Pd_in, alpha`, `source:` URL, `verified:`.
`N205, NU205, 6204, 6206, 6207, 6208` are `verified: false` with `blocked_on:`. Records the JNU
assignment (**N205 → normal/outer/roller; NU205 → inner**, Li et al., *Sensors* 2013, 13(6):8013–8041)
with a footnote that several widely-cited secondary papers state the reverse. Records the BSF
convention of every external source `[C13]`.

**`configs/datasets.yaml`** — paths, `fs`, class maps, RPM tables, `licence:`, `redistribution:`
`[C15]`. All Kaggle Datasets **private**.

**`physics/kinematics.py`** — returns `BPFO, BPFI, FTF, BSF, BPFB` (`BPFB = 2·BSF`, never
conflated). **Raises `UnverifiedBearingError`** for `verified: false`. `slip_window()` per §2.3.
CLI: `python physics/kinematics.py --bearing 6205 --rpm 1772`.

**`physics/harmonic_coords.py`** — asserts `BPFO < BPFB < BPFI` per bearing and raises otherwise;
asserts `FTF == BPFO/n`; **raises unless `feasibility.py` has certified the tuple** `[C17, C19]`;
returns the interpolated representation tensor **and** the snapped native-bin index sets for `gate.py`.

**`physics/gate.py`** — record-level; family-sum statistic, exact Gamma null; union bound across
families; BH across records `[C17, C18]`.

**`kaggle/push.py`** — T4 enforced **in code**; asserts `enable_gpu: true`; **exits non-zero without
pushing** for any accelerator other than `NvidiaTeslaT4`. Shells out to the resolved `kaggle`
executable — **never `import kaggle`** (PATH python is 3.11.15 without it; the CLI is under 3.13).

**`results/ledger/<runner_id>.csv`** `[C15]` — append-only per-runner shards merged by script.
Columns: `run_id, runner_id, kaggle_account, git_sha, config_hash, task, method, rung, seed,
split_type, label_space, track, window_samples, n_records, <metrics>, expected_false_accepts,
wall_clock, gpu_hours, kernel_url, artifact_path`. **The pulled artifact is retained alongside every
row. No number enters the manuscript that is not traceable to a ledger row. Nothing is hand-copied.**

**`metadata/smith_randall_cwru.csv`** — header only; human fills:
`record_id,channel,fault_type,clock_position,fault_size_in,load_hp,fs_hz,rpm,method1,method2,method3,notes`
with each `methodN ∈ {Y1,Y2,P1,P2,N1,N2}` (Y = success, P = partial, N = unsuccessful; Method 1 raw,
Method 2 discrete/random separation, Method 3 + spectral kurtosis). **Derive any ordinal collapse in
`eval/strata.py`, never in the CSV.**

---

## 5. Session plan

### Session 0 — evidence acquisition. **NO CODE.**

1. **Bio-SFDA full text** (PII `S259012302602133X`, gold OA) → `notes/bio_sfda.md`, with section
   refs: EAGLE's exact mechanism and whether it has FAR control; measured vs model-generated input;
   datasets, classes, **window lengths**; **exact split procedure and whether bearings recur**;
   per-task numbers; baselines; limitations. **Plus two `[C16]` questions:**
   *(a) Did they use PU's artificial-damage bearings only?* Artificial EDM faults resemble CWRU's,
   which would make CWRU→PU a far smaller shift than the label implies — **no leakage required**,
   reframing our claim to "their task may be easier than it sounds": safer and equally publishable.
   *(b) What window length?* If 2048 on PU, §0.3 says their physics module read degenerate
   coordinates — a second mundane explanation for 99.0% that needs no leakage either.
2. **PCTL full text** (ein.org.pl, OA) → confirm verbatim: Algorithm 1's `s_pred = P_phy(E(x_t))`
   input line, and *"This stage utilizes a small set of labeled target domain data."* → `notes/pctl.md`.
3. **Sensors 2025, 25(14):4383** (MDPI OA, PubMed 40732511, U-NetVAE, four datasets) → exact label
   space, split procedure, preprocessing, and the F1 ≈ 0.47 / recall ≈ 0.51 figures →
   `notes/sensors_benchmark.md`. This is the anchor of the central tension.
4. **`predictive-maintenance-mcp`** (`github.com/LGDiMaggio`) benchmark code → is its Smith & Randall
   transcription reusable? → `notes/pmmcp.md`.
5. **Rong & Lee 2025** (*SHM*, doi 10.1177/14759217251363600) → **time signal or spectrum axis?** →
   `notes/rong_lee.md`.

**Acceptance:** five notes files with direct quotations and section references, plus a one-page
`notes/POSITIONING.md` stating which of the three claims survive contact with the full texts.
**Gate:** if Bio-SFDA uses bearing-wise splits **or** FAR control, **re-scope before writing code.**

### Session 1 — feasibility, scaffold, verified Kaggle bridge

No training, no gate integration, no dataset uploads.
**Acceptance — seven tests; test 1 runs before any other component exists `[C19]`:**

1. **`test_feasibility.py`** — for every `(dataset, condition, bearing, track)`: pooled family bins
   `N_c ≥ 20`; anchor/shaft-harmonic separation `≥ 2` bins or flagged degenerate; revolutions `≥ 5`.
   **Asserts the 2048-sample Track-A configuration FAILS** — a regression guard making Blocker 4
   impossible to reintroduce. Emits `configs/windows.yaml` with `T_A = 2.0 s`.
2. **`test_kinematics.py`** — 6205 BPFO 3.5848 / BPFI 5.4152 / FTF 0.3983 at `atol=1e-4`;
   6203 (`n=8`) 3.0530 / 4.9469 / 0.3817 at `atol=1e-4`. **`BSF`/`BPFB` against the formula only** —
   2.3567 / 4.7134 and 1.9938 / 3.9877. `BPFB == 2·BSF` and `FTF == BPFO/n` exactly.
   `ΔBPFO/BPFO == −s_max` to machine precision; slip signs asserted. `kinematics(N205)` and
   `kinematics(6206)` raise. **The 6203 collision is asserted as a documented regression guard.**
3. **`test_gate_null.py`** — white and coloured noise; realised FAR matches α within Monte-Carlo
   error, **for the family-sum Gamma null** `[C18]`.
4. `python physics/kinematics.py --bearing N205` raises a clear unverified-geometry error.
5. `python kaggle/push.py --accelerator NvidiaTeslaP100` exits non-zero **without pushing**.
6. `python kaggle/preflight.py` reports no kernel queued or running.
7. `results/hello_t4.json` contains `device_name: "Tesla T4"`, `capability: [7,5]`.
   **Nothing proceeds until this prints.**

All tests run on CPU in under 60 s. Commit `session1: feasibility + scaffold + verified Kaggle T4
bridge`. Write change-log C1–C19 into `PROTOCOL.md` §13.

| S | Deliverable | Gate |
|---|---|---|
| 2 | Dataset loaders + private Kaggle Datasets (CWRU DE, PU first); checksum, class-count and licence assertions | — |
| 3 | `splits.yaml` + load-time bearing-overlap assertion, **tested with a deliberately leaky config** | — |
| 4 | **M0 (Track R)** reproduce SDALR on its own PU + JNU tasks. **Dump pseudo-labels and confidences, window- and record-aggregated** | >2 pp miss ⇒ **stop and reassess the literature** |
| 5 | **M1 (Track R)** PU relabelled to L3, bearing-wise. Two numbers, one delta | The delta is a result either way |
| 6 | Track A preprocessing: `prewhiten`, `band_select`, `ses`, `harmonic_coords`; precompute + cache on CPU | Channel `S` near-empty post-DRS **asserted**; feasibility certified |
| **6b** | **H1 zero-shot CWRU→PU at L0/L1/L2.5/L3/L5**, no adaptation | **H1 fails ⇒ drop the architecture claim, keep gate + protocol** |
| **6c** | **H6/H7 on PU 6203** — gate precision ± DRS; PCV-style and EAGLE-style rules vs the CS2 test. **CPU-only** | The paper's mechanistic core |
| 7 | **M2 / A7** gate + record-level Jaccard with reported power | **Jaccard > 0.85 ⇒ pivot to the protocol paper** |
| 8 | **M3** oracle-gap table, 3 tasks | Tiny gap ⇒ reframe: noise was not the bottleneck |
| 9 | **M4** diagnosability stratification | Core external-validation result |
| 10 | **M5** PU-artificial → PU-real | The fidelity hypothesis test |
| 11 | Full ladder L0–L8, 3 tasks, 5 seeds | H4 reported regardless, with its confound stated |
| 12 | **M6** full matrix, 5 seeds, Wilcoxon/Friedman, scorecard, figures | Submission-ready |

Sessions **6b and 6c run before gate integration**. Both are cheap (6c is CPU-only) and together
they gate the two largest risks: an architecture claim that does not hold, and a gate that cannot
work on the headline dataset.

### 5.1 Compute budget

| Block | Runs | GPU-h |
|---|---|---|
| M0 reproduction (Track R) | 36 | ~4 |
| H1 zero-shot | 50 | ~2 |
| H6/H7 | 0 (CPU) | 0 |
| M1 leakage delta | 60 | ~6 |
| M2/A7 + M3 | 90 | ~7 |
| Ladder (10 rungs × 3 tasks × 5 seeds) | 150 | ~12 |
| Full matrix B2/B3 (9 methods × ~8 tasks × 5 seeds) | 360 | ~28 |
| **Total** | ~750 | **~59 GPU-h ≈ 2 weeks of quota; budget 4 weeks with reruns** |

Kaggle: **9 h GPU session cap, ~30 h/week, resets Saturday 00:00 UTC, T4 only** (P100 is sm_60;
PyTorch needs sm_70+). Every training script checkpoints to `/kaggle/working` and is resumable.
`kaggle/budget.py` prints projected GPU-hours before each session; over quota ⇒ **reduce scope and
name the deferred experiments — never silently shorten training or drop seeds.**

### 5.2 Calendar — write into `DECISIONS.md` before Session 1

| Milestone | Date |
|---|---|
| Sessions 0–1 | by **2026-09-20** |
| M0 + M1 (Sessions 2–5) | by **2026-10-04** |
| **Hard preprint deadline** — whatever M1 says | **2026-10-18** |
| M2–M5 (Sessions 6–10) | by **2026-11-01** |
| Full matrix (Sessions 11–12) | by **2026-11-22** |
| **Target submission** | **December 2026** |

Scoop runway is 6–12 months; the preprint is the hedge and its date does not move.

---

## 6. Autonomous loop and guards

```
while milestones remain:
  read PROTOCOL.md → next unblocked milestone
  C19: compute the component's governing quantities; assert workable range
  verify preconditions (tests green, no kernel queued, quota remaining)
  write code; run unit tests locally on CPU
  push to Kaggle (T4 enforced in code); poll; pull; retain artifact
  append rows to results/ledger/<runner_id>.csv
  evaluate the milestone's decision rule
  PASS → commit, tag, advance    FAIL → STOP, write results/FAILURE_<milestone>.md, surface
```

**Halt and require a human decision on any of:** a decision rule fails · a published baseline missed
by **>2 pp** · weekly quota below **3 h** · a change would touch `[FROZEN]` · **a result is better
than expected by a wide margin** — treat exactly as a failure and check leakage before celebrating;
***not optional, our whole paper is about numbers that were too good*** · a checksum or class-count
assertion fails · a `[BLOCKED]` item is needed next · **`feasibility.py` cannot certify a tuple**.

Every deviation that could raise a headline number is logged in `DECISIONS.md` with the number
before and after. **Reporting that our method loses is authorised and expected.** Fabricating or
flattering a result is the one failure mode from which this project cannot recover.

---

## 7. Paper assembly

**Framing.** RESS is a reliability and safety journal, not an ML venue. "Better accuracy on CWRU"
desk-rejects. Frame throughout as **trustworthiness of automated diagnosis under deployment
conditions**: the gate is a screening mechanism controlling false acceptance at a stated rate;
leakage-safe evaluation asks whether reported reliability claims hold when the monitored machine is
not the one you trained on. That vocabulary is not spin — it is what the work is.

1. **Introduction** — Zhao et al.'s UDTL survey naming *physical priors* a rarely-studied open issue;
   the Bio-SFDA 99.0% vs benchmark F1 ≈ 0.47 tension as the motivating puzzle; the three claims.
2. **Related work** — PIUDA, PCTL, Bio-SFDA, SDALR, Sadoughi & Hu, SFRF, Rong & Lee,
   `predictive-maintenance-mcp`, each with an explicit stated delta.
3. **Method** — kinematics; **the 6203 lock (§0.2)** and **the resolution feasibility analysis (§0.3)**
   as motivation and as a methodological contribution in its own right — *no published
   physics-guided method we found states its spectral-resolution requirement, and some use windows at
   which their own fault coordinates are degenerate*; DRS; harmonic coordinates with the
   non-monotonicity proof; the family-sum CS2 test at level α; the closed-form slip model; multiplicity.
4. **Evaluation protocol** — *a contribution, so give it the space of one.*
5. **Results** — scorecard; ladder; oracle-gap closure; **H6/H7**; noise transition matrices;
   per-class with ball/roller separate; stratified gate precision/recall; leaky-vs-clean delta.
6. **Discussion** — where the gate fails and why; the artificial-vs-real fidelity axis; §2.8 limitations.
7. **Conclusion** — no overclaiming. If the gate closed 40% of the oracle gap, say 40%.

**Figures that earn their place.** (i) **The 6203 lock** — PU envelope spectrum with BPFO/BPFB/BPFI
windows and 3/4/5·f_r overlaid, before and after DRS. (ii) **The resolution figure** —
bins-per-slip-window vs window length, 2048 marked, feasible region shaded. *These two carry the
paper; make them excellent.* (iii) CWRU and PU fault lines landing on the same harmonic coordinates.
(iv) The leaky-vs-clean delta table. (v) Gate ROC with realised vs nominal FAR. (vi) Gate
precision/recall by Smith & Randall stratum. (vii) Ablation ladder, grouped bars with error bars.
(viii) t-SNE last and small — expected in this literature, proves nothing.

**Submission artefacts** — `paper/credit.md` (CRediT), `data_availability.md`, `coi.md`, stubbed now.
Public repo, frozen split files, the transcription, the merged ledger, a one-command reproduction
script. **In a paper arguing this field's evaluation is unreliable, the artefact is the argument.**

---

## 8. Risk register

| Risk | P | Mitigation | Trigger |
|---|---|---|---|
| Gate redundant with confidence filtering | **High** | A7 at S7; pseudo-labels dumped at S4 | Jaccard > 0.85 ⇒ pivot to protocol paper |
| H1 fails — no zero-shot gain | Med-high | S6b before gate code | Drop architecture claim; keep gate + protocol |
| H6 fails — DRS does not rescue the 6203 | Med | S6c, CPU-only, early | Report as a negative finding and lead with it |
| H4 fails — all gain is order tracking | Med | Mandatory L3 + declared CWRU confound | Say so in the abstract |
| Bio-SFDA leakage-safe, PU-artificial-only, or 2048-window | Med | Session 0 gate | Re-scope claims 1 and 3 before coding |
| HUST/JNU geometry never resolved | Med-high | Both `[BLOCKED]`, raise not return | Drop B4 and H2; L3-only cross-machine |
| ~~Track A sample counts too small~~ | **Resolved §0.6** | `T_A=2 s` + 50% within-record overlap → 864/1728/1584 per class | — |
| ~~A7 underpowered at record level~~ | **Resolved §0.6** | N≈640 ⇒ 95% CI half-width ±0.039 | — |
| Real spalls degrade the gate | Expected | Pre-registered fidelity axis | Report as a finding, not a weakness |
| Ball/roller class fails | Expected | Pre-registered prediction | Per-class reporting |
| Compute overrun | Low | `budget.py`, CPU caching, resumable checkpoints | Defer B5, name it |
| Scooped during execution | Med | **Hard preprint 2026-10-18** | — |

---

## 9. Open items assigned to the human

| # | Item | Blocks |
|---|---|---|
| 1 | **Transcribe `metadata/smith_randall_cwru.csv`** from Table 4, per-method columns, no collapsing. **Check `predictive-maintenance-mcp` first** | Session 9 |
| 2 | **JNU roller count `Z` and roller diameter** (N205/NU205) from a catalogue or by contacting Jiangnan University | all JNU kinematics |
| 3 | **HUST 6204/6206/6207/6208 ball count, ball diameter, pitch diameter** | H2, B4 |
| 4 | **HUST per-load shaft RPM** (0/200/400 W) from the BMC full text or the Mendeley per-file field | HUST tasks |
| 5 | **Sign off the pre-registered constants** — `s_max=0.02, K=5, J=2, M=9, T_A=2.0 s`, one-segment/no-Welch — before any gate result is seen | S6c onward |
| 6 | **Obtain Bio-SFDA and PCTL full texts** | Session 0 |
| 7 | **Record the calendar (§5.2) in `DECISIONS.md`** | Session 1 |
| 8 | **Confirm dataset licences** for redistribution as private Kaggle Datasets | Session 2 |

---

## 10. Honest probability assessment

**Novelty.** The conjunction in §2.1's last row is unoccupied across six independent searches. Every
component has neighbours — Sadoughi & Hu own fault-frequency receptive fields, Rong & Lee own
characteristic-frequency resampling, Bio-SFDA owns physics-gated pseudo-labels in SFDA. **Claim the
coupling, narrowly.** A broad claim will be correctly shot down.

**Acceptance.** No plan makes it certain. What raises it most is not more architecture — it is the
integrity apparatus plus **two sharp, verified findings that arrived before any experiment**: the
6203 shaft-harmonic lock and the resolution feasibility analysis. Both are quotable, both are
checkable by a reviewer in five minutes, and both bear directly on why a 99.0% headline on CWRU→PU
deserves scrutiny — **without requiring us to allege leakage.**

- **Likeliest strong outcome:** the leakage result holds; H6/H7 confirm the lock and the CS2 test's
  advantage; the gate closes a meaningful but not spectacular share of the oracle gap; KNEOS-HC gives
  a real but modest zero-shot gain. Solid Q1 in RESS/MSSP/*Measurement*. **Headline numbers will be
  below published SOTA and the paper explains why.**
- **Plausible weaker outcome:** A7 shows near-total overlap ⇒ pivot to the protocol-and-stratification
  paper, now carrying both findings. Still Q1-viable; evaluation-critique papers have precedent in
  exactly these venues.
- **Genuine failure mode:** neither gate nor KNEOS-HC helps and the leakage delta is small ⇒ an
  honest negative-results benchmark study. Q2-viable, still worth publishing.
- **The outcome that must never occur:** a headline number obtained by relaxing the split policy.

**The meta-lesson, encoded as C19.** Blockers 1 and 4 were both invisible in prose and surfaced only
on doing the arithmetic. Guards that catch bad *results* do not catch bad *specifications*. Every
component now computes its governing quantities and asserts they are workable **before** it is built.

---

## 11. Verification

Session 1 completes when the seven acceptance tests in §5 pass — **test 1 (feasibility) first** —
and `git status` is clean. Each later session completes when its gate evaluates PASS **and** every
reported number traces to a ledger row with a retained artifact. Any FAIL writes
`results/FAILURE_<milestone>.md` and stops the loop for a human decision.

**Immediate next action on approval: Session 0. No code.**
