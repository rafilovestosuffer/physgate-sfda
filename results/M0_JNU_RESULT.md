# M0 — SDALR reproduction on JNU (Track R, published leaky protocol)

Kaggle T4, torch 2.10.0+cu128, seed 2024, SDALR commit fb9c379 run unmodified except the declared
I/O adapter and t-SNE stub (and, for `final_checkpoint`, the one-line selection patch). 6 tasks, 2048-sample
windows, 2000/class (87.8 % overlap for fault classes — see notes/data_findings.md).

| Task | Paper | Ours (as_released) | Diff | Source-only (ours) |
|---|---|---|---|---|
| B1→B2 | 99.98 | 99.86 | −0.12 | 99.93 |
| B1→B3 | 100.00 | 100.00 | 0.00 | 96.42 |
| B2→B1 | 96.41 | 95.26 | −1.15 | 92.65 |
| B2→B3 | 100.00 | 100.00 | 0.00 | 99.02 |
| B3→B1 | 94.71 | 93.19 | −1.52 | 73.41 |
| B3→B2 | 99.92 | 99.89 | −0.03 | 91.86 |
| **Mean** | **98.50** | **98.03** | −0.47 | 92.22 |

**Decision (guard: > 2 pp miss halts): REPRODUCED.** Largest per-task miss 1.52 pp.

## Model-selection audit (A1)

`final_checkpoint` gave **identical** numbers on all six tasks. Verified from the logs rather than assumed:
labelled-target accuracy increases monotonically to the final checkpoint in every task, so the oracle
selection had nothing to select. Both variants reproduce the same curves to two decimals (deterministic
runs). **On JNU, target-label checkpoint selection inflates nothing.** PU is the stronger test (8 classes,
harder shift).

## Observations to carry into the paper

- JNU speed transfer is nearly trivial before any adaptation: source-only is 91.9–99.9 % on five of six tasks.
  Adaptation's measurable contribution is concentrated in B3→B1 (73.4 → 93.2).
- On B1→B2 adaptation marginally lowers accuracy (pre-adaptation 99.88 → 99.86).
- The 1.15 and 1.52 pp misses are both on tasks INTO 600 rpm; SDALR's windowing is unrecorded (audit A6),
  and our evenly spaced starts are the likeliest source.
- Every JNU task places the same physical bearing on both sides (C25). These numbers are Track R context only.
