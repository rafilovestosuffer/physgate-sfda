# B7-UORED (descriptive) and H8 — PROTOCOL C55; speed amendment C68 WITHDRAWN by C69

Artifacts: `b7_records.csv`, `b7_summary.json`, `b7_sensitivity.json`, `../uored_speed_check.txt`.
60 records (20 bearings × healthy + 2 fault states), full 10 s, 6203_UORED geometry (C54), comb gate L4, α = 0.05.

## 1. Speed source — what happened, in order

1. C55 pre-registered the file's logged (Hall, single reading) speed.
2. Before any verdict, the logged value disagreed with the raw-spectrum peak in 28.5–31.0 Hz by > 2 % in 34/60 files,
   and C68 made the spectral peak primary.
3. After the run, the fault lines themselves showed the spectral peak is **not** the shaft rate: in inner/outer files the
   strongest BPFI/BPFO lines sit at a ratio to spectral-speed theory that is **constant across harmonics** (+1.00 % inner;
   +0.96 % and +2.0 % outer). Outer-race lines cannot sit above theory under cage slip, so the reference speed is low. The
   logged speed matches those ratios (e.g. O_9: logged/spectral 1.0084 vs line ratio 1.0096; O_6: 1.0189 vs 1.0200; I_4:
   1.0120 vs 1.0100). It is grossly wrong in O_7 (+5.4 %, +22.7 %), O_8 (+9 %) and the matching H_7/H_8 files.
4. **C69:** because step 3 used fault lines, the primary reverts to the pre-registered logged speed (not chosen by
   outcome); both arms are reported; the 6 files with |logged/spectral − 1| > 5 % are a declared sensitivity exclusion.

## 2. Results (records; bearing-level in brackets)

| arm | outer: says / precision / recall | inner: says / precision / recall | ball recall | healthy FA | I→O |
|---|---|---|---|---|---|
| none · logged | 7 / 0.86 / 0.60 | 7 / 1.00 / 0.70 | 0.0 | 3/20 | 0 |
| **cepstrum · logged (primary)** | 5 / **1.00** / 0.50 [bearings 6, 7, 9] | 5 / **1.00** / 0.50 [**4 of 5**: 1, 2, 4, 5] | 0.0 [0/5] | **0/20** | 0 |
| none · spectral | 23 / 0.26 / 0.60 | 4 / 0.25 / 0.10 | 0.2 | 9/20 | **9** |
| cepstrum · spectral | 10 / 0.40 / 0.40 | 0 / — / 0.0 | 0.1 | 0/20 | **6** |
| primary, excluding 6 speed-compromised files | 4 / 1.00 / 0.67 | 5 / 1.00 / 0.50 | 0.0 | 0/18 | 0 |

(Exact Wilson intervals in `b7_summary.json`; n = 10 per class, so every interval is wide.)

## 3. H8 (decision on the primary arm): NOT SUPPORTED

Cage records called normal R_c = 0.90 (9/10; one called ball); I/O/B records called normal R_f = 0.67; difference 0.23 ≥ 0.15
but one-sided Fisher p = 0.15 ≥ 0.05. Low power was declared in C55. (The spectral arm "supports" H8 only because the gate
fails on the fault records there; it is not the primary and is not claimed.)

## 4. What B7-UORED shows

- **Envelope gating on naturally developed faults is precise with no healthy false alarms**, and on this rig engages 4 of 5
  inner-race bearings and 3/5 outer-race bearings, ball 0/5 — a markedly higher bearing-level coverage than Paderborn (C65).
- **Speed error is a first-order failure mode on the 6203 geometry.** A ≈ 1.2 % speed underestimate turns 6–9 of 10 inner-race
  records into confident *outer-race* calls, while the correct speed gives zero such confusions. On PU the analogous
  confusion came from pre-whitening being absent (KI16). Both are the same geometry-lock hazard: fault combs of a 6203 sit a
  few percent from shaft-harmonic-aligned positions, so a percent-level error in f_r moves evidence between families.
- The shaft-harmonic inner→outer confusion seen on PU KI16 without pre-whitening does **not** reproduce here (0 with the
  logged speed, raw arm). The "lock replicated on a second rig" claim is therefore **not** made; the geometric proximity is
  replicated, the failure mode is speed-conditional.
- UORED's logged speed is unreliable in ≥ 6/60 files by > 5 %; anyone gating UORED must validate speed.

## 5. Third speed arm — cage-comb (FTF) speed, C74 (added 2026-09-13)

`b7_ftf_records.csv`. 15/60 files carry a qualifying cage comb (≥ 3 of 4 harmonics z > 20). At f_r = f_FTF / 0.3812,
cepstrum arm, C30 and comb_v2 agree on every file:

| class | files | called correctly | notes |
|---|---|---|---|
| healthy | 5 | 5 normal | 0 false acceptance |
| outer race | 5 (O_7 ×2, O_8_1, O_9 ×2) | **4 outer** (O_8_1 normal) | O_7 correct here; logged speed is +7.6 % / +25 % off for O_7 |
| ball | 4 | 0 | **B_11_1 carries a textbook ball signature** (BPFB 119.40 Hz with ±FTF sidebands, FTF comb z 318→107) and is still called normal — a gate miss that speed does not explain; to diagnose |
| cage | 1 | normal (no cage family in L4) | — |
| inner race | 0 qualify | — | inner-race UORED stays out of headline claims (C74) |
