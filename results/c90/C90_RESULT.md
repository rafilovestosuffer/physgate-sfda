# C90 — empirical slip distribution (PROTOCOL C90, pre-registered 2026-09-15)

Artifacts: `c90_records.csv` (per record, both arms), `c90_summary.json`, `c90_synthetic.txt`.
Scripts: `experiments/c90_slip.py`, `experiments/c90_synthetic.py`. CPU only.
One implementation change was made before the full run and is recorded here: capped comb scores plateau, and argmax returned
the lowest slip on the plateau. Ties are now broken on uncapped z. It was found on 4 smoke records.

## Estimator validity (synthetic, shaft harmonics present)

For injected slips of 0.1 %, 1.0 %, 1.78 %, 2.30 % and 4.0 % on both PU geometries and both races, the recovered ŝ lies within
0.02–0.17 % of the truth, with a small downward bias. Injections at s* are flagged in-lock. The estimator can see a lock when
one is present.

## Result

| population | fault records | valid (unmasked / masked) | slip % (5, 25, 50, 75, 95), unmasked | in-lock, unmasked | in-lock, masked |
|---|---|---|---|---|---|
| PU IBU/MTK (s* = 2.30 %) | 1,519 | 242 / 242 | −0.31, 0.00, **0.06**, 0.10, 0.22 | 0/242 | 0/242 |
| PU FAG (s* = 1.78 %) | 320 | 52 / 49 | −0.31, −0.14, **−0.07**, 0.19, 0.88 | 3/52 (5.8 %) | 0/49 |
| CWRU fan end 6203 (s* = 1.74 %) | 33 | 10 / 10 | −0.61, −0.45, −0.38, 0.10, 0.42 | 0/10 | 0/10 |
| CWRU drive end 6205 (s* = 16.3 %, out of range) | 44 | 21 / 21 | −0.41, −0.37, −0.33, −0.20, −0.11 | — | — |
| **all 6203 geometries pooled** | 1,872 | 304 / 301 | — | **3/304 (0.99 %)** | **0/301 (0 %)** |

PU median slip by condition: N15_M01_F10 0.05 %, N15_M07_F04 0.16 %, N15_M07_F10 0.06 %, N09_M07_F10 −0.26 %.
Artificial damage 0.09 %; real damage 0.00 %.

The 3 unmasked in-lock records are all KI21 at N09 (900 rpm). None is valid once shaft-harmonic bins are masked, so they are
shaft-harmonic pickup, not fault lines at s*.

## Decision (pre-registered framing rule)

Pooled 6203 in-lock bracket = [0 %, 0.99 %]. The upper bracket is below 2 %, so **the slip–lock proposition shrinks to a
remark.** Stratum by stratum the conclusion is the same: the one stratum with a non-zero upper bracket (FAG, 5.8 %) is
driven entirely by records that fail the masked arm.

## What this changes

1. **The statement "all four s* values fall within normal slip" (brief, manuscript draft) is withdrawn.** Measured slip on
   these rigs is about 0.1 % (PU: 95 % of valid records within [−0.31 %, +0.22 %]), an order of magnitude below s* = 1.6–2.3 %.
   The 1–2 % figure is a general textbook range, not a measurement on these rigs.
2. The algebra (BPFO + BPFI = n, simultaneous lock at s* = δ/BPFO₀) remains correct and is kept as a short remark. It is
   practically irrelevant on Paderborn and CWRU at their operating conditions.
3. Negative median slip (CWRU about −0.35 %; PU N09 −0.26 %) is not physical cage slip. It is the combined bias of the
   speed reference and nominal geometry at the 0.3 % level, which bounds how precisely any fixed-kinematics gate can
   place its windows. This is consistent with C78's null.
4. The comb gate's δ grid of ±2 % covers the measured slip with a wide margin; its exclusion of s* = 2.30 % has no practical
   consequence.

## Limits

- Only records with ≥ 2 lit fault lines are measurable (16 % of 6203 fault records). A record exactly at lock would still be
  valid in the unmasked arm, which is the arm biased toward lock, and that arm found 3 shaft-pickup cases out of 304.
- UORED is excluded (no independent speed).
- The CWRU fan-end sample is small (10 valid records).
