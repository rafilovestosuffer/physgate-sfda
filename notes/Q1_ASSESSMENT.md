# Q1 readiness assessment — 2026-09-15 (MSSP primary, C67)

## Scoop check (this date)
Searches for bearing-wise / leakage-safe evaluation of SFDA and for physics-gate safety on real healthy records returned no
new competitor. Closest remains Vieira et al. (MSSP 2026): supervised, single test bench, SFDA explicitly out of scope.

## What an MSSP reviewer will find convincing (we have it)
| Element | Evidence | Strength |
|---|---|---|
| Large, clean, significant effect | M1: −36.9 pp, Wilcoxon p = 0.0002, paired design isolating bearing overlap | strong |
| Mechanism, not just a number | per-bearing label purity 1.000 from saved predictions; figure | strong, rare in this literature |
| Reproduction before critique | SDALR reproduced on JNU and PU within seed variability | strong |
| Signal-processing substance (MSSP scope) | gate safety on 480 real healthy records; full ROC; slip–lock proposition; per-manufacturer PU geometry; UORED speed; CWRU cross-end contamination | good |
| Honest negatives | H6, H7, C77–C79, C78 control reported | good for credibility |
| Pre-registration and traceability | 84-entry change log, ledger, artifacts | differentiator; present as supplementary |

## Weaknesses a reviewer will raise, and the response
| Risk | Severity | Response |
|---|---|---|
| **One SFDA method** | high | Source-only already collapses 93.3 → 54.0, so the effect lives in the source model, not the adaptation algorithm; **add SHOT (C85)** to show it for a second, canonical method |
| One dataset for the paired leakage design | medium | PU is the only public set with enough physical bearings per class and multiple conditions; UORED (1 condition), CWRU (1 healthy bearing), HUST (geometry blocked), JNU (1 bearing per class) cannot host the design — state explicitly |
| Gating gains modest and seed-sensitive | medium | C83 three-seed decision; report OGC honestly (single-seed 0.19–0.30); gates are not the headline |
| "Not cross-machine" | medium | title and text say cross-condition, cross-bearing; do not overclaim |
| Novelty of the slip proposition is modest | low–medium | stated as a proposition with Smith & Randall credited; not in the title |
| Length / focus | medium | cut to three contributions; move dataset hygiene details and change log to supplementary |
| Bio-SFDA critique tone | reputational | mechanism-only comparison; offer authors right of reply before submission (human) |

## Verdict
**Realistic Q1 candidate for MSSP, conditional on:** (1) C83 completing, (2) a second SFDA method (C85), (3) tight writing that
leads with M1 + mechanism and treats gating as a secondary, measured question. Without (2) the paper is still publishable but a
"single method" rejection risk is real. Fallback venues if MSSP declines: *Measurement*, *Reliability Engineering & System
Safety* (reframed around reliability of automated diagnosis), *IEEE TIM*.

## Necessary steps, in order
1. C83 seeds (running / after quota reset).
2. C85 SHOT on the M1 paired design (≈ 2–3 GPU-h, next quota week).
3. Figures: M1 + purity (done), ROC (done), 6203 lock (done), gating-in-SFDA (after C83).
4. Convert references to Elsevier style; supplementary change-log table.
5. Author actions: right-of-reply email to Bio-SFDA authors; confirm authorship/CRediT; final read.
6. Preprint (arXiv / SSRN) by 2026-10-18; MSSP submission after C85.
