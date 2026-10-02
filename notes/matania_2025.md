# notes/matania_2025.md — Matania, Cohen, Bechhoefer & Bortman, MSSP 224:112117 (2025)

**Status: [VERIFIED FROM THE AUTHORS' PUBLIC CODE]** 2026-09-13. Paper text paywalled (doi 10.1016/j.ymssp.2024.112117),
not read. Repository read in full: github.com/omriMatania/zero_fault_shot_learning_for_bearing_spall_type_classification
(MATLAB + one notebook; README cites the MSSP paper). Statements below describe **what the code does**.

## The "physics-based invariant feature space", exactly

`physical_doamin_adaptation.m` → for each signal (already in the **cycle / angular domain**, `sigs_cyc`):
1. `calc_order_of_envelope.m`: |hilbert(x)|² → |FFT| → one-sided **order-domain squared envelope spectrum**.
2. `extract_bpfo_bpfi_bsf_values.m`: for each family in {BPFO, BPFI, BSF} and harmonic k = 1…`num_harmonies`
   (**10** in `main.m`), take the **maximum** of the order SES inside **[(1−tol)·k·o, (1+tol)·k·o]**, `tol = 0.02`
   (symmetric, all families; BSF = 1× spin, not 2×).
3. Feature vector of 30 values, divided by its RMS.
4. Classifier (notebook) trained on **simulated** signals (`generate_simulated_bearing_signal.m`, spall orders
   3.5 / 5.2 / 2.2) plus endurance-test signals augmented by **re-scaling the order axis of BPFO spectra to other
   spall types** (`convert_bpfo_of_env_order_2_new_spall_type.m`, inner/ball amplitude ×0.5). Tested on CWRU, MFPT,
   PU, XJTU-SY, PRONOSTIA/FEMTO, NBSWT.
No pre-whitening/DRS, no sidebands, no shaft or cage channel, no statistical test, no target adaptation.

## Consequence for KNEOS-HC — decision C66

Our L4 (harmonic coordinates, J = 0) **is** Matania's feature space up to discretisation (we keep 9 sub-bins per
window instead of the max; we add C/S channels and DRS). The core idea — kinematic harmonic positions in the order
SES as a machine-invariant representation — is **TAKEN (2025, MSSP)**.

What remains ours, each already a separate hypothesis and none a headline:
- sideband channels (J = 2) — **H5**;
- DRS before the representation — **H6 / L2.5**;
- the same coordinates driving a pseudo-label gate in SFDA — claim 1, now an *evaluation* (C65);
- memorisation under leakage — **H9** (applies equally to Matania-style features; test both).

## Delta sentence (Related Work)

"Matania et al. project order-domain envelope spectra onto kinematic harmonic peaks to train a zero-fault-shot
classifier from simulation; we use the same kind of coordinates as (i) an input rung (reimplemented, L4) and
(ii) the basis of pseudo-label gates in source-free adaptation, and ask under a leakage-safe protocol whether
sidebands, pre-whitening or a statistical gate add anything."

## Contact

Omri Matania (omrimatania@gmail.com, per `main.m`) / Jacob Bortman, BGU PHM Lab — full-text request is optional now.
