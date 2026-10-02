# Supplementary S5: measured cage slip and the shaft-order coincidence of 6203 bearings

This material was Section 6.8 of earlier versions. It moved here in revision 6 because it supports the gate design
(the choice of slip window) rather than the paper's argument. Figure: `paper/tex/figures/fig7_slip.pdf`.
Artifacts: `results/c90/c90_records.csv` and `results/c90/` (PROTOCOL C90), with synthetic validation in
`experiments/c90_synthetic.py`.

## The coincidence

Under the cage-slip model BPFO(s) = (1 - s) BPFO_0 and BPFO(s) + BPFI(s) = n. If BPFO_0 = m + δ with m an integer, both
race lines reach integer shaft orders at the same slip s* = δ / BPFO_0:

| Geometry | BPFO_0 (orders) | s* |
|---|---|---|
| Paderborn IBU/MTK 6203 (pitch 29.05 mm) | 3.0706 | 2.30 % |
| Paderborn FAG 6203 (pitch 28.55 mm) | 3.0543 | 1.78 % |
| CWRU fan-end 6203 | 3.0530 | 1.74 % |

Smith and Randall observed lock-like behaviour of the fan-end lines with shaft harmonics on CWRU and noted that it makes a
definite diagnosis difficult. The standard tutorial treatment quotes random slip of 1-2 % (Randall and Antoni 2011), so the
coincidence could matter for any gate that places windows by geometry.

## Measurement

Fault-line positions were fitted against the measured shaft speed on every recording with at least two lit harmonics. On
synthetic signals with injected slips of 0.1 % to 4 % the unmasked estimator recovers the truth to within 0.17 % (the
shaft-masked variant to within 0.28 %); the synthetic set holds 15 cases (the FAG inner-race case is missing).

| Population | Measurable records | Median slip | 5-95 % range | Negative | Min / max |
|---|---|---|---|---|---|
| PU IBU/MTK 6203 | 242 | +0.06 % | -0.31 to +0.22 % | 49 | -1.00 / +4.07 % |
| PU FAG 6203 | 52 | -0.07 % | -0.31 to +0.88 % | 35 | -0.40 / +1.58 % |
| CWRU fan end 6203 | 10 | -0.38 % | -0.61 to +0.42 % | 6 | -0.63 / +0.66 % |
| CWRU drive end 6205 | 21 | -0.33 % | -0.41 to -0.11 % | 21 | -0.44 / -0.09 % |

Measurable 6203 fault recordings are 16 % of the population (those with at least two lit harmonics), a selection towards
recordings with strong fault lines.

## Reading

- The median Paderborn slip (+0.06 %) is smaller than the estimator's validated accuracy (0.17 %); what the measurement
  supports is that slip on these rigs is well below 1 %, an order of magnitude below s*, not a precise value.
- Negative values cannot be cage slip, which only lowers the cage speed. They indicate an offset in the assumed kinematics:
  a non-zero effective contact angle under axial load or clearance, a small geometry difference, or a bias in the speed
  reference. On CWRU, where speed is logged rather than measured, every drive-end value is negative (median -0.33 %), which
  bounds how precisely any fixed-kinematics window can be placed there.
- One IBU/MTK value (+4.07 %) lies outside the ±2 % search band and is an estimator failure, not slip.
- Of 304 measurable 6203 recordings, three fall within tolerance of s*, and all three fail once shaft-order bins are
  masked, which identifies them as shaft pickup. By the criterion fixed before the measurement, the lock is not a practical
  failure mode at these operating points, and the gate's one-sided 2 % window is generous for these rigs.
- UORED is excluded from the slip analysis: its logged speed is unreliable (Supplementary S3), and there is no independent
  speed reference.
