# Supplementary S2 — Physics gates: definitions, false acceptance on healthy recordings, and operating curves

Every number traces to a retained artifact (paths given). Gate verdicts are per recording and inherited by the windows of that
recording (PROTOCOL C17).

## S2.1 Gate definitions

| gate | domain | rule | pre-specified parameter |
|---|---|---|---|
| Comb test (C30) | squared envelope spectrum after cepstrum pre-whitening, fast-kurtogram band | harmonic comb (K = 5; inner-race sidebands J = 2) scored at a common slip offset within ±2 %, ranked against 499 surrogate orders; admissible if the surrogate p-value passes α / n_families and ≥ 2 positions carry unmistakable lines | α = 0.05 |
| comb_v2 (C72) | as C30 | additionally rejects a family when ≥ 50 % of its lit positions lie within 1.5 bins of an integer shaft order; arbitration by aligned-line fraction | α = 0.05 |
| Envelope threshold rule (PCV-style) | squared envelope spectrum, no pre-whitening | a harmonic is present if the median-normalised spectrum exceeds z inside its kinematic slip window; a family is declared if ≥ 2 of 3 harmonics are present | z = 10 |
| Raw-spectrum band rule (EAGLE-style) | short-time Fourier transform | band energy and peak-to-neighbourhood ratio at BPFO, BPFI and BSF, robust z-scored across recordings | z = 2 |

The last is our implementation of the mechanism described for Bio-SFDA; the authors' code was not available, so it is reported
as the mechanism as described, as we implemented it, and never compared against their published accuracy.

## S2.2 False acceptance at the pre-specified operating points

Population: 2,319 Paderborn recordings (480 healthy, 1,839 single inner/outer), 3.9 s each
[src: results/h6_c35/, results/h7/H7_RESULT.md, results/comb_v2/COMB_V2_RESULT.md].

| gate | healthy false acceptance | correct fault verdicts |
|---|---|---|
| Envelope threshold rule | 1 / 480 | 366 |
| comb_v2 | 0 / 480 | 312 |
| Comb test | 9 / 480 | 309 |
| Raw-spectrum band rule | 214 / 480 (45 %) | 429 |

## S2.3 Full operating curves

Sweeping each gate's parameter [src: results/roc/ROC_RESULT.md, roc_pu.png]:

| gate | at zero healthy false acceptance | at ≤ 2 % false acceptance | further along the curve (false acceptances of 480) |
|---|---|---|---|
| Envelope threshold rule (z) | **351** correct (z = 15) | 373 (z = 8, 8 FA) | 439 (z = 5, 68 FA) |
| comb_v2 (α) | 312 | 317 (6 FA) | 325 (11 FA) |
| Comb test (α) | — (minimum 2 FA) | 309 (9 FA) | 323 (22 FA) |
| Raw-spectrum rule (z) | 0 | — | 340 (55 FA) |

The envelope threshold rule lies on or above every other gate at every false-acceptance level; the statistical machinery of the
comb test does not buy a better curve on this dataset. No gate exceeds about 20 % correct verdicts (the PCV-style rule's 373 of 1839, at z = 8) before false acceptance passes
10 %: the envelope rule engages 13 of the 23 faulty bearings (7 of 11 real-damage, 6 of 12 artificial), most of them on only part of
their recordings, which is the coverage ceiling that bounds Section 6.6 of the paper.
Recordings within a bearing are correlated, so the curve describes this dataset rather than envelope gating in general.

## S2.4 Negative results on gate coverage

- Ball faults: zero detections on CWRU and UORED under every variant tested, including a sideband-aware test
  [src: results/c77/].
- A fault-frequency-guided band search (IESFOgram-style) raised UORED false alarms to 25–80 % and was not adopted
  [src: results/c79/].
- On naturally developed faults (UORED) the cepstrum arm with logged speed gives zero healthy false acceptances and engages
  4 of 5 inner-race and 3 of 5 outer-race bearings [src: results/b7_uored/B7_UORED_RESULT.md].

## S2.5 Healthy false acceptance by physical bearing

Each bearing contributes 80 recordings. Counts are descriptive; repeated recordings do not supply independent new-bearing replication. Original record-level intervals for zero/one events require an independence assumption and are not deployment safety bounds.

| Bearing | Envelope rule | Guarded comb | Surrogate comb | Raw-spectrum rule |
|---|---|---|---|---|
| K001 | 0 | 0 | 3 | 54 |
| K002 | 1 | 0 | 0 | 15 |
| K003 | 0 | 0 | 3 | 54 |
| K004 | 0 | 0 | 1 | 24 |
| K005 | 0 | 0 | 1 | 15 |
| K006 | 0 | 0 | 1 | 52 |

## S2.6 Agreement with Smith and Randall's diagnosability grades on CWRU (M4b)

The surrogate-null comb (cepstrum arm, alpha = 0.05) against the per-record diagnosability grade of the CWRU benchmark of
Smith and Randall (2015), as collapsed in predictive-maintenance-mcp, on 64 drive-end records (60 fault, 4 normal), first
5.000 s, per-file speed [src: results/m4b/M4B_RESULT.md; pre-registered as PROTOCOL C29, re-specified onto this detector by
C31]. Spearman rho between grade and agreement +0.565 (one-sided p < 0.0001).

| Grade | Records | Gate agreement |
|---|---|---|
| Y1 textbook | 9 | 0.89 |
| Y2 clearly diagnosable | 35 | 0.26 |
| P1 / P2 partial | 1 / 5 | 0.00 |
| N1 not diagnosable | 10 | 0.00 |

No fault record received a wrong family (all 43 disagreements are abstentions), and none of the 4 normal records was
flagged. Caveat that travels with this result: this is a second run; the first (M4) exposed a detector defect on the same 64
records, and the revisions that followed were fixed by synthetic tests before this run, but the records are not fresh.
