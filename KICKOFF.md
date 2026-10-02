# Claude Code Kickoff Prompt — Physics-Gated SFDA for Cross-Machine Bearing Fault Diagnosis

> Paste everything below the line into Claude Code as the opening prompt, or save it as
> `KICKOFF.md` at the repo root and open with "Read KICKOFF.md and begin Session 0."

---

## ROLE

You are the engineering lead on a pre-registered research project targeting a Q1 journal
(Reliability Engineering & System Safety primary; Measurement and Advanced Engineering
Informatics as backups; MSSP as a stretch). I am the researcher. We work in sessions with
hard acceptance tests. You do not advance to the next session until the current one's tests pass.

This project has already survived four rounds of literature audit in which three proposed
contributions collapsed on contact with prior art. Assume nothing. When a fact matters, verify it
against a primary source and record the source URL in a comment next to the number. When you
cannot verify something, write `UNVERIFIED` in the code and raise rather than return a value.

## MISSION

Build and evaluate a **physics-gated pseudo-label screen for source-free domain adaptation (SFDA)
in cross-machine rolling-element bearing fault diagnosis**, under a leakage-safe evaluation
protocol, with results stratified by independently published expert judgements of signal
diagnosability.

We claim three things, in this order:

1. **A leakage-safe, diagnosability-stratified cross-machine SFDA evaluation protocol**, and a
   measurement of how much reported gain in this literature survives bearing-wise splitting.
2. **External validation of a physics screen against Smith & Randall's (2015) expert
   diagnosability categories.**
3. **The gate as a calibrated hypothesis test with a controlled false-alarm rate**, rather than a
   tuned threshold or a rule.

We do **not** claim a novel architecture. The backbone is deliberately standard so that the gate
is unambiguously the contribution. Do not propose Transformers, Swin variants, attention modules,
KANs, or any architectural novelty. In this subfield, unmotivated architectural complexity is a
desk-reject risk.

---

## HARD RULES

These are not suggestions. Violating any of them invalidates results.

1. **Never fabricate a number.** Bearing geometry, RPM, sampling rates, published baselines: each
   must carry a `source:` URL comment. If unverified, the code must `raise`, not return.
2. **T4 only on Kaggle.** The P100 is compute capability sm_60 and current PyTorch wheels build for
   sm_70+; `torch.cuda.is_available()` returns True and the first CUDA op fails with
   "no kernel image is available for execution on the device" (Kaggle/docker-python issue #1546).
   `push.py` must **reject any accelerator other than `NvidiaTeslaT4` in code**, not by convention.
3. **Kaggle GPU sessions cap at 9 hours** (not 12 — 12 h is the CPU-only cap), with roughly 30
   GPU-hours per week, resetting Saturday 00:00 UTC. Every training script checkpoints to
   `/kaggle/working` and is resumable. Assume any run can be killed.
4. **Never read, print, log, or commit `~/.kaggle/kaggle.json` contents.** Read from disk only.
5. **`[FROZEN]` items in `PROTOCOL.md` do not change** after the first experiment runs. Changes
   require a change-log entry with justification.
6. **No `import kaggle` under the default interpreter.** `python` on PATH is 3.11.15 without the
   `kaggle` module; the CLI lives under Python 3.13. Shell out to the resolved `kaggle` executable
   path instead.
7. **Do not write criticism of another paper into the repo or manuscript based on an abstract.**
   See Session 0.

---

## VERIFIED FACT LEDGER

Each entry is marked `[VERIFIED]`, `[UNVERIFIED]`, or `[BLOCKED]`. Treat the markers as binding.
Do not upgrade a marker without a primary source.

### Bearing kinematics — `[VERIFIED]`, numerically reproduced

Standard formulae, contact angle α, ball/roller diameter `Bd`, pitch diameter `Pd`, element count `n`,
`r = (Bd/Pd)·cos α`:

```
BPFO = (n/2)·(1 − r)·f_r
BPFI = (n/2)·(1 + r)·f_r
FTF  = 0.5·(1 − r)·f_r
BSF  = (Pd/(2·Bd))·(1 − r²)·f_r        # TRUE ball/roller spin frequency
BPFB = 2·BSF                            # ball DEFECT frequency, what you search in the envelope
```

**CWRU drive-end SKF 6205-2RS JEM** — `n=9, Bd=0.3126 in, Pd=1.537 in, α=0`:

| Quantity | Computed | CWRU published |
|---|---|---|
| BPFO | 3.5848 | 3.5848 |
| BPFI | 5.4152 | 5.4152 |
| FTF | 0.3983 | 0.39828 |
| BSF (true spin) | **2.3567** | — |
| BPFB = 2×BSF | **4.7134** | **4.7135** |

**CWRU fan-end / Paderborn 6203-2RS JEM** — `n=8, Bd=0.2656 in, Pd=1.122 in, α=0`:

| Quantity | Computed | CWRU published |
|---|---|---|
| BPFO | 3.0531 | 3.0530 |
| BPFI | 4.9469 | 4.9469 |
| FTF | 0.3816 | 0.3817 |
| BSF (true spin) | **1.9938** | — |
| BPFB = 2×BSF | **3.9877** | **3.9874** |

**THREE THINGS THAT WILL BITE YOU — read carefully:**

- **CWRU's published "Ball" column is 4.7135 and 3.9874. That is `2×BSF`, not `BSF`.** An earlier
  draft of our plan claimed CWRU publishes 2.3570; **that is false.** Store both quantities under
  distinct names (`BSF` and `BPFB`), assert the unit test against **CWRU's published values
  (4.7135 / 3.9874)**, and search `BPFB` as the primary ball line with `BSF` as secondary. Even
  harmonics of ball-spin dominate in envelope spectra because a ball defect strikes both raceways
  once per ball revolution.
- **6203 requires `n=8`.** With `n=9` you get BPFO 3.4348 and the test fails. Some secondary
  sources claim 9 elements for the CWRU fan end; they do not reproduce CWRU's own table. The unit
  test is the arbiter: use whatever reproduces the published multipliers, which is `n=8`.
- **Tolerance: use `atol=5e-4`, not 4-decimal exact.** 6203 `2×BSF` computes to 3.9877 against
  CWRU's published 3.9874 (3e-4 gap, from CWRU's own rounding/geometry). A strict 4-dp assert
  fails. Assert BPFO/BPFI/FTF at `atol=1e-4` and the ball lines at `atol=5e-4`.
- **Never infer pitch diameter from bore and OD.** 6203's Pd (1.122 in = 28.499 mm) happens to
  equal (17+40)/2 = 28.5 mm, but 6205's Pd is 39.04 mm while (25+52)/2 = 38.5 mm. Coincidence, not
  a rule.

### Cage-slip tolerance model — `[VERIFIED]`, closed form derived and numerically confirmed

Theoretical fault frequencies ignore slip/skidding. The measured deviation has a known sign:
outer-race lines fall **below** theoretical, inner-race lines come out **above**. Rather than four
hand-set tolerance windows, **pre-register one constant** `s_max` (cage slip fraction) and derive
both asymmetries:

```
f_c = (1 − s)·FTF                     # cage frequency reduced by slip
BPFO' = Z·f_c            ⇒  ΔBPFO/BPFO = −s                    (exactly, geometry-independent)
BPFI' = Z·(f_r − f_c)    ⇒  ΔBPFI/BPFI = +s·(BPFO/BPFI)        (geometry-dependent)
```

Numerically confirmed:

| s | 6205 BPFO | 6205 BPFI | 6203 BPFO | 6203 BPFI |
|---|---|---|---|---|
| 0.01 | −1.000% | +0.662% | −1.000% | +0.617% |
| **0.02** | **−2.000%** | **+1.324%** | **−2.000%** | **+1.234%** |
| 0.03 | −3.000% | +1.986% | −3.000% | +1.852% |

**Pre-registered value: `s_max = 0.02`.** Note the BPFI shift is **geometry-dependent** — compute it
per bearing from `s·(BPFO/BPFI)`. Do **not** hard-code +1.32%; that is the 6205 value only.

The slip model cleanly covers BPFO and BPFI. **BSF and FTF under slip need separate treatment** —
flag as `UNVERIFIED` and use a symmetric ±s_max window for those two lines until we justify better.

### Datasets

**CWRU** — `[VERIFIED]` Drive end SKF 6205-2RS JEM at 12 kHz and 48 kHz; fan end 6203-2RS JEM at
12 kHz (different bearing, different multipliers — use DE only unless testing sensor placement).
Loads 0–3 hp, ~1730–1797 rpm. EDM single-point faults at 0.007/0.014/0.021/0.028 in. Use the
per-file RPM, never a nominal value.

**Paderborn (PU)** — `[VERIFIED]` Type **6203**, 17×40×12 mm, vibration at **64 kHz**, 4 operating
conditions, 20 measurements × 4 s per bearing. 32 bearings: 6 healthy (K001–K006); 12 artificial
(outer KA01/03/05/06/07/08/09, inner KI01/03/05/07/08); 14 real from accelerated life tests (outer
KA04/15/16/22/30, inner KI04/14/16/17/18/21, combined KB23/24/27). **No ball-fault class.**
Lessmeier et al. established a significant shift between artificial and real damage, with poor
generalisation training on the former and testing on the latter. **PU-artificial → PU-real is our
headline task**: established in the source paper, genuinely hard, bearing-wise clean by
construction, and a direct test of the hypothesis that real spalls degrade the gate.

**JNU** — `[VERIFIED — contradiction resolved]` 50 kHz, 600/800/1000 rpm, 20 s, PCB MA352A60
accelerometer (vertical), wire-cut dents 0.3 mm × 0.05 mm (W×D), bearings 25×52×15 mm, classes
{normal, inner, outer, roller}.

> **The fault-to-bearing assignment is now settled against the original source.**
> Li, Ping, Wang, Chen & Cao, *Sensors* 2013, 13(6):8013–8041, DOI 10.3390/s130608013 (Ping and Cao
> are at Jiangnan University) states verbatim: *"The N205 with separable out-race is used for
> normal, outer-race defect and roller element defect states. The NU205 with separable inner-race
> is used for inner-race defect state."*
>
> **Correct: N205 → normal + outer + roller. NU205 → inner.**
>
> Both our own PROTOCOL v1.0 and several widely-cited secondary papers (e.g. ClassBD, arXiv
> 2404.15341) state the reverse. They are wrong. The mechanics confirm the original: an N-type has
> no flanges on the outer ring (outer ring separable); an NU-type has no flanges on the inner ring
> (inner ring separable). You must separate the ring to expose a raceway for wire-cutting. Cite
> Li et al. 2013 and footnote the widespread secondary error — it pre-empts a reviewer who has
> read the wrong version.

**JNU remains `[BLOCKED]` on one item only:** roller count `Z` and roller diameter for N205/NU205
were not obtainable from any manufacturer catalogue (SKF/NSK/FAG/NTN pages give only the
25×52×15 mm envelope). **Without `Z`, JNU kinematics cannot be computed.** `kinematics.py` must
raise for these bearings. JNU is therefore **not on the critical path**; it can still be used for
SFDA baselines (which need no kinematics) but not for the gate until `Z` is resolved.

**HUST** — `[VERIFIED with caveats]` **Hanoi** University of Science and Technology (not Huazhong).
Thuan & Hong, *BMC Research Notes* 16(1):138, 2023, DOI 10.1186/s13104-023-06400-4; Mendeley Data
DOI 10.17632/cbv7jyx4p9. **99** raw signals, **51,200 Hz**, 10 s each; 3 loads (0/200/400 W);
1 HP induction motor; PCB352C33 accelerometer; 0.2 mm wire-cut cracks; **five bearing models
6204–6208**, so kinematics resolve **per file**, not per dataset. File naming encodes model and
load (e.g. `I402.mat` = Inner-race, 6204, 200 W).

> **Correction to our earlier plan:** arXiv 2302.12533 is **NOT formally withdrawn.** It carries
> the comment "We are considering some issues in the paper." Do not write "withdrawn" anywhere.
> The 90-vs-99 signal count is a genuine preprint-vs-published difference. Cite the BMC version.
> Note also that a survey (arXiv 2504.11581) reports 25,600 Hz / 20 s for HUST, conflicting with
> the primary paper's 51,200 Hz / 10 s. **Trust the BMC primary source.**

**HUST `[BLOCKED]`:** per-load shaft RPM was not found in any open source. Needed from the BMC full
text or the Mendeley per-file `rpm` field.

### Label spaces — `[FROZEN]`

- **L3 = {Normal, Inner, Outer}** — the only space common to all four datasets, because PU has no
  ball class. Mandatory for any task involving PU.
- **L4 = {Normal, Inner, Outer, Ball/Roller}** — CWRU ↔ JNU ↔ HUST only.
- Compound faults (PU KB\*, HUST 2-combinations) are **excluded from main tables** and reported
  separately as an out-of-label-space stress test. Never silently folded into single-fault classes.

### Splitting policy — `[FROZEN]`

1. **Bearing-wise splits are mandatory.** No physical bearing appears on both sides of any task.
2. **Healthy signals must be split bearing-wise too** — the specific residual leak identified by
   Vieira et al., *MSSP* 258:114640 (2026) in the Hendriks split. PU makes this feasible (six
   healthy bearings). **CWRU has effectively one healthy configuration and therefore cannot be
   bearing-wise split on the healthy class** — state this limitation explicitly; prefer
   PU/JNU/HUST as the healthy source in cross-machine tasks.
3. Fixed-length windows; no overlap across a split boundary. Overlap within a split must be declared.
4. **Secondary table:** every method is run a second time under the conventional condition-wise
   ("leaky") split. The delta between tables is a deliverable, not a diagnostic.

Anchors: Hendriks, Dumond & Knox, *MSSP* 169:108732 (2022) — constructing train/test by operating
condition is not a real domain shift because the same physical bearings appear in both.
Abburi et al. (PHM 2023) — bearing-wise splits score consistently worse than leaky random splits.

### Smith & Randall diagnosability categories — `[VERIFIED]`

Smith WA & Randall RB, *MSSP* 2015, 64–65:100–131. Their Table 4 classifies each record with six
labels, assigned **per diagnostic method**:

| Label | Definition |
|---|---|
| **Y1** | Clearly diagnosable, classic characteristics in both time and frequency domains |
| **Y2** | Clearly diagnosable, non-classic characteristics in either or both domains |
| **P1** | Probably diagnosable — discrete components at expected fault frequencies, but not dominant |
| **P2** | Potentially diagnosable — smeared components appearing to coincide with expected frequencies |
| **N1** | Not diagnosable for the specified fault, but other identifiable problems present (e.g. looseness) |
| **N2** | Not diagnosable at all |

**Three methods** reported per record: Method 1 = raw signal, no pre-processing (benchmark);
Method 2 = with discrete/random separation before envelope analysis; Method 3 = adding spectral
kurtosis / kurtogram band selection.

Table organised by fault location (inner; outer at 3:00/6:00/12:00; ball), fault diameter
(0.007/0.014/0.021/0.028 in), load, and sampling rate (12k/48k). A commonly cited stratification
finds ~44 records clearly diagnosable (Y1+Y2) in the 12 kHz DE subset (~60 fault records + 4
normal baselines). **Transcribe the exact counts from the paper's tables — do not rely on the ~44
summary.**

CSV schema (`metadata/smith_randall_cwru.csv`), per-method columns so nothing is lost:

```
record_id,channel,fault_type,clock_position,fault_size_in,load_hp,fs_hz,rpm,method1,method2,method3,notes
```

where each `methodN ∈ {Y1,Y2,P1,P2,N1,N2}`. **Derive any ordinal collapse in `eval/strata.py`,
never in the CSV.** Do not collapse the three methods at transcription time.

### Competitors and prior art

**Bio-SFDA — `[PARTIALLY VERIFIED — PAYWALLED]`. This is the most important open risk.**

Yoon T, Lee J, Park J, Park B, Jeong J. "Bio-SFDA: Physics-Guided Multimodal Source-Free Domain
Adaptation for Reliable Bearing Fault Diagnosis." *Results in Engineering* 30:111105, 2026.
DOI 10.1016/j.rineng.2026.111105, PII S259012302602133X. Sungkyunkwan University.
**Note: five authors, not two.** Correct the citation in any draft that says "Yoon et al." with two.

Verified from the abstract only: EMA teacher–student pipeline, dual 1D-vibration / 2D-spectrogram
encoder, three modules — **WBC** (signal-hygiene guard filtering corrupted/low-quality target
windows), **EAGLE** ("a physics-guided reliability functional that exploits BPFO/BPFI/BSF and
impulsive-band activity to weight and gate pseudo-labels"), **SPIDER** (bounded multi-metric
controller mapping online accuracy/macro-F1/mAP/loss/ECE to conservative updates of learning rate,
momentum, augmentation strength, acceptance thresholds). Headline result: **CWRU→PU 99.0%
accuracy / 98.5% macro-F1 / 99.0% mAP**, with lower NLL and ECE than source-only and SFDA/TTA
baselines. Ablations reportedly identify EAGLE as the main performance driver.

**NOT VERIFIED and therefore NOT to be asserted anywhere:**
- whether EAGLE uses a 4-bit pattern, a threshold, a weighting function, or a statistical test;
- whether it has any false-alarm-rate control or null distribution;
- whether it reads the measured signal or a model-generated representation;
- which datasets/tasks/classes/windows beyond the CWRU→PU headline;
- the split protocol and whether leakage is present;
- named baselines, stated limitations, future work;
- how fault frequencies and slip tolerance were handled.

An earlier draft of our plan asserted "4-bit threshold pattern, no null distribution, no false-alarm
control, no stratification, no leakage analysis." **None of that is verified. Do not repeat it.**

**PCTL — `[PARTIALLY VERIFIED]`.** Jiao X, Zhang J, Cao J, *Eksploatacja i Niezawodność* 2026,
28(2):211797, DOI 10.17531/ein/211797, Xinjiang University, open access at ein.org.pl. Uses a
rule-based physics validator to supervise a confidence predictor in a diagnosis–verification–feedback
loop, on PU and IEEE PHM 2012, with a Bi-LSTM (hidden 128) plus MLP heads.

> **Our earlier plan asserted that PCTL's validator scores the model's own reconstructed spectrum
> (`s_pred = P_phy(E(x_t))`) and called this "circularity" our sharpest differentiator. That
> reading is only partially supported** — the full PDF is robots-disallowed and could not be
> confirmed verbatim. Publishing a circularity criticism based on a misreading would be seriously
> damaging. **Verify in the full PDF before the claim enters any file.**

**PIUDA.** Jia N, Huang, Ding, Wang, Zhu, "Physics-informed unsupervised domain adaptation framework
for cross-machine bearing fault diagnosis," *Advanced Engineering Informatics* 62 (2024) 102774.
Physics-informed pseudo-label generation from state characteristic frequencies + spectral energy,
plus confidence dynamic enhancement. **Already cross-machine — "cross-machine" is not a
contribution and must not appear in our abstract as a delta.** Not source-free.

**SDALR — `[VERIFIED]`, our M0 reproduction target.** Wu W et al., "Both reliable and unreliable
predictions matter: Domain adaptation for bearing fault diagnosis without source data,"
*Neurocomputing* **657:131661 (2025)**, DOI 10.1016/j.neucom.2025.131661, PII S0925231225023331.
arXiv 2503.08749. Code: `github.com/BdLab405/SDALR`. **It is in Neurocomputing, not Neural
Networks** — the preprint footer saying "submitted to Neural Networks" is stale.

Setup: **PU 8-class where classes ARE individual bearing IDs** — K001 (healthy) + KA04, KA15, KA22,
KA30, KI14, KI17, KI21. Domains A1=N15_M01_F10, A2=N15_M07_F04, A3=N15_M07_F10, all at 1500 rpm.
**JNU 4-class** (H/IR/OR/B), domains B1=600, B2=800, B3=1000 rpm. Both: window 2048, 2000
samples/class, six transfer tasks. 1D-modified ResNet-18; classifier = FC with weight
normalization + softmax. SGD, batch 64; source lr 7e-3 / 10 epochs; target lr 5e-4 / 20 epochs;
decay `lr₀·(1+10p)^(−0.75)`.

Reproduction targets:

| | SHOT | SF-CA | SFAD | **SDALR** |
|---|---|---|---|---|
| **PU avg** | 88.25 | 90.80 | 87.23 | **96.78** |
| **JNU avg** | 91.11 | 97.41 | 97.12 | **98.50** |

Per-task PU — SHOT: 86.41 / 94.58 / 82.58 / 85.12 / 92.95 / 87.88 · SF-CA: 89.61 / 96.70 / 86.47 /
86.27 / 95.03 / 90.71 · **SDALR: 87.03 / 99.95 / 96.19 / 99.73 / 99.96 / 97.84**
(note SDALR's first task is anomalously low at 87.03 — expect it).

Per-task JNU — SHOT: 94.31 / 88.35 / 90.27 / 84.37 / 92.05 / 97.29 · SF-CA: 99.48 / 98.59 / 94.71 /
98.81 / 93.28 / 99.60 · **SDALR: 99.98 / 100.00 / 96.41 / 100.00 / 94.71 / 99.92**

> **Structural finding to report, not hide:** because PU classes *are* bearings, SDALR's PU task
> cannot be made bearing-wise without changing the task. M1 therefore collapses PU to **L3**
> {healthy, inner, outer}, uses all six healthy bearings, and holds out whole bearings.
> "The classes are bearings" becomes an explicit reported result.

**`predictive-maintenance-mcp` — `[VERIFIED]`, NEW and partially pre-empting claim 2.**
`github.com/LGDiMaggio/predictive-maintenance-mcp` (also on PyPI). Implements a blind, reproducible
CWRU diagnostic-accuracy benchmark **explicitly stratified by Smith & Randall per-record
diagnosability grades (Y1/Y2/P1/P2/N1/N2)**, reporting 44/44 characteristic-frequency detection and
34/44 (77.3%) correct-first-rank on the Y1+Y2 stratum of the 12 kHz DE subset (60 fault records +
4 normal baselines). **Cite it and differentiate**: ours is an SFDA-specific, FAR-controlled
statistical gate evaluated under domain shift, not a rule-based expert screen on in-domain data.
Read its benchmark code before finalising our stratification design — it may save transcription work.

**Not pre-empted, per search:** (i) a leakage-safe cross-machine SFDA evaluation protocol with
bearing-wise splits; (iii) a physics pseudo-label gate as a statistical hypothesis test with
controlled false-alarm rate built on the Borghesani et al. 2013 SES threshold.

### Signal-processing foundation — `[VERIFIED]`

- **Borghesani, Pennacchi, Ricci & Chatterton, *MSSP* 40(1) 2013, 38–55** — "Testing second order
  cyclostationarity in the squared envelope spectrum of non-white vibration signals." Analytical
  thresholds for CS2 peaks that drop the white-noise assumption. **Use this. Do not derive our own
  null distribution.** Our contribution is applying it as a pseudo-label gate.
- Non-Gaussian background noise degrades these estimators; **log-envelope indicators are more
  resilient** (Borghesani & Shahriar). This is ablation A3, not optional.
- Antoni — fast kurtogram (baseline band selector). IESFOgram / Combined Improved Envelope Spectrum
  via cyclic spectral coherence (upgrade), motivated by damage exciting several bands at once.
- Antoni & Borghesani, *MSSP* 114 (2019) 290–327 — statistical design of condition indicators.

### Venue notes — `[VERIFIED]`

- **RESS**: IF ≈ 8.1, Elsevier hybrid, subscription route free. Primary target.
- **IEEE TII excluded**: 10-page hard cap on new Regular Papers, $250/page overlength from page 11,
  <20% acceptance. Our experimental matrix cannot fit.
- **Results in Engineering** (where Bio-SFDA sits) is gold OA, Q1 by SCImago, but published **4,689
  articles in 2025** with roughly **5 weeks** submission-to-publication. This is a high-throughput,
  rapid-publication profile. It does **not** license us to dismiss Bio-SFDA — it means its headline
  number deserves the same scrutiny we apply to everything else. State this neutrally if at all.
- **Zhao et al., UDTL survey, *IEEE TIM*** lists **"physical priors"** among rarely-studied open
  issues in UDTL-based fault diagnosis, alongside feature transferability, backbone influence, and
  negative transfer. This is our Introduction anchor. Code: `github.com/ZhaoZhibin/UDTL`
  (`resnet18_1d` — use theirs).

---

## THE CENTRAL RESEARCH TENSION

Bio-SFDA reports **99.0% on CWRU→PU**: a transfer between a 6205 at 12 kHz with EDM faults and a
6203 at 64 kHz with real spalls. The honest four-dataset cross-machine benchmark (*Sensors* 2025,
25(14):4383, which already built a unified four-dataset protocol with consistent class and sensor
settings) reports **F1 ≈ 0.47** on comparable shift.

**Those two numbers cannot both describe the same problem.** The most likely explanations, in order:
differing label spaces, window-level leakage, condition-wise rather than bearing-wise splitting, or
a genuinely easier task definition. **Determining which is the paper.** That is claim 1, and it is
an empirical question we can settle on a T4.

---

## SESSION 0 — evidence acquisition (NO CODE)

Do not write code. Do not scaffold. This session exists because our last plan asserted six
unverified facts about a competitor and built a contribution around them.

**Tasks:**

1. Obtain the **Bio-SFDA full text** (ScienceDirect PII S259012302602133X; *Results in Engineering*
   is gold OA so it should be freely readable — if it is not, use institutional access). Extract and
   record, in `notes/bio_sfda.md`, with page/section references: EAGLE's exact mechanism and
   whether it has FAR control; its input representation (measured vs model-generated); all datasets,
   classes, window lengths; **the exact split procedure and whether bearings recur across splits**;
   all per-task numbers; named baselines; stated limitations.
2. Obtain the **PCTL full text** (ein.org.pl, open access). Settle whether PCV scores the measured
   envelope or a model-predicted spectrum. Record in `notes/pctl.md`. **Our circularity criticism
   lives or dies here.**
3. Obtain the ***Sensors* 2025, 25(14):4383** full text (MDPI, open access). Record its exact label
   space, split procedure, and preprocessing in `notes/sensors_benchmark.md`. This is the F1 ≈ 0.47
   anchor for our central tension.
4. Read `predictive-maintenance-mcp`'s benchmark code. Record in `notes/pmmcp.md` what it already
   does with Smith & Randall strata and whether its transcription is reusable.

**Acceptance:** four notes files exist, each with direct quotations and section references, and a
one-page `notes/POSITIONING.md` stating which of our three claims survive contact with the full
texts. **If Bio-SFDA turns out to use bearing-wise splits or FAR control, we re-scope before writing
a line of code.**

---

## SESSION 1 — repo scaffold and verified Kaggle bridge

Ends when a Kaggle kernel prints `Tesla T4`. **No training. No gate code. No dataset uploads.**

### File tree

```
PROTOCOL.md                       # research contract + §13 change log (see corrections below)
CLAUDE.md                         # ops notes; "Current milestone: M0"
KICKOFF.md                        # this document
.gitignore                        # kaggle.json .kaggle/ runs/ results/*.tmp *.pt *.mat data/ *.pdf
requirements.txt
notes/                            # Session 0 outputs
configs/
  bearings.yaml                   # geometry + source URL per number + verified flag
  datasets.yaml                   # paths, fs, class maps, RPM tables
  splits.yaml                     # stub, Session 3
  tasks.yaml                      # stub, Session 3
physics/
  kinematics.py                   # BPFO/BPFI/BSF/BPFB/FTF + slip-window helper
tests/
  test_kinematics.py
kaggle/
  pack_repo.py                    # repo -> private versioned Kaggle Dataset
  push.py                         # T4 enforced IN CODE
  poll.py
  pull.py
  preflight.py                    # refuses to push if a kernel is queued/running
  hello_t4.py                     # prints device name + capability
metadata/
  smith_randall_cwru.csv          # header + schema only; human fills rows
results/.gitkeep
```

### Component specifications

**`configs/bearings.yaml`** — per bearing: `n`, `Bd_in`, `Pd_in`, `alpha`, a `source:` URL comment,
and `verified: true|false`. `N205` and `NU205` get `verified: false` with
`blocked_on: "roller count Z and roller diameter not in any manufacturer catalogue"`.
Record the resolved fault assignment (N205 → normal/outer/roller; NU205 → inner) with the
Li et al. 2013 DOI as the source comment. HUST 6204–6208 each get their own entry.

**`physics/kinematics.py`** —
- Returns a dataclass with `BPFO, BPFI, FTF, BSF, BPFB` where `BPFB = 2*BSF`. Never conflate.
- **Raises `UnverifiedBearingError`** on any bearing with `verified: false`. Silent numbers are
  the failure mode we are engineering against.
- `slip_window(line, s_max)` returns `(f_lo, f_hi)` using the derived asymmetry: BPFO biased low by
  exactly `s_max`; BPFI biased high by `s_max*(BPFO/BPFI)` computed per bearing; BSF/BPFB/FTF use a
  symmetric `±s_max` window and are marked `UNVERIFIED` in a docstring.
- CLI: `python physics/kinematics.py --bearing 6205 --rpm 1772`.

**`tests/test_kinematics.py`** —
- 6205: BPFO 3.5848, BPFI 5.4152, FTF 0.3983 at `atol=1e-4`; **BPFB 4.7135 at `atol=5e-4`**.
- 6203 with `n=8`: BPFO 3.0530, BPFI 4.9469, FTF 0.3817 at `atol=1e-4`; **BPFB 3.9874 at `atol=5e-4`**.
- Assert `BPFB == 2*BSF` exactly.
- Assert slip signs: BPFO window is strictly below theoretical, BPFI strictly above.
- Assert `ΔBPFO/BPFO == -s_max` to machine precision for both bearings.
- Assert `kinematics(N205)` raises.
- Runs on CPU in under 30 s.

**`kaggle/push.py`** — hard-codes T4 enforcement; asserts `enable_gpu: true` in generated metadata;
**exits non-zero without pushing** for any accelerator other than `NvidiaTeslaT4`. Shells out to the
resolved `kaggle` executable path; never `import kaggle`.

**`metadata/smith_randall_cwru.csv`** — header only, schema exactly as specified above.

### Acceptance tests — all five must pass

1. `python -m pytest tests/ -q` passes, CPU, under 30 s, with the tolerances above.
2. `python physics/kinematics.py --bearing N205` raises a clear "unverified geometry" error.
3. `python kaggle/push.py --accelerator NvidiaTeslaP100` exits non-zero **without pushing**.
4. `python kaggle/preflight.py` reports no kernel queued or running.
5. Hello-world kernel pushed, polled, pulled; `results/hello_t4.json` contains
   `device_name: "Tesla T4"` and `capability: [7, 5]`. **Nothing proceeds until this prints.**

`git status` clean; commit tagged `session1: scaffold + verified Kaggle T4 bridge`.

### PROTOCOL.md change-log entries required this session

| ID | Change | Justification |
|---|---|---|
| C1 | Ball line split into `BSF` (true spin, 2.3567 / 1.9938) and `BPFB` (2×BSF, 4.7135 / 3.9874). Unit test asserts CWRU's published values. | An earlier draft claimed CWRU publishes 2.3570. It does not; it publishes 4.7135. Both quantities are needed; naming them separately prevents a factor-of-two error. |
| C2 | SDALR cited as *Neurocomputing* 657:131661 (2025), DOI 10.1016/j.neucom.2025.131661. | Preprint footer "submitted to Neural Networks" is stale. |
| C3 | HUST cited as BMC Res. Notes 16(1):138 + Mendeley. **"Withdrawn" claim about arXiv 2302.12533 removed.** | The preprint is flagged ("We are considering some issues"), not withdrawn. 90-vs-99 is a preprint/published difference. |
| C4 | JNU assignment corrected to N205 → normal/outer/roller, NU205 → inner, per Li et al., *Sensors* 2013, 13(6):8013–8041. | PROTOCOL v1.0 had it reversed. Resolved against the original source; mechanics (separable ring) confirm. |
| C5 | 6203 element count fixed at `n=8`; tolerance for ball lines relaxed to `atol=5e-4`. | `n=9` fails to reproduce CWRU's published BPFO. 6203 2×BSF computes 3.9877 vs published 3.9874. |
| C6 | `s_max = 0.02` pre-registered as the single slip constant; BPFI shift derived per bearing as `s·(BPFO/BPFI)`, not hard-coded. | Specification of a `[VERIFY]` item, not a change to a `[FROZEN]` one. Derives the asymmetry instead of asserting it. |
| C7 | Bio-SFDA added as primary prior art with five authors; all mechanism claims marked UNVERIFIED pending Session 0. | Prevents asserting unverified competitor internals. |
| C8 | `predictive-maintenance-mcp` added as partial prior art for claim 2. | Already stratifies CWRU by Smith & Randall grades. |

---

## MILESTONE PATH

| Session | Deliverable | Gate |
|---|---|---|
| **0** | Four full-text notes + `POSITIONING.md` | If Bio-SFDA is leakage-safe or FAR-controlled, re-scope before coding |
| **1** | Scaffold + verified T4 bridge | Five acceptance tests |
| 2 | Dataset loaders + private Kaggle Dataset uploads (CWRU DE, PU first) | — |
| 3 | `splits.yaml` + load-time assertion that hard-fails on any bearing ID appearing on both sides | — |
| 4 | **M0**: reproduce SDALR on its own PU + JNU tasks | If the published table doesn't reproduce, stop and reassess the literature |
| 5 | **M1**: PU relabelled to L3, bearing-wise. Two numbers, one delta | The delta is a result either way |
| 6 | `band_select.py` → `ses.py`; precompute and cache SES per dataset | Kinematics tests already green |
| 7 | **M2 / A7**: gate + Jaccard overlap vs confidence filtering | **Near-total overlap ⇒ pivot to the protocol paper** |
| 8 | **M3**: oracle-gap table (ungated / gated / oracle SHOT-clean) on 3 tasks | Small gap ⇒ reframe: pseudo-label noise was not the bottleneck |
| 9 | **M4**: diagnosability stratification | Core external-validation result |
| 10 | **M5**: PU-artificial → PU-real headline task | The fidelity hypothesis test |
| 11+ | **M6**: full matrix, 5 seeds, Wilcoxon/Friedman, t-SNE | Submission-ready |

**Pull forward:** at the end of Session 4, once SDALR reproduces, dump its pseudo-labels and
confidence scores to disk. Session 7's Jaccard then needs no retraining. One extra file write now
saves a full GPU cycle later.

---

## METRICS — `[FROZEN]`

Raw accuracy deltas are **not** the headline.

1. **Oracle-gap closure.** Three conditions per task: `ungated`, `gated`, `oracle` (pseudo-labels
   filtered by ground truth, SHOT-clean style). Headline = **fraction of the ungated → oracle gap
   the gate closes.** If the gap is small, the finding is that pseudo-label noise was not the
   bottleneck — publishable either way.
2. **Pseudo-label noise transition matrix**, before and after gating. Shows *which* confusions the
   physics removes.
3. **Diagnosability stratification.** Gate precision/recall per Smith & Randall stratum. Hypothesis:
   gate rejection rate tracks their expert categorisation.
4. Per-class always, with ball/roller reported separately — **we predict the gate is weak there**,
   because a ball spins as well as rolls and its characteristic frequency is hard to find.
   Macro-F1 alongside accuracy. 5 seeds minimum. Wilcoxon signed-rank pairwise; Friedman + post-hoc
   across many tasks.

---

## ABLATIONS — `[FROZEN]`, decided before results are seen

- **A1** gate on/off
- **A2** band selection: fast kurtogram vs IESFOgram vs fixed band
- **A3** SES vs log-envelope spectrum
- **A4** rejected samples discarded vs retained with entropy-only loss
- **A5** α sweep → gate ROC
- **A6** harmonic family depth (fundamental / +harmonics / +shaft sidebands for BPFI)
- **A7** **overlap with confidence filtering (Jaccard)** — highest priority, run earliest

---

## OPEN ITEMS ASSIGNED TO THE HUMAN

These block later sessions. Do not let me forget them.

1. **Transcribe `metadata/smith_randall_cwru.csv`** from Smith & Randall Table 4, per-method
   columns, no collapsing. Check `predictive-maintenance-mcp` first — it may already have this.
2. **Resolve JNU roller count `Z` and roller diameter** for N205/NU205 from a manufacturer
   catalogue or by contacting Jiangnan University. Until then JNU has no kinematics.
3. **Confirm HUST per-load shaft RPM** (0/200/400 W) from the BMC full text or Mendeley per-file
   `rpm` field.
4. **Sign off `s_max = 0.02` as pre-registered** before any gate result is seen.
5. **Obtain Bio-SFDA and PCTL full texts** (Session 0).

---

## BEHAVIOURAL EXPECTATIONS

- Tell me when I am wrong. Three of my earlier "verified gaps" evaporated under audit, and one
  "correction" in the last plan was itself backwards. Push back with sources.
- When a number matters, compute it and show me the computation. Do not assert.
- Prefer the boring option. The contribution is the gate and the protocol, not the code.
- If an acceptance test fails, stop and report. Do not work around it.
- Keep every claim in the manuscript traceable to either a primary source or a run in `results/`.
