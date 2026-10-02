# notes/pctl.md — PCTL (Jiao, Zhang & Cao 2026)

**Status: [VERIFIED — full PDF read]** via ein.org.pl open access (CC BY), extracted with PyMuPDF,
18 pages / 62,844 chars, 2026-09-13.

Jiao X, Zhang J, Cao J. "A Physics-Guided Transfer Learning Framework with Consistency Verification
for Cross-Domain Bearing Fault Diagnosis." *Eksploatacja i Niezawodnosc – Maintenance and
Reliability* 2026; 28(2):211797. doi:10.17531/ein/211797. Xinjiang University.

> The earlier verification report listed this as unconfirmed ("full PDF robots-disallowed"). It was
> obtainable by a different route. All three claims below are now verbatim-sourced.

---

## 1. It validates its OWN RECONSTRUCTION, not the measured signal — verbatim

> **Algorithm 1 Physics Consistency Verification (PCV) Module**
> **Input:** Predicted class `c_pred`, **predicted envelope spectrum `s_pred = P_phy(E(x_t))`**,
> target machine parameters (e.g. bearing geometry, rotation speed `f_r`).
> **Output:** Physics Consistency Score `S_phys`.
> ```
> 1: if c_pred is 'Normal' then
> 3:   S_phys ← 1 − mean_energy_at_fault_freqs(s_pred)
> 5: else
> 6:   f_char ← calculate_theoretical_freq(c_pred, f_r)
> 9:   for h in {1,2,3} do            // Check first 3 harmonics
> 10:    peak_energy ← find_peak_energy_in_window(s_pred, h·f_char)
> 14:  S_phys ← mean(harmonic_scores)
> 16: return S_phys  // A score between 0 and 1
> ```

`P_phy` is an MLP trained to reconstruct the envelope spectrum from the encoded feature, with
`L_phy = ||P_phy(E(x_s)) − s_env(x_s)||²`.

**State the observation precisely and without overreach.** The referee scores a spectrum the model
itself produced. This is a *structural* property of their design, not an error, and they never claim
otherwise — but it means the consistency score is not an independent measurement of the signal.
Our gate reads the measured SES only. **Phrase as a difference in what is being validated, never as
an accusation.**

## 2. It is NOT source-free — verbatim

> "Stage 1: Pre-training. This stage takes source domain data (Source Data, `D_s`) and unlabeled
> target domain data (Target Data, `D_t`) as input."

Domain-adversarial training with a gradient reversal layer between encoder and domain discriminator.

## 3. It REQUIRES LABELLED TARGET DATA — verbatim

> "This stage utilizes a small set of labeled target domain data (Labeled Target Data)."
> "During the fine-tuning stage, we use a small, labeled subset of the target domain to update the
> model parameters."

So the setting is source+target **semi-supervised** fine-tuning, strictly weaker than our
source-free, fully-unlabelled-target setting. **This is the cleanest differentiator we have and it
is fully quotable.**

## 4. Other verified specifics

- Encoder: ResNet1D (4 residual blocks, 128-d output) **+ Bi-LSTM (hidden 128)** + attention fusion.
- Losses: `L_pretrain = L_phy + λ_dom·L_dom + λ_cond·L_cond`;
  `L_finetune = L_class + λ_consistency·L_consistency`, with
  `L_consistency = ||C_conf(E(x_t)) − S_phys||²` — the PCV score supervises a **confidence
  predictor**, and the PCV module *"does not participate in gradient backpropagation."*
- Datasets: **CWRU, Paderborn, IEEE PHM 2012** (gearbox). Tasks T1 CWRU→PU, T2 PU→CWRU,
  T3 PHM2012→CWRU, T4 PHM2012→PU.
- Preprocessing: **1024-point samples, overlapping sampling, z-score.** ← At 1024 points the
  resolution problem of PLAN §0.3 is *worse* than at 2048. Their `find_peak_energy_in_window` on a
  1024-point envelope spectrum has essentially no bins inside a physically meaningful window. Worth
  one careful sentence in Related Work, framed as a resolution observation, not a dismissal.
- Pre-training: Adam, lr 1e-3, batch 64, 100 epochs, λ_dom 0.1, λ_cond 0.5.
  Fine-tuning: encoder lr 1e-5, heads lr 1e-4, batch 32, 50 epochs, λ_consistency 0.2.
- No band selection (no kurtogram/IESFOgram), no discrete/random separation, no slip window
  specified, no false-alarm control, no null distribution.

## 5. Delta to state in Related Work

PCTL: source+target, needs labelled target, heuristic [0,1] score on a reconstructed spectrum,
supervises a confidence head.
Ours: source-free, no target labels, calibrated test with controlled false-alarm rate on the
measured SES, gates the pseudo-label loss directly.
