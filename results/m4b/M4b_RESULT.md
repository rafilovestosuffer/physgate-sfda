# M4b — Smith & Randall stratification with the frozen C30 detector

**Pre-registration:** PROTOCOL C29 (commit 61961b8), re-specified onto the C30 detector by C31
(commit 205ea13), both committed before this run. **This is a second run.** The first run (M4) exposed a
detector defect and is on file as invalid (`results/m4/M4_INVALID.md`). Report M4b as a second run,
always.

Population: 64 CWRU DE records (60 fault, 4 normal), first 5.000 s, L4, α = 0.05, per-file RPM.
Grades: predictive-maintenance-mcp `sr2015_grade` (single collapsed grade; CC BY-NC-SA 4.0).

## Pre-registered primary result — SUPPORTED

Cepstrum arm (primary): **Spearman ρ = +0.565, one-sided p < 0.0001.**

| Grade | n | Gate agreement | Wilson 95 % CI |
|---|---|---|---|
| Y1 textbook | 9 | **0.89** | 0.56 – 0.98 |
| Y2 clearly diagnosable | 35 | 0.26 | 0.14 – 0.42 |
| P1 / P2 partial | 1 / 5 | 0.00 | — |
| N1 not diagnosable | 10 | **0.00** | 0.00 – 0.28 |

Normals called faulty: **0 / 4**. By fault type: outer 0.36, inner 0.44, **ball 0.00** (pre-registered weak).
`none` arm, context only: ρ = +0.463, p = 0.0001; overall agreement 0.33.

## Exploratory — NOT pre-registered, label it so wherever it appears

**The association survives within fault type**, so it is not an artefact of ball records clustering in
low grades:
- outer race, n = 28: ρ = +0.465, one-sided p = 0.006 (Y1 4/5, Y2 6/20, P/N 0/3)
- inner race, n = 16: ρ = +0.713, one-sided p = 0.001 (Y1 4/4, Y2 3/8, N1 0/4)
- ball, n = 16: 0/16 at every grade (no variance)

**Every disagreement is an abstention.** Of the 43 fault records the gate did not agree with, all 43 were
called "normal" (inner 9, outer 18, ball 16). **Zero cross-family confusions.** All 17 fault verdicts were
correct, and all 4 normals were correct. On CWRU the gate behaves as a pseudo-label screen should:
high precision when it admits, abstention rather than a wrong class when evidence is insufficient. The
cost is coverage (28 % of fault records admitted).

## Caveats that travel with this result

- n is small (9 Y1, 4 normals) and CWRU's healthy class is one physical bearing.
- Grades are PMMCP's collapsed grade; Smith & Randall's per-method grades are not yet transcribed.
- The 6205 has no shaft-harmonic lock. This says nothing about the 6203 (Paderborn) — that is H6.
- The detector was revised after M4 exposed a defect on these same 64 records. The revisions were driven
  by synthetic tests and frozen before this run (C30), but the records are not fresh. Out-of-sample
  confirmation comes from H6 (Paderborn), which no version of the detector has touched.
