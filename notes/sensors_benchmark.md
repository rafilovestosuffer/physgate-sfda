# notes/sensors_benchmark.md — Sensors 2025, 25(14):4383

**Status: [VERIFIED — full text read]** via MDPI open access, 2026-09-13.

Jeong H, Kim S, Seo D, Kwon J. "Source-Free Domain Adaptation Framework for Rotary Machine Fault
Diagnosis." *Sensors* 2025, 25(14), 4383. doi:10.3390/s25144383. Inha University, Republic of Korea.
Received 2025-06-16, accepted 2025-07-10, published 2025-07-13.

---

## 1. THE SESSION-0 FINDING — our "central tension" as written is NOT supportable

PLAN.md §7 and the KICKOFF frame the paper around:

> "Bio-SFDA reports 99.0% on CWRU→PU. The honest four-dataset cross-machine benchmark reports
> F1 ≈ 0.47 on comparable shift. **Those two numbers cannot both describe the same problem.**"

**They can. They describe genuinely different problems.** Verified:

| | Bio-SFDA | Jeong et al. (this paper) |
|---|---|---|
| Datasets | CWRU → Paderborn | **VAT, DXAI, VBL-VA001, MaFaulDa** |
| Fault taxonomy | bearing element faults | **machine-level faults** |
| Classes | inner / outer / ball (+normal) | **{Normal, Misalignment, Unbalance, Bearing}** |
| Bearing granularity | inner vs outer vs ball distinguished | **all bearing faults merged into ONE class** |

Verbatim (§4.1.5): *"we integrated the data into five primary fault categories: normal,
misalignment, unbalance, and bearing. The bearing class merges BPFO, BPFI, and bearing cage-related
faults."* (The paper says "five" but lists four — an internal inconsistency in the source; the four
listed are the operative set.)

**None of CWRU / PU / JNU / HUST appears in this benchmark.** The four datasets are rotor-rig
datasets: VAT (KAIST, 680–2460 rpm), DXAI (UFSJ Brazil — normal/unbalance/misalignment/looseness),
VBL-VA001 (ITS Indonesia, fixed 3000 rpm, 20 kHz), MaFaulDa (UFRJ Brazil, ABVT trainer,
737–3686 rpm, 50 kHz, 5 s). Total 62,863 samples, X and Y motor axes.

**ACTION REQUIRED — rebuild the Introduction's framing device before writing.** See
`notes/POSITIONING.md`. The juxtaposition must be dropped as a *contradiction* and demoted to
*context*.

---

## 2. What DOES survive, and is citable

**(a) They independently motivate our leakage claim.** Verbatim (§4.1.5):
> *"To address the known issue of test–train leakage in condition-based maintenance studies,
> especially those relying on single-source datasets like CWRU, we constructed a benchmark that
> integrates four diverse public datasets."*

This is third-party support for Claim 1 from an author group with no stake in our argument. Cite it.

**(b) Honest cross-machine rotary diagnosis is genuinely hard.** F1 = 0.47, recall = 0.51 in the
target domain, and that is their *best* method, beating SVM/LR/RF/GB/KNN/1D-CNN/LSTM/Transformer.
Usable as context for "cross-machine numbers should be low", *not* as a same-task comparator.

**(c) Their order transform is speed-only — direct support for the KNEOS-HC gap.** Algorithm,
verbatim (§3.1 "Mechanically Informed Order Spectrum Preprocessing"):
```
X(f)      ← FFT(x(t))
f0        ← r̂/60                 ▹ Fundamental rotational frequency
o         ← f/f0                  ▹ Convert to order domain
X_order(o)← X(f)
X_log(o)  ← log scaling
```
Coverage: *"up to 10 times the fundamental rotational order (10×)"*. Stated purpose: *"Order
analysis normalizes the frequency axis based on the machine's rotational speed (RPM), aligning fault
features at consistent order indices regardless of operating speed."*

**This normalises speed, not geometry.** After their transform, BPFO still sits at 3.5848 for a 6205
and 3.0531 for a 6203 — different indices on different machines. A kernel trained on one still
sees the other's fault line displaced. **This is exactly our rung L3, and they report F1 0.47 with
it.** That is a documented, quantified reason why speed normalisation alone is insufficient
cross-machine, which is the precise gap KNEOS-HC addresses.

Note also: their 10× shaft-order ceiling would truncate our K=5 BPFO harmonics (5 × 3.05 = 15.3
orders) — a concrete design difference worth one sentence in Related Work.

---

## 3. Method and protocol details

- Framework: order-frequency preprocessing → U-Net variational autoencoder (reconstruction
  learning) → test-time training (TTT) for source-free adaptation.
- Classification is by comparing latent representations of input vs a **reference signal**, not
  direct softmax classification.
- Baselines: SVM, Logistic Regression, Random Forest, Gradient Boosting, KNN, 1D-CNN, LSTM, Transformer.
- Training: CrossEntropyLoss, Adam, lr 1e-3, dropout 0.3, batch 512, 200 epochs. ML hyperparameters
  grid-searched **on source-domain training data only** (a point in their favour).
- Five input representations compared, including time- and frequency-domain statistical features.
- Domain separation is **by dataset** (train on some datasets, test on others). Whether *bearings*
  recur within a dataset is not addressed — their leakage control is at dataset granularity, which
  is coarser than our bearing-wise requirement but stronger than condition-wise.

## 4. Open items

- Exact per-task source→target assignments and the full results table were not transcribed; not
  needed, since this paper is now context rather than a comparator.
- The "five categories / four listed" inconsistency should be quoted carefully if cited.
