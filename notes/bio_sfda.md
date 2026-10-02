# notes/bio_sfda.md — Bio-SFDA (Yoon, Lee, Park, Park & Jeong 2026)

**Status: [VERIFIED — FULL TEXT READ]** 2026-09-13, from the publisher PDF supplied by the researcher
(20 pp., CC BY-NC-ND 4.0). Supersedes the earlier abstract-only note.

Yoon T, Lee J, Park J, Park B, Jeong J. *Results in Engineering* 30:111105 (2026).
doi:10.1016/j.rineng.2026.111105. Received 15 Nov 2025, accepted 16 May 2026. Sungkyunkwan University.

Rule for this file: facts about the text, with section/table references. **No inference about intent.**
In the manuscript, only items marked `[cite]` may be stated, neutrally, in Related Work / Discussion.

---

## 1. Mechanism (answers Session-0 checklist items 1–2)

- **EAGLE (§4.2, Eq. 4.8, Fig. 6).** Four ROIs (BPFO, BPFI, BSF, impulse band) masked on the **STFT
  magnitude** of the measured window. Per ROI: band energy, envelope-peak count, energy ratio,
  kurtosis, SNR_ROI → z-scored, winsorised → a band is active if any feature exceeds a per-band
  threshold. Weight `w_e = clip(α0 + α1·SNR_ROI + α2·mean(bits), 0.5, 0.95)`; pseudo-label used iff
  teacher confidence `s ≥ τ_s` **and** `w_e ≥ τ_w`; loss weight `w_i = clip(w_e·s, ε, 1)`. `[cite]`
- **Thresholds** are initialised "offline from source-like data and bearing knowledge" and then
  **rescaled online so band-activation rates stay within a conservative range** (§4.2). `[cite]`
- **No null distribution, no false-alarm rate, no significance level** appears anywhere in the text.
  The gate is a **frequency-position rule with adaptive thresholds**. `[cite]` — this is now a
  verified absence (full text), not the struck inference of the earlier note.
- Characteristic frequencies use **BSF**, not 2×BSF (Eq. 4.7). No slip model. No DRS / pre-whitening.
  §4.2 states that because gating uses relative energy, the method "tolerates moderate parameter errors". `[cite]`
- **SPIDER (§4.3, Eq. 4.12–4.20)** takes Acc, macro-F1, mAP, Loss and ECE trends as inputs and moves the
  learning rate, momentum, augmentation and the acceptance thresholds. The paper does not state how
  Acc/F1/mAP/ECE are computed on an unlabelled target stream. `[cite as an open question, no more]`

**Consequence for H7.** "EAGLE-style rule" is now specifiable from the text: ROI band-energy / SNR
predicates at BPFO/BPFI/BSF on an STFT, thresholds set so activation rate is bounded. Our
reimplementation must (i) use BSF as they do, (ii) state that it is a reimplementation, (iii) not use
SPIDER (label-dependent inputs unspecified).

## 2. Data, label space, windows, splits (checklist items 3–6)

- §5.2: "All datasets have four classes: Normal, Inner, Outer, Ball." — applied to PU. **Paderborn has
  no ball/rolling-element damage class** (our `configs/datasets.yaml`; PU has inner, outer and
  combined inner+outer only). Which PU bearings/files were used is **not stated**. `[cite]`
- Table 2 gives fault sizes 0.007–0.021 **mm** (CWRU's sizes are in inches) as the class schema. `[cite]`
- **Window length for the reported experiments is not stated.** Table A.1 lists L = 4096 @ 12.8 kHz
  and 8192 @ 25.6 kHz for "Factory line A/B", which match neither CWRU (12/48 kHz) nor PU (64 kHz). `[cite]`
- **Split procedure is not stated for the experiments.** Appendix A.3 gives a generic leakage policy
  ("device/session disjointness") and an audit checklist, not a record of what was done. (Item 6,
  artificial-only PU: **unanswerable from the text**.)
- Data availability: "on request". No code or repository link. `[cite]`

## 3. Numbers, and internal consistency (checked by arithmetic)

| Check | Text | Finding |
|---|---|---|
| Table 4 SDALR† 96.8 on CWRU→PU, "literature-reported" | SDALR's 96.78 is the mean over PU **A1↔A2↔A3 within-PU** tasks (our M0 target) | the number is from a different task `[cite]` |
| Table 8 caption | F1/mAP/NLL "are reconstructed to be consistent with those Acc values" | stated in the caption `[cite]` |
| Table 8 vs Table 9 | incremental full model 15.0 % acc; complete model 99.0 % | not reconciled in text |
| Table 14 per-class F1 (Bio-SFDA) 96.1 / 95.2 / 92.0 / 94.5 | mean = 94.45 | Table 4 macro-F1 0.985 |
| Table 13 class separability | Bio-SFDA 0.136 vs source-only 1.88 | text: "strongest class separability" |
| Table 12 best cell | 95.4 % | Table 4: 99.0 % at the same default |
| Fig. 9 caption | "eight cases … five inner, one outer" | 6 enumerated |
| Appendix A.1, A.2, A.4 | "replace each filename…", "Replace the numbers with your measured values" | template text in the published appendix |

## 4. Decision (discharges the Session-0 gate)

- **Gate question: bearing-wise split OR FAR control?** Neither is reported. **No re-scope needed.**
- **Bio-SFDA is not a reproducible baseline** (no code, data on request, task definition unrecoverable:
  a ball class on PU). We therefore **do not reimplement Bio-SFDA** and **do not compare against its
  99.0 %**. It is cited (a) as the published instance of physics-guided pseudo-label gating in SFDA
  (TAKEN row), and (b) for its gate *mechanism*, which H7's "EAGLE-style rule" reimplements from §4.2.
- The Introduction does **not** use 99.0 % as a motivating number (C20 already withdrew the tension;
  this closes it). Related Work states the mechanism delta only: a thresholded band rule with adaptive
  activation rate versus a record-level test with a stated null and measured realised FAR.
- **Tone rule:** §3 table items are for our own risk assessment. At most one neutral sentence in the
  manuscript ("the task definition applies a ball class to Paderborn, which has none, and the split is
  not reported, so we do not compare numerically"). No further commentary.
