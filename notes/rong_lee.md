# notes/rong_lee.md — Rong & Lee 2025

**Status: [VERIFIED — FULL TEXT READ]** 2026-09-13, PDF supplied by the researcher (SHM, 27 pp.).

Rong Z, Lee J. "An interpretable transfer learning method for bearing diagnosis across different
systems, faults, and signal types." *Structural Health Monitoring* (2025). doi:10.1177/14759217251363600.

## The one question — ANSWERED: the **time signal**

- "Feature reshaping" (pp. 11–12): 30 Hz Butterworth high-pass → **down-sampling of the time signal**
  by `M = fs / f_s' = fs / (2·m·f0)` with bandwidth factor `m = 2`, where `f0` is "the center
  frequency of the characteristic signal", located by FFT spectral analysis → CWT image → power-law
  amplitude transform `A = A0^k` to suppress secondary components.
- Case study 2 (p. 21): the 51.2 kHz acoustic signal "is resampled to 10 kHz", then segmented and CWT'd.
- `f0` is a **data-derived spectral peak**, not a kinematic BPFO/BPFI computed from geometry and speed.
- Transfer is **supervised fine-tuning with labelled target data** (limited labels), not SFDA.

## Delta for KNEOS-HC (Related Work, one sentence)

Rong & Lee move a data-derived spectral peak to a fixed position by resampling the time signal and
then fine-tune on labelled target data; KNEOS-HC places every fault family at a fixed harmonic index
from kinematics and measured speed, carries sideband and shaft channels explicitly, needs no target
labels, and shares those coordinates with a statistical gate. **The PARTLY-TAKEN row becomes
"characteristic-frequency time-signal resampling: TAKEN (Rong & Lee); kinematic harmonic coordinates:
not found".** Their method is not order normalisation and not source-free.
