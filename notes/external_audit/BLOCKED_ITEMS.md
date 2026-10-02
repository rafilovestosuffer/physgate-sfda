# BLOCKED ITEMS — what I could resolve, what I could not, and a correction

Audit date 2026-09-13. Three requests: the two PDFs, the JNU/HUST geometry, the Smith & Randall
per-method grades. **One is resolved to primary sources, one is confirmed genuinely blocked (and
this corrects C40), one I cannot supply.**

---

## 0. Correction to C40 — I was wrong, and the HUST blocker is real

`PROGRAMME_REV6.md` C40 says manufacturer tables publish ball count, ball diameter and pitch
diameter for 62-series bearings, and therefore that the HUST blocker is "softened". **That is wrong.
Withdraw C40 and restore HUST to fully blocked.**

What I actually found, checking SKF, NTN and distributor catalogues directly:

| Bearing family | Catalogues publish | Internal geometry published? |
|---|---|---|
| Cylindrical roller (N/NU) | `d, D, B` **plus `Ew` (N-type outer raceway) and `Fw` (NU-type inner raceway)** | **Yes, derivable** — see §1 |
| Deep-groove ball (62-series) | `d, D, B`, load ratings, limiting speeds, mass | **No.** No `Z`, no `Dw`, no `Dpw` |

The asymmetry has a physical cause, which is why it is stable and not an artefact of one catalogue:
**cylindrical roller bearings are separable, so the raceway diameters are mounting dimensions the
manufacturer must publish. Deep-groove ball bearings are non-separable, so there is nothing to
publish and nobody publishes it.** SKF's own deep-groove tables for 6204/6206/6207/6208 carry
boundary dimensions and ratings only.

So rule 2 in `CLAUDE.md` — never estimate bearing geometry, unverified bearings RAISE — holds for
HUST. **H2 and B4 stay blocked.** Three honest routes, in order of preference:

1. **Ask the dataset authors.** Thuan & Hong at Hanoi University of Science and Technology ran the
   rig and hold the bearings. They can read `Z` off a disassembled bearing and measure `Dw` with a
   micrometer in ten minutes. This is the only route that yields a primary source. It also resolves
   open item 4 (per-load shaft RPM) in the same email.
2. **Aggregator geometry databases**, e.g. RITEC's calculator (claims ~2 700 bearings, SKF/NTN/Cooper/Dodge)
   and similar tools that expose `Z`, `Dpw`, `Dw` as editable fields rather than only emitting
   frequencies. These are **secondary**. Enter them as `verified: false`, record the URL and the
   accessed date, and apply C13: assert against the closed-form formula, never adopt a published
   frequency table. Note that the same designation genuinely differs between manufacturers, and
   RITEC's own tool warns that using one manufacturer's data for another's part number gives a
   wrong answer.
3. **Accept the block.** Drop H2 and B4, keep HUST as an L3 cross-machine target where the gate is
   not run. This costs one hypothesis and one block, and it is honest.

**Same problem now applies to UORED.** The FAFNIR 203KD is a deep-groove ball bearing, so its
internal geometry is unpublished for exactly the same reason. And the NSK 6203 is not automatically
the geometry already in `configs/bearings.yaml` — that entry reproduces **CWRU's** 6203 table, and
NSK may differ. Before running the gate on UORED, confirm which of the 20 bearings are NSK and which
are FAFNIR, and treat the two as separate `bearings.yaml` entries. Keep open item 9 open.

---

## 1. JNU N205 / NU205 — resolved to two primary sources, which disagree

### Source A — NTN catalogue, raceway diameters (primary, exact)

| | `d` | `D` | `B` | `Ew` | `Fw` |
|---|---|---|---|---|---|
| N205 (inner ring, two ribs, plain outer) | 25.000 | 52.000 | 15.000 | **45.000** | — |
| NU205 (plain inner, outer ring two ribs) | 25.000 | 52.000 | 15.000 | — | **32.000** |

All mm. The two are the same 205 envelope with the same rolling set, so:

```
Dw  = (Ew − Fw) / 2 = (45.000 − 32.000) / 2 = 6.500 mm
Dpw = (Ew + Fw) / 2 = (45.000 + 32.000) / 2 = 38.500 mm
```

NTN publishes no roller count.

### Source B — Sun & Gao, *Sensors* 2024, 24(17):5700, Table 6 (CC BY), citing Li et al. 2013

| | NU205 | N205 |
|---|---|---|
| bore / OD / width | 25 / 52 / 15 mm | 25 / 52 / 15 mm |
| roller diameter | **7 mm** | **7 mm** |
| contact angle | 0 | 0 |
| **number of rollers** | **11** | **10** |

No pitch diameter given.

### They disagree, and the disagreement matters

`Dw` = 6.5 (NTN-derived) vs 7.0 (Sun & Gao). Assuming `Dpw` = 38.5 throughout:

| | `Z` | BPFO | BPFI | FTF | BSF | BPFB |
|---|---|---|---|---|---|---|
| **A** N205 | 10 | 4.1558 | 5.8442 | 0.4156 | 2.8771 | 5.7542 |
| **A** NU205 | 11 | 4.5714 | 6.4286 | 0.4156 | 2.8771 | 5.7542 |
| **B** N205 | 10 | 4.0909 | 5.9091 | 0.4091 | 2.6591 | 5.3182 |
| **B** NU205 | 11 | 4.5000 | 6.5000 | 0.4091 | 2.6591 | 5.3182 |

Shift from A to B: **BPFO −1.56 %, BPFI +1.11 %, FTF −1.56 %, BPFB −7.58 %.**

`s_max` = 0.02. A 1.56 % BPFO shift is **78 % of the entire pre-registered slip window**, and the
7.6 % BPFB shift puts that line clean outside it. A wrong `Dw` here does not perturb the search band,
it vacates it. **Both entries stay `verified: false`.**

To close it, read **Li et al., *Sensors* 2013, 13(6):8013–8041 directly** — it is open access at
PMC3715255, it is already the source you trust for C4, and Sun & Gao cite it as the origin of their
table. If Li et al. give `Dw` = 7 mm, take it; a rig bearing is whatever the rig bearing is, and NTN
is a different manufacturer. If Li et al. give no geometry, Sun & Gao's table is secondary and the
NTN derivation is the better primary anchor.

### The genuinely new finding: `Z` differs between the two bearings

**N205 has 10 rollers; NU205 has 11.** Every JNU class except inner-race comes from the N205; the
inner-race class comes from the NU205. So the JNU inner-race records have *different kinematics* from
every other JNU record. **Kinematics must resolve per class on JNU, not per dataset.** That is a new
constraint on `configs/bearings.yaml` and on any JNU loader — and it is a third independent reason
JNU is structurally unlike the others, alongside C25 and C39.

C4 also picked up two more independent confirmations along the way: both Sun & Gao (*Sensors* 2024)
and a 2026 *Sensors* paper state the N205 covers normal, outer and roller and the NU205 covers inner.
ClassBD's reversal is the outlier, as you had it.

### Drop-in fragment for `configs/bearings.yaml`

```yaml
N205:
  type: cylindrical_roller
  bore_mm: 25.000
  od_mm: 52.000
  width_mm: 15.000
  contact_angle_rad: 0.0
  n_rollers: 10
  roller_diameter_mm: null      # CONTESTED — see below
  pitch_diameter_mm: null       # CONTESTED — see below
  verified: false
  blocked_on: "Dw and Dpw contested between two primary sources; Z from secondary"
  candidates:
    - source: "NTN Bearing Corp. of America catalogue, N205 + NU205 raceway diameters"
      url: "https://bearingfinder.ntnamericas.com/item/single-row-cylindrical-roller-bearings/iso-series-single-row-cylindrical-roller-bearings/n205"
      accessed: "2026-09-13"
      derivation: "Dw=(Ew-Fw)/2=(45.000-32.000)/2 ; Dpw=(Ew+Fw)/2=(45.000+32.000)/2"
      roller_diameter_mm: 6.500
      pitch_diameter_mm: 38.500
      note: "manufacturer NTN; JNU rig manufacturer unknown. Ignores radial internal clearance (CN, ~20-45um), which reduces Dw by ~0.02mm."
    - source: "Sun T, Gao J, Sensors 2024 24(17):5700 Table 6, citing Li et al. Sensors 2013 13(6):8013-8041"
      doi: "10.3390/s24175700"
      accessed: "2026-09-13"
      roller_diameter_mm: 7.000
      pitch_diameter_mm: null
      n_rollers: 10
      note: "SECONDARY. Verify against Li et al. 2013 (PMC3715255) before adopting."
  fault_classes: [normal, outer, roller]     # C4
  fault_class_source: "Li et al., Sensors 2013, 13(6):8013-8041, verbatim"

NU205:
  type: cylindrical_roller
  bore_mm: 25.000
  od_mm: 52.000
  width_mm: 15.000
  contact_angle_rad: 0.0
  n_rollers: 11                 # NOTE: differs from N205. Kinematics resolve PER CLASS on JNU.
  roller_diameter_mm: null
  pitch_diameter_mm: null
  verified: false
  blocked_on: "same as N205"
  fault_classes: [inner]        # C4

6204: &hust_blocked
  type: deep_groove_ball
  n_balls: null
  ball_diameter_mm: null
  pitch_diameter_mm: null
  verified: false
  blocked_on: >
    Deep-groove ball bearings are non-separable, so no manufacturer publishes internal
    geometry. Checked SKF and NTN catalogues 2026-09-13: boundary dimensions and load
    ratings only. Resolve by contacting Thuan & Hong (HUST/Hanoi) or accept the block.
6206: *hust_blocked
6207: *hust_blocked
6208: *hust_blocked
```

Boundary dimensions for the HUST bearings, from SKF, if the loader wants them for sanity checks
only — they do **not** unblock the kinematics: 6204 = 20/47/14, 6206 = 30/62/16, 6207 = 35/72/17,
6208 = 40/80/18 mm.

---

## 2. The two PDFs — I cannot supply these

I can't hand over copyrighted PDFs, and I also could not get past the access controls: ScienceDirect
returned rate-limit and bot-detection responses on repeated attempts, and SAGE blocks automated
fetching. Routes that should work for a human:

**Bio-SFDA** — Yoon T, Lee J, Park J, Park B, Jeong J. *Results in Engineering* 30:111105 (2026),
doi `10.1016/j.rineng.2026.111105`, PII `S259012302602133X`.

- *Results in Engineering* is **gold open access**, so the article is free to read. What blocked me
  was bot detection, not a paywall — resolve `https://doi.org/10.1016/j.rineng.2026.111105` in an
  ordinary browser and it should open.
- Corresponding author is **Jongpil Jeong**, Department of Smart Factory Convergence, Sungkyunkwan
  University. Confirmed author list of five, matching C7.
- Best second route: the paper appears to derive from **Taehwi Yoon's master's work at SKKU**. The
  thesis, if it is in the SKKU library repository, will describe EAGLE, WBC and SPIDER in far more
  detail than the article does — which is exactly what H7 needs. Search the SKKU repository by author
  before emailing.

**Rong & Lee** — *Structural Health Monitoring* (2025), doi `10.1177/14759217251363600`.

- SAGE, almost certainly subscription. Institutional access is the clean route.
- Otherwise: request the author-accepted manuscript directly from the authors, or check whether their
  institution's repository holds it. SAGE permits AAM deposit, so a repository copy often exists.
- Reminder of what you actually need from it, per `PLAN.md` §0 item 5: **one bit** — does their
  characteristic-frequency resampling act on the *time signal* or on the *spectrum axis*? That single
  answer settles the KNEOS-HC novelty-delta wording. It is small enough to ask the authors by email
  rather than waiting for the PDF.

---

## 3. Smith & Randall per-method grades — I don't have them, and nor should I transcribe them

The per-record, per-method table is a substantial data table inside a copyrighted MSSP paper, so I
won't reproduce it even if I could reach it. What I can tell you:

- The category scheme is confirmed: **Y1, Y2, P1, P2, N1, N2**, applied across three methods.
  Method 1 is the benchmark applied to the raw signal; Method 3 adds spectral kurtosis.
- Their own finding, which is what strengthens H6's framing: **Method 2 yields more Y1 and Y2
  outcomes than Method 3**, and they attribute Method 3's weakness to impulsive content unrelated to
  the bearing fault, to which spectral kurtosis is vulnerable. Method 2 is the pre-whitening method.
  That is C11's justification, from their results rather than only ours.
- The most likely existing machine-readable transcription is **`predictive-maintenance-mcp`**
  (L. G. Di Maggio), which already stratifies a CWRU benchmark by Smith & Randall grades and reports
  34/44 correct-first-rank on the Y1+Y2 stratum. **I have not verified whether it stores per-method
  grades or only a pooled diagnosability label** — check that before assuming it saves you the
  transcription. If it only holds pooled grades, human item 1 stands as written.

Either way, keep the per-method columns in `smith_randall_cwru.csv`. Collapsing Methods 1–3 into one
grade is what makes H6 argue from our data alone; keeping them is what lets H6 argue from theirs.

---

## 4. Net effect on the open-items table

| # | Item | Status after this pass |
|---|---|---|
| 1 | Smith & Randall per-method grades | **open**; check `predictive-maintenance-mcp` first |
| 2 | JNU roller count `Z` | **partly resolved** — `Z` = 10 (N205), 11 (NU205) from a secondary source; `Dw`/`Dpw` contested. Read Li et al. 2013 (PMC3715255) to close |
| 3 | HUST 6204/6206/6207/6208 geometry | **fully blocked — C40 withdrawn.** Contact Thuan & Hong, or drop H2/B4 |
| 4 | HUST per-load shaft RPM | open — ask in the same email as item 3 |
| 7 | Bio-SFDA full text | open; try the DOI in a browser, then the SKKU thesis |
| 9 | FAFNIR 203KD geometry | **open and harder than logged** — deep-groove, so unpublished. Also split UORED's NSK 6203 from CWRU's 6203 in `bearings.yaml` |
| — | **NEW: JNU kinematics resolve per class, not per dataset** | must be encoded before any JNU kinematics call |
| — | **NEW: Rong & Lee reduces to one question** | time signal or spectrum axis — email the authors |

Two things to fold into `PROTOCOL.md` §13: **C40 is withdrawn**, and **C42 — JNU kinematics are
per-class because `Z` differs between the N205 and the NU205.**
