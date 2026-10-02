# notes/POSITIONING.md — Rev 6 (2026-09-13)

Supersedes the Session-0 verdict. Claim order per C39. Every row names its nearest neighbour and delta (C50).

## 1. Claims and their nearest neighbours

| # | Claim | Nearest published neighbour | One-sentence delta | Evidence status |
|---|---|---|---|---|
| 1 | Evaluation of physics gating of SFDA pseudo-labels by realised false acceptance on real healthy bearings (C65) | **Bio-SFDA / EAGLE** (gating mechanism); **PCTL** (PCV rule); **Borghesani 2013** (statistical SES test) | nobody has measured, on real healthy bearings and leakage-safe, which gate designs are safe; our comb gate is one arm, not the winner | **Measured (H7):** PCV-style SES rule P 0.994 / FA 1/480; comb gate 0.955 / 9/480; EAGLE-style raw-STFT rule FA 214/480. Engages ~6/23 PU fault bearings. M2/M3 pending. |
| 2 | Gate validated against Smith & Randall per-record grades under shift | **`predictive-maintenance-mcp`** + Appl. Sci. 2026 | theirs: rule-based, in-domain, frequency detection/ranking; ours: statistical gate, diagnosability-stratified precision/recall, used under domain shift | **M4b measured** on CWRU (ρ = +0.565; Y1 0.89 … N1 0). **UORED (descriptive, speed-conditional, C70):** bearing-level engagement inner 4/5 > outer 3/5 > ball 0/5 (corrected from 5/5, 2026-09-13) (logged arm) — the same difficulty ordering expert graders report, on a dataset they never graded; n = 5 bearings per class, stated as consistent with, not proof of, claim 2. Under-shift part pending (M5). |
| 3 | First leakage-safe evaluation of SFDA for bearings | **Vieira et al. MSSP 2026** (methodology); **He et al. EAAI 2026** (source-free cross-machine, no leakage analysis in abstract) | Vieira restrict themselves to a single test bench; no SFDA paper found that splits bearing-wise | M0-JNU reproduced; M0-PU and M1 running. |

## 2. The representation — NOT a contribution (C66); kept as ablation rungs

| Neighbour | Delta |
|---|---|
| Jeong et al. 2025 — order spectrum (speed-only, raw FFT) + TTT; order step carries 0.23 → 0.46 F1 | we add geometry normalisation, DRS + squared envelope, sideband and shaft channels. **H4 tests whether that addition matters; L3 first (C38).** |
| Matania et al. MSSP 2025 — **code read**: order SES max within ±2 % of k·{BPFO,BPFI,BSF}, k ≤ 10 | **same idea as our L4 — TAKEN (C66)**; only sidebands (H5) and DRS remain, tested not claimed |
| Rong & Lee SHM 2025 — time-signal down-sampling to centre a data-derived spectral peak; labelled fine-tuning | ours: kinematic harmonic indices, no target labels |
| Sadoughi & Hu; SFRF | fault-frequency receptive fields/filters exist; ours is a coordinate system, not a filter bank |

The representation is not a paper claim (C66); L4m/L4/L5/L3 are reported as ablations only.

## 3. Findings that already exist and survive the audit

1. **The 6203 shaft-harmonic lock — now manufacturer-dependent on Paderborn (C35).** FAG 6203 (Pd 28.55):
   BPFO +1.81 % of 3·f_r, BPFB −0.17 % of 4·f_r, BPFI −1.09 % of 5·f_r — all collide at s_max 0.02.
   IBU/MTK 6203 (Pd 29.05): BPFO +2.35 %, BPFI −1.41 % (shaft harmonic just outside the one-sided slip
   window, < 1 native bin at 3 s), BPFB +1.78 % still collides. **Wording (Smith & Randall observed the
   lock in 2015): ours is the consequence for automated gating, quantified per geometry — not the
   observation.** And a sharper, checkable point: *papers that use one "6203" geometry for Paderborn use a
   geometry that matches none of its three manufacturers exactly.*
2. **Resolution feasibility** (§0.3): 2048-sample PU windows are 0.8 revolutions; fault anchors share
   native bins with shaft harmonics. PCTL uses 1024; JNU literature uses 1024 (Sun & Gao 2024).
3. **H6 NOT SUPPORTED (both runs; C35 re-run raw 0.742, cepstrum 0.955, healthy FA 9/480).** Inner→outer
   confusion is essentially one FAG bearing (KI16: 57/80 raw → 7/80 pre-whitened) — a case study, not a population
   claim (C56). **H7 NOT SUPPORTED.** **B6a: CWRU cross-end contamination measurable** (13/52, cluster CI 11–40 %).

## 4. What we will not say

- Anything implying Bio-SFDA's number is wrong or leaked. We say only that its task definition and split
  are not reproducible from the text, so we do not compare numerically (C49).
- "Physical priors are rarely studied" (C41). "A leakage-safe protocol" as our novelty (C39). "A novel
  CFAR/statistical detector" (C40).
