# notes/jeong_2025.md — Jeong et al., Sensors 2025, 25(14):4383

**Status: [VERIFIED — FULL TEXT READ]** 2026-09-13 (PDF supplied). Complements `sensors_benchmark.md`
(datasets and taxonomy, C20).

## Ablation, Table 6 (target-domain test) — verbatim numbers

| configuration | order preproc. | reconstruction | TTT | target P / R / F1 |
|---|---|---|---|---|
| Baseline | x | x | x | 0.26 / 0.26 / 0.23 |
| + Order spectrum preprocessing | o | x | x | 0.48 / 0.50 / 0.46 |
| + Reconstruction | o | o | x | 0.48 / 0.50 / 0.46 |
| + Ours (TTT) | o | o | o | 0.50 / 0.51 / 0.50 |

Order preprocessing carries F1 0.23 → 0.46; reconstruction adds nothing; test-time training adds 0.04.
Audit C31 is **confirmed** (and single-seed: "random seed fixed at 42", §4.3.1).

## What their "order spectrum" is (§3.1, Algorithm 1)

FFT magnitude of the raw window → frequency axis divided by the shaft frequency → orders up to 10× →
log(1+|X|) → scaling. **Speed-only normalisation of the plain (not envelope) spectrum**; no geometry,
no envelope, no DRS, no sidebands. Adaptation is test-time training, not SFDA with pseudo-labels.

## How our rungs differ, stated before any ladder result

- **Their order spectrum ≈ our L1 run on an order axis, minus the envelope.** It is not our L3 (L3 =
  L2.5 [DRS + kurtogram band + SES] + angular resampling).
- Their evidence is precisely the H4 failure mode: normalising speed does most of the work. **H4 risk:
  High (C38).** L3 is run and cached before any L4/L5 comparison is interpreted.
- Delta sentence for Related Work: "Jeong et al. normalise speed on the raw spectrum; KNEOS-HC also
  normalises geometry, operates on the pre-whitened squared envelope, and exposes sideband and
  shaft-residual channels — H4 tests whether the addition matters."
