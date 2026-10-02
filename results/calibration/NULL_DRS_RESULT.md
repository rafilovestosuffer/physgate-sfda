# C36 — gate null with DRS in the loop (null-only synthetic)

Source: `results/calibration/null_drs_2026-09-13.json` (script `experiments/null_calibration_drs.py`, 436 s CPU).
Grid: {6205, 6203_PU_2905, 6203_PU_2855} × arm {none, cepstrum} × {white, AR(2)} × α {0.10, 0.05, 0.01}; 300 trials/cell;
fs 12 kHz, T 3.0 s, band 2–4 kHz. Pre-stated pass rule: gate FAR ≤ α + 2 SE in every cell.

## Result: PASS (36/36), with a caveat that must travel with every FAR sentence

| quantity | realised range across the 12 cells | nominal |
|---|---|---|
| **gate** false acceptance (`physical_class != normal`) at α = 0.10 / 0.05 / 0.01 | **0.000** everywhere | 0.10 / 0.05 / 0.01 |
| per-family surrogate p ≤ 0.10 | 0.105 – 0.148 | 0.10 |
| per-family surrogate p ≤ 0.05 | 0.063 – 0.087 | 0.05 |
| per-family surrogate p ≤ 0.01 | 0.020 – 0.037 | 0.01 |

1. **The surrogate p-value alone is anti-conservative** (≈1.3–1.7× at 0.05, 2–4× at 0.01). The surrogates
   are correlated with each other and with the kinematic comb, so the rank test is coarse. We do **not**
   claim an exact p-value.
2. **False-acceptance control comes from the frozen multiplicity rule** (≥ 2 aligned lines at z > 20, C30),
   which pure noise essentially never satisfies. The synthetic null therefore cannot bound the gate's FAR
   from above in a useful way — **the binding number is the realised FAR on real healthy records**
   (PU: 15/480 = 3.1 % [1.9, 5.1] at α = 0.05, cepstrum arm, pre-C35 geometry; re-measured in `results/h6_c35`).
3. DRS in the loop does not move calibration materially (cepstrum arm p-rates marginally lower).

Manuscript wording (C40): "the gate's false-acceptance rate, measured on N real healthy records, was x %
[CI] at nominal α; the per-family surrogate p-value is a ranking statistic, not an exact level-α test."
