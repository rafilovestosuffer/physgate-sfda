# PROGRAMME REV 6 — full revision after external literature audit

**Supersedes `PLAN.md` Rev 5 across §0, §2.1, §2.6, §3.3, §5, §7, §8, §9.**
**Amends `PROTOCOL.md` §1, §4, §6, §7, §13, §14.**
**Does not change any `[FROZEN]` item.** Governing order is unchanged; `PROTOCOL.md` §13 remains
authoritative, and every change below is written as a §13 entry (C27–C41).

Audit date: 2026-09-13. Zero experiments run. Session 2 not yet started.

> **Reading rule for Claude Code.** §1 is the verified-correct register — do not re-derive any of it.
> §2 is the change log. §3–§11 are the revised programme. §12 is the session plan. Start at §12.S2.0.

---

## 1. Verified correct — do not re-litigate, do not re-derive

Reproduced independently or checked against primary sources. Each is closed.

| Item | Status |
|---|---|
| Kinematics 6205 / 6203 | Reproduce CWRU's published table to ≤ 2.8e-4. Worst case 6203 BPFO at 1.19e-4, matching `DECISIONS.md`. Tolerance split 2e-4 / 5e-4 correct. |
| `n = 8` for the 6203 | `n = 9` gives BPFO 3.4348 and fails. Confirmed. |
| 6203 shaft-harmonic lock | BPFO +1.77 % of 3·f_r, BPFB −0.31 % of 4·f_r, BPFI −1.06 % of 5·f_r. Offset exactly scale-invariant for k = 1…5. Smallest slip reaching 3·f_r from BPFO is s = 0.0174; BPFB collides at any width. |
| C24 CA-CFAR calibration | Independent MC, 20 000 trials, white exponential null: F(2n,2m) realises 0.0516 / 0.0500 / 0.0498 at nominal 0.05 for N ∈ {20,45,95}. Median-normalised Gamma(N,1) realises 0.068 / 0.091 / 0.127 and worsens with N. The switch was correct. **Subject to C33.** |
| C4 — JNU assignment | Li et al. (2013) verbatim: separable-outer-race N205 → normal, outer, roller; separable-inner-race NU205 → inner. ClassBD (arXiv 2404.15341) does state the reverse. Our correction stands; mechanics confirm it. |
| C3 — HUST | 99 signals, 6204–6208, 3 loads, 51 200 Hz, 10 s, Hanoi Univ. of Sci. & Tech., BMC Res. Notes 16(1):138. The 25 600 Hz / 20 s figure in arXiv 2504.11581 is an error. Dataset is missing ball and inner+ball for the 6204. |
| C20 — Introduction framing withdrawal | **Fully confirmed from full text.** Jeong et al. use VAT, DXAI, VBL-VA001, MaFaulDa; none of CWRU/PU/JNU/HUST; classes are {normal, misalignment, unbalance, bearing} with the bearing class merging BPFO, BPFI and cage faults; target F1 = 0.47. Withdrawing "99.0 % vs 0.47 cannot both be true" was right. **Never reinstate it.** |
| Bio-SFDA | Real. *Results in Engineering* 30:111105 (2026), PII S259012302602133X, SKKU. 99.0 % acc / 98.5 % macro-F1 / 99.0 % mAP on strict CWRU→PU. |
| SDALR | PU 8-class where classes are bearing IDs (K001, KA04, KA15, KA22, KA30, KI14, KI17, KI21); 2048 windows; 2000 samples/class; A1/A2/A3 at 1500 rpm. Our structural finding is sound. |
| Smith & Randall | Y1/Y2/P1/P2/N1/N2 across three methods confirmed. Method 2 (pre-whitening) yields more Y1+Y2 than Method 3, whose spectral kurtosis they report as vulnerable to impulsive noise. C11's justification holds. |
| Borghesani et al. 2013 | MSSP 40:38–55, doi 10.1016/j.ymssp.2013.05.012. Derives SES statistics under coloured noise, a CS2 threshold test, and CS1 contamination effects. The right null. |
| `predictive-maintenance-mcp` | Real, L. G. Di Maggio, with an *Applied Sciences* 2026 paper. 44/44 frequency detection, 34/44 (77.3 %) correct-first-rank on Y1+Y2. Characterisation accurate. |
| Hendriks, Dumond & Knox | MSSP 169:108732 (2022) confirmed. They argue splitting by operating condition is not a real domain shift because the same physical bearings appear on both sides, and propose independent bearing sets. |
| UDTL survey | "Physical priors" genuinely listed among rarely-studied open issues. Accurate quote, stale claim — see C34. |
| Venue | Protocol/benchmark papers do publish in RESS: Zhao, Zio & Shen 245:109964 (2024). RESS remains correct as primary under the C29 ordering. |

---

## 2. Change log — append to `PROTOCOL.md` §13

### C27 — `PLAN.md` §0.6 is void; Track A PU counts re-derived `[VERIFIED by arithmetic]`

PU records are 4.0 s. §0.6 assumed `T_A` = 2.0 s and 50 % within-record overlap → 3 windows/record.
C21 moved `T_A` to 3.0 s; the hop becomes 1.5 s and **one window fits per record**.

| | 2.0 s | 3.0 s |
|---|---|---|
| windows / PU record | 3 | **1** |
| healthy (6 brgs) | 1440 | **480** |
| outer (12 brgs) | 2880 | **960** |
| inner (11 brgs) | 2640 | **880** |
| CWRU windows / ~10 s record | 9 | 5 |

The strike-through in `PLAN.md` §8 ("~~Track A sample counts too small~~ Resolved §0.6") is
**withdrawn**; risk returns to open. Windows at `[0,3]` and `[1,4]` fit at 66.7 % overlap giving
2/record — a legitimate option, but a change to a declared quantity, so it is logged, not assumed.

### C28 — CWRU healthy split: our limitation is weaker than published practice `[VERIFIED]`

Vieira et al. (MSSP 2026, 258:114640) construct a leakage-free CWRU healthy split: exclude the
healthy/healthy configuration, treat each sensor as monitoring its co-located bearing, then train on
the drive-end healthy bearing and test on the fan-end healthy bearing, or the reverse. We must engage
with this, not restate our limitation.

Their construction assumes a sensor at a healthy location reports a healthy bearing even with a
faulted bearing on the same shaft. **That assumption is directly testable with our gate** — see
block **B6** in §6. This is the cheapest genuinely novel experiment in the programme: CPU-only, no
training, and it either validates or improves a 2026 MSSP protocol.

### C29 — Claim reordering `[DECISION — blocking, needs researcher sign-off]`

The leakage-safe-evaluation space is now crowded: Hendriks et al. (MSSP 2022), Abburi et al.
(PHM 2023), Matania et al. (PHM Europe 2024), Wheat et al. (IEEE Access 2024), Vieira et al.
(MSSP 2026), and a further PHM Europe 2026 entry. Claim 1 as worded is dead.

**But claim 1 is not taken.** Vieira explicitly scope themselves out: their work *"focuses on a
simpler yet fundamentally critical problem: training and testing within a single testbench,"* and
they name inter-testbench / cross-domain work as the alternative they are **not** doing. Nobody has
done leakage-safe evaluation of SFDA.

| # | Claim | Wording discipline |
|---|---|---|
| **1** | The physics screen as a **record-level, FAR-controlled pseudo-label gate for SFDA** — exact family-sum null, BH multiplicity control across records, realised-vs-nominal FAR reported on real data. | Claim the **gate**, never the **test** (C30). |
| **2** | External validation against Smith & Randall's per-record diagnosability categories, **under domain shift**. | Differentiate from `predictive-maintenance-mcp`: ours is under shift and statistical, theirs is in-domain and rule-based. |
| **3** | **The first leakage-safe evaluation of SFDA for bearing diagnosis** — Vieira's bearing-wise methodology applied to the cross-machine source-free setting, measuring how much published SFDA gain survives. | Vieira is the **methodology source**, cited as such, not a footnote. |

### C30 — Claim 1 narrowed: CFAR on the SES is prior art `[VERIFIED — corrects an earlier note]`

CFAR thresholding of the squared envelope spectrum already exists in condition monitoring (adaptive
Autogram with a CFAR detector on the square-envelope spectrum for incipient cavitation; CFAR-derived
condition indicators in US Army helicopter HUMS). Borghesani and Antoni already give statistical CS2
thresholds. We claim the **use as a record-level pseudo-label gate inside SFDA**, sharing harmonic
coordinates with the network input, with BH control of expected false accepts. Not the detector.
Add a TAKEN row to §2.1.

### C31 — H4 risk Med → **High**, on published evidence `[VERIFIED]`

Jeong et al. (*Sensors* 2025, 25(14):4383) — our own F1 ≈ 0.47 anchor — has order-frequency
preprocessing as its first stated contribution. Their ablation, target domain:

| configuration | target F1 |
|---|---|
| baseline | 0.23 |
| **+ order-spectrum preprocessing** | **0.46** |
| + reconstruction | 0.46 |
| + test-time training (full) | 0.50 |

Order normalisation carries 0.23 → 0.46; everything learned adds 0.04. That is exactly the H4 failure
mode, already published, in the nearest analogue. **L3 runs before any KNEOS-HC code is written.**

### C32 — KNEOS-HC has a closer neighbour than the ledger admits `[VERIFIED]`

Matania, Cohen, Bechhoefer & Bortman, *MSSP* 224:112117 (2025), "Zero-fault-shot learning for bearing
spall type classification by hybrid approach": combines physics-based algorithms with ML and
**projects the signals into an invariant feature space by physics-based algorithms**, then classifies
with a fully connected network. Six datasets, ≥ 98 % accuracy, code public. In MSSP, one of our
target venues, from a group that also owns a leakage paper.

This is the nearest published neighbour to KNEOS-HC's core argument and is **absent from
`ADDENDUM_A.md` §A1 and `PLAN.md` §2.1**. Add it, state the delta explicitly, and cite both Matania
papers. Our delta: their invariant space serves a zero-shot classifier trained on simulation; ours
serves **both** the network input **and** the null of a calibrated test on the same axis, source-free,
with no simulator.

### C33 — The gate null was calibrated without DRS in the loop `[GAP — blocks any real-data gate result]`

C24 calibrated CA-CFAR on synthetic white and AR(2) backgrounds, but C11 makes cepstrum pre-whitening
mandatory step 1.5, and Borghesani et al. note cepstral pre-whitening removes spectral-energy
fluctuation along the frequency axis — it changes the SES background statistics. A null calibrated
before step 1.5 is not the null the gate faces.

Re-run `test_gate_null.py` with DRS applied to the synthetic backgrounds, same grid
(N ∈ {20,45,95}, α ∈ {0.10,0.05,0.01}, both backgrounds). If realised FAR moves outside ~2 SE of
nominal, re-fix reference/guard bandwidth **on synthetic noise** and log it as a C23-style
pre-registration. Session 6 blocker.

### C34 — Introduction anchor replaced `[DECISION]`

"Physical priors are rarely studied" is an accurate quote from a 2019 preprint (IEEE TIM 2021). In
2026 the field contains PIUDA, PCTL, Bio-SFDA, pyDSN, Matania 2025, Jeong 2025, the *Sci. Rep.* 2026
physics-guided framework, and the *EiN* 2026 order-analysis framework. The claim is stale and a
reviewer kills it in one line. New anchor:

> **Physics priors in cross-machine diagnosis are now common. Calibrated ones are not.** Every
> published physics screen we could find sets a threshold or a rule; none reports a false-alarm rate
> against a stated null, and none reports its own spectral-resolution requirement.

That framing is defensible, current, and is what our two pre-experimental findings actually support.

### C35 — **UORED-VAFCLS added to the dataset roster** `[VERIFIED — the largest single improvement available]`

University of Ottawa Rolling-element Dataset (Sehri, Dumond & Bouchard, *Data in Brief* 49:109327,
2023; Mendeley `y2px5tg92h`). **NSK 6203 and FAFNIR 203KD**, 42 kHz, 10 s per record, ~1750 rpm
constant, constant load, 20 physical bearings — **five per fault type across inner, outer, ball and
cage** — each with three states (healthy, developing, faulty), 60 records total.

Why this matters more than anything else in this document:

1. **The 6203 geometry is already verified in our repo.** The gate runs on day one; no new blocker.
2. **It is a second, independent 6203 rig.** Orders are speed-free, so the shaft-harmonic lock is
   *identical* to PU: BPFO sits +1.77 % from 3·f_r on both. Our headline finding stops being a
   PU quirk and becomes **replicated across two rigs at different speeds**. H6/H7 gain a second
   test bed for free.
3. **It has a cage class.** C22 demoted FTF to a context channel because no dataset had a cage class.
   UORED does. See C36.
4. **Five physical bearings per fault class** — the only dataset in our roster where a bearing-wise
   split has real statistics.
5. **Spectrally it is the easiest condition we have.** At `T_A` = 3.0 s: Δf = 0.333 Hz,
   BPFO–3·f_r separation **4.65 bins**, **87.5 revolutions** per window, pooled family N ≈ 80. PU N09
   remains the worst case at 2.39 bins; UORED is comfortable.
6. **Vieira et al. use it**, so our numbers sit directly alongside the reference protocol.

**The honest limitation, and it determines the role:** 60 records total. At `T_A` = 3.0 s / 50 %
overlap that is 5 windows/record and only ~50 windows per fault class, ~30 after a 60 % train split.

| class | bearings | records | windows | ~60 % train |
|---|---|---|---|---|
| healthy | 20 | 20 | 100 | 60 |
| inner / outer / ball / cage | 5 each | 10 each | 50 each | 30 each |

**So UORED is a target and gate-evaluation dataset, never a source.** It has one speed and one load,
so it carries no within-dataset condition shift either. Do not attempt to train on it.

### C36 — Label space `L4c` added; FTF is a decision family on UORED only `[FROZEN — new]`

`L4c = L3 + {Ball, Cage}` = {Normal, Inner, Outer, Ball, Cage}, **UORED only**. On `L4c` the deciding
families are `{BPFO, BPFI, BPFB, FTF}` and `N_MIN` applies to FTF. Everywhere else C22 stands
unchanged: no cage class exists, so FTF carries no verdict and `N_MIN` must not apply to it.

FTF is intrinsically bin-poor (`FTF = BPFO/n` exactly, so the slip window is n× narrower). At UORED's
1750 rpm and `T_A` = 3.0 s this must be certified by `feasibility.py` before any `L4c` gate result —
**assume it fails until the arithmetic says otherwise**, and if it fails, report that as a finding:
*the cage family is below the resolution floor at every window length a 10 s record permits.*

### C36b — Two splitting traps, both named by the reference protocol `[VERIFIED]`

- **UORED must be split by `bearing_id`, never by severity.** Vieira explicitly classify a split on
  fault severity level — *"as in the UORED-VAFCLS dataset, where two distinct severity levels are
  provided for each bearing"* — as **bearing-level leakage**, because Inner-1 and Inner-2 come from
  the same physical bearing. Our 3:2 bearing split is correct; a severity split would look reasonable
  and be wrong. Encode it as an assertion, not a convention.
- **Bearing-wise is necessary, not sufficient.** A recent motor-current study makes the point that a
  bearing-wise split can still evaluate only within operating regimes seen during training. Our B1
  (PU A1↔A2↔A3) is condition-disjoint by construction, so we are covered — but the manuscript must
  state that the two leakage axes are independent, or a reviewer will assume we conflated them.

### C37 — New block B6: gate-based audit of a published split `[NEW]`

Two CPU-only experiments, no training, both falsifiable, both publishable alone:

- **B6a — CWRU cross-end contamination (tests C28).** Gate the CWRU fan-end healthy signals drawn
  from *faulted* configurations at level α. Vieira's split assumes they are healthy. If the realised
  acceptance rate on the drive-end fault family significantly exceeds α, cross-end contamination is
  measurable and their split — the current best practice — leaks. Report either way.
- **B6b — UORED cage as an out-of-label-space specificity test.** An `L3`/`L4` model has no cage
  class. Run the gate on UORED cage records: it should **reject** every O/I/B family. Rejection rate
  is a direct, training-free measurement of gate specificity on a fault the classifier cannot
  represent. If channel `C` carries the evidence instead, that is a bonus result for C36.

B6 is the highest value-per-GPU-hour work in the programme: zero GPU hours.

### C38 — Ladder input-dimension discipline `[NEW]`

At `T_A` = 3.0 s / 64 kHz an L0 window is **192 000 raw samples**; an L5 KNEOS-HC tensor is
(5, K=5, 2J+1=5, M=9) = **1 125 values**. `resnet18_1d` from `ZhaoZhibin/UDTL` is used in that
literature at ~1024–2048 samples. With a few hundred windows per class, **L0 is not a floor, it is a
strawman**, and H1 inherits the defect. Emit `results/feasibility/ladder_input_dims.csv` (input
shape, parameters, receptive field, windows/class per rung) and resolve by researcher decision:
(a) fix `T_A` and declare L0's disadvantage; (b) give L0/L1 the Track R 2048 window and forbid
cross-track claims per C17; or (c) decimate L0 and declare it. Logged before any ladder result exists.

### C39 — JNU structural finding strengthened `[VERIFY on the files]`

C25 says each class is one physical bearing. Li et al. actually assign *normal, outer and roller* to
the N205 and *inner* to the NU205 — two bearing **types**, not four bearings. If the files confirm,
C25's justification upgrades from "one bearing per class" to "three classes share one bearing type,"
which is a stronger structural result. JNU remains Track R only either way.

### C40 — HUST geometry blocker softened `[VERIFIED]`

HUST includes **6205**, whose geometry we already hold. Manufacturer vibration-frequency tables
(NTN and equivalents) publish ball count, ball diameter and pitch diameter for 62-series bearings,
and C13 already specifies how to validate them: assert against the closed-form formula, record the
source's convention, never trust the frequency table. One additional resolved model makes a
held-out-model test possible. The BMC paper does not state a manufacturer, so any catalogue value
enters as `verified: false` until the formula reproduces a published multiplier. **UORED's FAFNIR
203KD needs the same treatment** and becomes human open item 9.

### C41 — Preprint scope changed `[DECISION — the date does not move]`

`DECISIONS.md` sets a hard preprint at **2026-10-18**, scoped as "whatever M1 says." Under C29, M1
(the leakage delta) is no longer the lead claim, and M2/A7 — which would support the new claim 1 —
cannot land by 18 October. Reframe rather than reschedule:

> **Preprint = a methods and calibration note.** The 6203 shaft-harmonic lock replicated on two rigs
> (§0.2 + C35); the spectral-resolution feasibility analysis (§0.3); the null-only CFAR calibration
> table already sitting in `results/calibration/`; the leakage-safe SFDA evaluation protocol; and the
> pre-registered hypotheses with their decision rules. **No gate results, no accuracy tables.**

Everything in it already exists or is CPU-only. It stakes the gate design and both findings without a
single GPU hour, and it is the strongest hedge available against a crowded field. The date holds.

---

## 3. Revised claims — `PROTOCOL.md` §1 replacement

See C29. Three claims, reordered. Plus a standing wording rule:

> No novelty claim appears in any repo file or manuscript sentence without (a) a named nearest
> published neighbour and (b) a one-sentence delta. Absence of a neighbour means the search was not
> hard enough. This is a halt condition, not a style note.

---

## 4. Revised prior-art ledger — replaces `PLAN.md` §2.1

| Idea | Status | Reference |
|---|---|---|
| Bearing-wise / leakage-safe evaluation | **TAKEN** | Hendriks MSSP 169:108732 (2022); Abburi PHM (2023); Matania PHME 8(1):13 (2024); Wheat *IEEE Access* 12:169879 (2024); **Vieira MSSP 258:114640 (2026)** |
| Multi-label CWRU benchmark + S&R error analysis | **TAKEN** | Rosa, Braga & Silva, arXiv 2407.14625 |
| Cross-domain fault-diagnosis benchmark in RESS | **TAKEN** | Zhao, Zio & Shen, *RESS* 245:109964 (2024) |
| Order normalisation inside SFDA | **TAKEN** | Jeong et al., *Sensors* 25(14):4383 (2025) — and it is their dominant ablation term |
| Physics-based projection to an invariant feature space | **TAKEN** | **Matania et al., *MSSP* 224:112117 (2025)** |
| Source-free **and** cross-machine | **TAKEN** | He B. et al., *EAAI* 166:113585 (2026) |
| Physics-guided pseudo-label gating in SFDA | **TAKEN** | Bio-SFDA (EAGLE), *Results in Eng.* 30:111105 (2026) |
| Rule-based physics validator supervising confidence | **TAKEN** | PCTL, *EiN* 28(2):211797 (2026) |
| Physics-informed cross-machine UDA | **TAKEN** | PIUDA, *AEI* 62:102774 (2024) |
| Physics priors + order analysis + pseudo-label self-training | **TAKEN** | *EiN* 2026 physics-informed cross-domain; *Sci. Rep.* 2026 physics-guided hierarchical |
| **CFAR / statistical thresholds on the SES** | **TAKEN** | Borghesani MSSP 40:38–55 (2013); Antoni; Autogram+CFAR cavitation; Army HUMS CFAR indicators |
| Sub-bands centred on fault frequencies | **TAKEN** | Sadoughi & Hu; SFRF (arXiv 2506.12375) |
| Cepstrum pre-whitening / DRS | **TAKEN — standard** | Randall & Antoni MSSP 25(2) 2011; S&R 2015 Method 2 |
| Envelope spectrum as cross-device alignment | **TAKEN** | conditional kernel Bures metric learning, PMC11085194 |
| Diagnosability stratification of a CWRU benchmark | **PARTLY TAKEN** | `predictive-maintenance-mcp` + *Appl. Sci.* 16(6):2812 (2026) |
| **Leakage-safe evaluation of SFDA specifically** | **NOT FOUND** | Vieira explicitly excludes it |
| **A FAR-controlled statistical test used as a record-level pseudo-label gate in SFDA, on coordinates shared with the network input, with BH control across records** | **NOT FOUND** | — |
| **Diagnosability-stratified gate precision/recall under domain shift** | **NOT FOUND** | — |

Three unoccupied rows. That is the paper.

---

## 5. Revised dataset roster

| Dataset | Bearing | fs | Record | Role | Gate? |
|---|---|---|---|---|---|
| CWRU DE | 6205 | 12 kHz | ~10 s | Source; Smith & Randall stratification | yes |
| CWRU FE | 6203 | 12 kHz | ~10 s | B6a only | yes |
| PU | 6203 | 64 kHz | 4 s | **Headline source and target**; artificial→real | yes |
| **UORED-VAFCLS** | **6203 / 203KD** | **42 kHz** | **10 s** | **Target + gate evaluation only, never a source (C35)** | **yes (6203); 203KD pending)** |
| HUST | 6204–6208 | 51.2 kHz | 10 s | Cross-machine target; B4 blocked on geometry | 6205 only |
| JNU | N205/NU205 | 50 kHz | 20 s | **Track R only** (C25, C39) | **no — raises** |

---

## 6. Revised benchmark suite — replaces `PLAN.md` §3.3

| Block | Tasks | Track | Split | Space | GPU |
|---|---|---|---|---|---|
| **B0** reproduction | PU A1↔A2↔A3 (6), JNU B1↔B2↔B3 (6) | R | as published (leaky) | 8-class / 4-class | yes |
| **B1** leakage delta | same 12 | R | bearing-wise | L3 / L4 | yes |
| **B2** cross-machine | CWRU↔PU, CWRU↔HUST, PU↔HUST, **CWRU→UORED, PU→UORED** | A | bearing-wise | L3 | yes |
| **B3** fidelity | PU-artificial → PU-real | A | bearing-wise by construction | L3 | yes |
| **B4** geometry | HUST held-out models | A | bearing-wise | L4 | **blocked** |
| **B5** stress | compound / out-of-label-space | A | bearing-wise | — | yes |
| **B6a** split audit | CWRU cross-end healthy contamination (C28/C37) | A | n/a | n/a | **none** |
| **B6b** specificity | UORED cage vs L3/L4 gate (C37) | A | n/a | L4c | **none** |
| **B7** lock replication | 6203 lock + DRS on **PU and UORED** (C35) | A | n/a | n/a | **none** |

Methods: `source-only`, `SHOT`, `SDALR`, one prototype/clustering SFDA, `confidence-threshold`,
`PCV-style rule`, `EAGLE-style rule` (our reimplementations, H7), `gated (ours)`,
`oracle (SHOT-clean)`. Seeds `[0,1,2,3,4]`, fixed, never reselected.

**Note B6 and B7 cost zero GPU hours and can run during any quota exhaustion.** Schedule them there.

---

## 7. Revised hypotheses — replaces `PLAN.md` §2.6

| | Hypothesis | Decision rule | Change |
|---|---|---|---|
| **H1** | Zero-shot: source-only CWRU→PU, KNEOS-HC > plain SES > raw 1D | Fails ⇒ drop the architecture claim, do not defend it | **Subject to C38** — not valid until the input-dimension audit is resolved |
| **H2** | Geometry generalisation on HUST held-out models | Blocked | **Partially unblocked** by C40 (6205 known, one more needed) |
| **H3** | Gate acceptance ↔ classifier confidence associate more strongly under KNEOS-HC | Reported either way | unchanged |
| **H4** | KNEOS-HC beats angular resampling alone (L3) | Fails ⇒ say so in the abstract | **Risk High (C31). Runs first, before KNEOS-HC exists.** |
| **H5** | `J = 2` beats `J = 0` | Fails ⇒ drop sidebands | unchanged |
| **H6** | Without step 1.5, PU outer-race gate precision is at chance; with it, materially above | Fails ⇒ negative finding, lead with it | **Now replicated on UORED (C35)** |
| **H7** | Frequency-position rule at chance for the outer race where the CS2-order test is not | The sharpest prediction in the paper | **Two rigs, not one** |
| **H8** | **NEW.** The gate rejects O/I/B families on UORED cage records at a rate materially above its rejection rate on true O/I/B records | Fails ⇒ gate specificity is weak out-of-label-space; report it | zero GPU cost |

---

## 8. Revised ablation ladder

Unchanged in content (L0–L8, FiLM cut, no attention / Transformers / KANs), with two additions:

- **L3 runs first.** Per C31, angular resampling alone is evaluated before KNEOS-HC is implemented.
  If L4/L5 do not beat L3, the architecture claim dies there, cheaply, on cached CPU features.
- **Every rung carries its input shape in the ledger** (C38). A rung comparison without matched or
  declared input dimensionality is not reported.

---

## 9. Revised metrics — amends `PROTOCOL.md` §5

`[FROZEN]` metrics unchanged. Two additions, both secondary, neither replacing a frozen metric:

1. **Macro-AUROC under a multi-label reading**, reported alongside macro-F1 for B1 and B2.
   Rationale: Vieira's formulation is prevalence-independent and threshold-free, which is the natural
   partner to a FAR-controlled gate, and it makes our tables directly comparable to the reference
   protocol. Secondary table, not the headline; the frozen headline stays oracle-gap closure.
2. **Realised FAR on real healthy records**, per dataset, per α. C24 calibrated on synthetic noise.
   The number that matters to a reviewer is what the gate does on a real record with no fault.

Reliability scorecard gains two columns:
`… | Gate-P@Y1Y2 | Gate-R@N1N2 | FAR_real | AUROC_clean | Sig`

---

## 10. Revised risk register — replaces `PLAN.md` §8

| Risk | P | Mitigation | Trigger |
|---|---|---|---|
| **H4 fails — all gain is order tracking** | **High (was Med)** | L3 first, CPU-cached, before KNEOS-HC exists | Say so in the abstract |
| Gate redundant with confidence filtering | High | A7 at S7; pseudo-labels dumped at S4 | Jaccard > 0.85 ⇒ pivot |
| **Track A sample counts too small** | **Open (was struck)** | S2.0 sweep; UORED as target not source | `est_train_windows_per_class < 250` ⇒ halt |
| **Null invalid after DRS** | **Med-high (new)** | C33 recalibration before any real gate | Realised FAR > 2 SE from nominal |
| H1 fails — no zero-shot gain | Med-high | S6b before gate code | Drop architecture claim; keep gate + protocol |
| **Ladder comparison invalid on input dimensionality** | **Med (new)** | C38 audit in S2 | Resolve before any ladder result |
| H6 fails — DRS does not rescue the 6203 | Med | S6c CPU-only, **two rigs** | Negative finding, lead with it |
| Bio-SFDA leakage-safe / PU-artificial-only / 2048-window | Med | Session 0 gate | Re-scope before coding |
| HUST / JNU / 203KD geometry unresolved | Med | All `[BLOCKED]`, raise not return | Drop B4 and H2; L3-only cross-machine |
| **Scooped on the protocol claim** | **Realised** | C29 reordering; C41 preprint reframe | Already happened — act, don't mitigate |
| Real spalls degrade the gate | Expected | Pre-registered fidelity axis | Finding, not weakness |
| Ball/roller class fails | Expected | Pre-registered prediction | Per-class reporting |
| **Cage family below resolution floor** | **Med (new)** | C36 certification | Report as a finding |
| Compute overrun | Low | `budget.py`; B6/B7 cost zero GPU | Defer B5, name it |

---

## 11. Revised compute budget

| Block | Runs | GPU-h | Change |
|---|---|---|---|
| M0 reproduction (Track R) | 36 | ~4 | — |
| **L3-first / H4 early** | 30 | ~2 | **new, pulled forward** |
| H1 zero-shot | 50 | ~2 | — |
| **B6 + B7 + H8** | 0 | **0** | **new, CPU** |
| M1 leakage delta | 60 | ~6 | — |
| M2/A7 + M3 | 90 | ~7 | — |
| Ladder (10 rungs × 3 tasks × 5 seeds) | 150 | ~12 | — |
| Full matrix B2/B3 (9 methods × ~10 tasks × 5 seeds) | 450 | ~34 | **+6 h for UORED targets** |
| **Total** | ~866 | **~67 GPU-h** | ≈ 2.5 weeks of quota; budget 4–5 weeks with reruns |

Still inside 30 GPU-h/week. The UORED additions are targets only, so they add inference and short
adaptation runs, not source training.

---

## 12. Session plan S2 → S12

Each session ends when its gate evaluates PASS **and** every number traces to a ledger row with a
retained artifact. FAIL writes `results/FAILURE_<id>.md` and stops for a human decision.

### S2 — Data layer *(current)*

- **S2.0 `[BLOCKING]`** Extend `feasibility.py` to certify the **window contract**, not just spectral
  separation. Per (dataset, bearing, condition) emit: `record_length_s, T_A, overlap_frac,
  windows_per_record, windows_per_class, est_train_windows_per_class, delta_f_hz, bpfo_hz,
  sep_from_nearest_shaft_harmonic_bins, pooled_family_bins_N, revolutions_per_window,
  raw_input_samples_per_window`. Assert: separation ≥ 2.0 bins, family N ≥ 20, revolutions ≥ 5,
  windows/record ≥ 1, **`est_train_windows_per_class` ≥ 250**. Emit
  `results/feasibility/T_A_sweep.csv` over `T_A ∈ {2.0,2.5,3.0,3.5,4.0}` × `overlap ∈ {0,0.5,0.667,0.75}`.
  **Do not choose `T_A` autonomously** — C21 derived it from resolution alone, without the
  sample-count constraint, so the derivation is incomplete. Researcher decides; `DECISIONS.md`
  records windows and separation before and after.
- **S2.1** Loaders: CWRU DE, PU, **UORED**. `bearing_id` and `record_id` are first-class fields, not
  derived later. CWRU: per-file RPM asserted in 1700–1800, plus `sensor_location ∈ {DE,FE}` and
  `config_type ∈ {healthy_healthy, faulted}` so the C28/Vieira split and B6a are constructible in S3
  without reloading. UORED: `bearing_id ∈ 1…20`, `health_state ∈ {healthy, developing, faulty}`,
  `manufacturer ∈ {NSK, FAFNIR}`, vibration channel only. **No JNU in Track A.**
- **S2.2** Per-record manifests: `record_id, dataset, bearing_id, bearing_model, manufacturer,
  class_L3, class_L4, class_L4c, operating_condition, rpm, rpm_source ∈ {measured,nominal,unknown},
  fs_hz, duration_s, n_windows, sha256, licence, redistribution`. H4's confound is declared from
  `rpm_source`, not from prose.
- **S2.3** Ladder input-dimension audit (C38) → `results/feasibility/ladder_input_dims.csv` + decision.
- **S2.4** Literature reconciliation, **no code**: `notes/vieira_2026.md` (incl. a section
  "What we adopt, what we differ on, and why" — this is our §Evaluation Protocol text, written before
  M1 runs), `notes/jeong_2025.md` (the ablation table verbatim), `notes/matania_2025.md` (the
  invariant-feature-space delta), `notes/uored.md`, and `notes/POSITIONING.md` rewritten to C29.
- **S2.5** Private versioned Kaggle datasets, checksummed, after S2.0 passes and manifests validate.

**Gate:** S2.0 certifies; manifests validate; five notes exist; `pytest -q` green < 60 s CPU.

### S3 — Splits

`splits.yaml` + a load-time assertion that hard-fails on any `bearing_id` on both sides, itself
tested with a deliberately leaky config. **Implement Vieira's CWRU healthy construction (C28) as a
named, selectable split**, alongside our conservative one; report both. UORED splits are 3:2 by
bearing per fault type, matching Vieira so numbers are comparable.

**Gate:** the leaky config fails the assertion; both CWRU healthy constructions produce valid splits.

### S4 — M0: reproduce SDALR

As published, Track R, leaky splits. Halt if any published number is missed by > 2 pp.
**Pull forward:** dump pseudo-labels and confidence scores to disk at the end, so S7's Jaccard needs
no retraining.

### S5 — M1: leakage delta

PU relabelled to L3, bearing-wise. Two numbers, one delta, per method. The delta is a result either
way. **Framed under C29 as claim 3, not claim 1.**

### S6 — Representation and the early kills *(reordered)*

- **S6a** `band_select.py` → `ses.py`; precompute and cache SES per dataset on CPU.
- **S6b `[NEW ORDER]`** **L3 alone** — angular resampling, no kinematic warping. H4's null, run
  before KNEOS-HC exists (C31).
- **S6c** H1 zero-shot, subject to the C38 resolution.
- **S6d** **C33 null recalibration with DRS in the loop. Blocks every later gate result.**
- **S6e** B7: the 6203 lock and DRS on **PU and UORED**, CPU-only. Figure (i) of the paper.

**Gate:** if L5 does not beat L3 at S6b, the architecture claim is dropped here and the programme
continues as gate + protocol. This is a feature.

### S7 — M2 / A7: the gate, and the redundancy test

Gate implementation; A7 Jaccard vs confidence filtering at **record** level (C17), confidence
aggregated by mean and majority, both reported, with power. **Near-total overlap ⇒ pivot to the
protocol-and-stratification paper**, now carrying both findings plus B6/B7.

### S8 — M3: oracle-gap closure

Ungated / gated / oracle on 3 tasks. Small gap ⇒ reframe: pseudo-label noise was not the bottleneck.

### S9 — M4: diagnosability stratification + B6

Smith & Randall strata (human transcription required — check `predictive-maintenance-mcp` first).
**Run B6a and B6b here; they need no GPU and no training.**

### S10 — M5: PU-artificial → PU-real, plus CWRU→UORED and PU→UORED

The fidelity hypothesis, plus the second 6203 rig as a cross-machine target.

### S11–S12 — M6: full matrix

5 seeds, Wilcoxon signed-rank pairwise, Friedman + Nemenyi across methods, t-SNE last and small.
Reliability scorecard assembled. Reproducibility package frozen.

---

## 13. Revised calendar

| Milestone | Date | Change |
|---|---|---|
| Session 2 | 2026-09-20 | — |
| M0 + M1 (S3–S5) | 2026-10-04 | — |
| **Preprint — methods and calibration note (C41)** | **2026-10-18** | **scope changed, date unmoved** |
| S6 incl. L3-first and C33 recalibration | 2026-11-01 | — |
| M2–M5 (S7–S10) | 2026-11-15 | slipped 2 weeks |
| Full matrix (S11–S12) | 2026-11-29 | slipped 1 week |
| **Target submission** | **December 2026** (RESS primary) | held |

**Venue, verified 2026-09-13.** RESS carries a 2026 impact factor of **13.7** (released June 2026 on
2025 data, up 24.6 % from 11.0), and is Q1 in Engineering–Industrial at 7/69 and in Operations
Research & Management Science at 4/106. Its scope explicitly lists *methods and applications of
automatic fault detection and diagnosis*. So the answer to "is this Q1-worth" is yes on the venue
side — but note the bar moved: a 25 % IF jump in one year means more submissions and a more selective
desk.

**Two calendar consequences.** Median time to accept is ~5 months and to publish ~6, with 21 % of
papers over 9 months. A December 2026 submission therefore lands in print around mid-2027. That makes
the C41 preprint the *primary* instrument for staking the claim, not a courtesy — treat it as a
deliverable with the same evidence standards as the paper. It also means a desk reject costs a full
quarter, so the secondary venue (MSSP) should be format-ready in parallel, not chosen after a
rejection.

The slip is absorbed by B6/B7 costing zero GPU hours and by S6b killing the architecture branch early
if it is going to die.

---

## 14. Revised paper assembly

**Framing (C34).** Physics priors are common; calibrated ones are not. RESS vocabulary throughout:
false-alarm rate, screening, deployment validity, trustworthiness of automated diagnosis when the
monitored machine is not the one you trained on.

1. **Introduction** — the calibration gap; the three claims in C29 order.
2. **Related work** — Vieira, Hendriks, Matania (×2), Jeong, Bio-SFDA, PCTL, PIUDA, SDALR, He,
   Zhao/Zio/Shen, `predictive-maintenance-mcp`. Each with an explicit stated delta. Do not hope a
   reviewer misses any of them.
3. **Method** — kinematics; **the 6203 lock replicated on two rigs**; **the resolution feasibility
   analysis**; DRS; harmonic coordinates with the non-monotonicity proof; the CA-CFAR family-sum test
   at level α with its null-only calibration table; the closed-form slip model; multiplicity.
4. **Evaluation protocol** — a contribution, so give it the space of one. Vieira credited as the
   methodology source; our delta is SFDA + cross-machine + stratification + B6.
5. **Results** — scorecard; ladder with input dimensions declared; oracle-gap closure; H6/H7 on two
   rigs; H8; B6a and B6b; noise transition matrices; per-class with ball/roller/cage separate;
   stratified gate precision/recall; leaky-vs-clean delta; realised vs nominal FAR on real records.
6. **Discussion** — where the gate fails and why; artificial-vs-real fidelity; §2.8 limitations.
7. **Conclusion** — no overclaiming. If the gate closed 40 % of the oracle gap, say 40 %.

**Figures that earn their place.** (i) the 6203 lock, PU **and** UORED, before and after DRS;
(ii) bins-per-slip-window vs window length, 2048 marked, feasible region shaded; (iii) realised vs
nominal FAR, synthetic and real; (iv) CWRU and PU fault lines on shared harmonic coordinates;
(v) leaky-vs-clean delta table; (vi) gate precision/recall by Smith & Randall stratum;
(vii) ablation ladder, grouped bars with error bars; (viii) t-SNE, last and small.

---

## 15. Human open items — revised

| # | Item | Blocks | Status |
|---|---|---|---|
| 1 | Transcribe `smith_randall_cwru.csv`, per-method columns, no collapsing | S9 | open |
| 2 | JNU roller count `Z` | JNU kinematics | open; JNU is Track R only regardless |
| 3 | HUST 6204/6206/6207/6208 geometry | H2, B4 | **softened** (C40) |
| 4 | HUST per-load shaft RPM | HUST tasks | open |
| 5 | **Sign off `T_A` and overlap after the S2.0 sweep** | all Track A | **NEW, blocking** |
| 6 | **Sign off the C29 claim reordering** | Introduction, abstract | **NEW, blocking** |
| 7 | Bio-SFDA full text | H7 | demoted below Vieira |
| 8 | Dataset licences incl. **UORED** | S2.5 | open |
| 9 | **FAFNIR 203KD geometry** (`n`, `Bd`, `Pd`) | UORED gate on non-NSK bearings | **NEW** |
| 10 | **Sign off the C41 preprint reframe** | 2026-10-18 | **NEW, blocking** |
| 11 | Sign off §4 constants | every gate result | open |

---

## 16. Standing rules added this revision

Append to `PLAN.md` §6 halt conditions:

- `feasibility.py` cannot certify a (dataset, condition, `T_A`, overlap) tuple → halt.
- `est_train_windows_per_class < 250` on any Track A training class → halt, surface as a decision.
- A window lacks `bearing_id` or `record_id` → hard fail.
- A novelty claim exists anywhere without a named nearest neighbour and a stated delta → halt.
- A ladder rung is compared to another without both input dimensionalities in the ledger → halt.
- A real-data gate result is produced before C33 recalibration passes → halt.

And one behavioural rule, because this is the failure mode the existing apparatus did not catch:

> The plan's integrity machinery is working — it caught four of its own errors before this audit and
> its arithmetic survived independent reproduction. What it did not catch is **positioning drift**:
> the literature moved between the freeze and now, and the plan had no mechanism to notice. Add one.
> Re-run the prior-art sweep at the start of every third session and log the date. A frozen protocol
> is not a frozen field.

Reporting that our method loses remains authorised and expected.
