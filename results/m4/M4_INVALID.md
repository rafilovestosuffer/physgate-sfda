# M4 (C29) — declared INVALID as a test of claim 2. Specification defect in the gate detector.

**Status:** the pre-registered run (commit 61961b8) completed and, by the letter of C29, returned
ρ = 0.270, one-sided p = 0.018 → "supported". **That verdict is not reported as support.** The run
exposed a defect in the detector, so it measured the defect, not diagnosability.

The files `m4_records.csv` and `m4_summary.json` are retained unchanged as the evidence.

## What the run showed

- The gate called **57 of 60 fault records "normal"** (cepstrum arm; overall agreement 5 %).
- On all four textbook-grade (Y1) inner-race records (209–212) every family returned **p = 1.000**.
- A correlation of 0.27 between grade and a 5 % agreement rate is driven by 2 of 9 Y1 outer-race hits
  and is not evidence that the gate tracks expert diagnosability.

## Diagnosis on record 209 (Y1 inner race, 1797 rpm file speed)

The fault is plainly present. Largest envelope-spectrum peaks (cepstrum arm, 2–4 kHz band):
**161.8 Hz (BPFI), 191.8 (BPFI + f_r), 323.8 (2×BPFI), 485.6 (3×BPFI).**

**Defect 1 — window position.** Predicted BPFI = 5.4152 × 29.95 Hz = 162.19 Hz. The pre-registered
inner-race window is one-sided ABOVE theoretical, [162.19, 164.33] Hz. The measured line, 161.8 Hz,
sits 0.24 % BELOW it, outside the window. The slip model encodes the sign of slip, but a recorded shaft
speed that is slightly high shifts every line down, and **speed-measurement error has no fixed sign.**

**Defect 2 — dilution by the family sum.** Even with symmetric ±2 % windows and a reference excluding all
families' windows, the BPFI test bins average less than the reference (ratio 0.73 on 209, 0.66 on 211).
At Δf = 0.2 Hz a slip window holds tens of bins; summing over the whole window buries a narrow line in
empty bins. The escaped peak then lands in the CFAR reference and inflates it, yielding p = 1.

**Why a simple fix was rejected.**
- Label-free speed estimation from the spectrum's shaft harmonics locks onto **30.000 Hz = half the
  60 Hz mains frequency** (record 211 estimated 30.000 Hz vs 29.20 Hz on file). CWRU's 0 hp shaft speed
  sits 0.17 % from mains/2 — a second coincidence of the same kind as the 6203 lock. Unusable.
- A per-window MAXIMUM restores sensitivity (BPFI p = 4×10⁻¹⁰ on 209) but destroys specificity: BPFO and
  BPFB also returned p ≈ 0 on records 210 and 212, because with 25 wide windows per family some strong
  line of another origin always falls inside.

## Consequence

Both defects share one missing constraint: a speed or slip offset δ moves **every harmonic of a family by
the same fraction**. The detector must scan a common δ across the family's harmonics and sidebands, and
must be calibrated against the record's own line structure. Redesign logged as **C30**; M4 is re-run as
**M4b** under a new pre-registration. H6 had not been run and uses the corrected detector from the outset.
