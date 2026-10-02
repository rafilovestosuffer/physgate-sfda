# C103 - Does pretraining inside the arm's own process explain the cross-job gap?

Kernel `physgate-c103-pretrain-state` (primary account, Tesla T4), `kaggle/kernels/c103_pretrain_state.py`.
Artifact: `results/artifacts/physgate-c103-pretrain-state/` (both arm JSONs, per-task adaptation logs, kernel log).
Ledger: 12 rows `physgate-c103-pretrain-state-...-pretrain_in_process` / `...-skip_pretrain` (rafiurrahman01.csv).

## Result

Fold A source, fold B target, `final_checkpoint`, gate `none`, seed 2024.

| Task | Arm 1: pretrain in process | Arm 2: `--skip-pretrain` (arm 1's checkpoint) | Difference |
|---|---|---|---|
| A1->A3 | 76.13 | 76.13 | 0.00 |
| A1->A2 | 76.98 | 76.98 | 0.00 |
| A3->A1 | 61.12 | 61.12 | 0.00 |
| A3->A2 | 57.72 | 57.72 | 0.00 |
| A2->A1 | 34.07 | 34.07 | 0.00 |
| A2->A3 | 34.55 | 34.55 | 0.00 |
| **Fold mean** | **56.762** | **56.762** | **+0.000** |

Both arms genuinely ran: arm 1 took 2343 s (pretraining plus six adaptations), arm 2 took 2058 s (six adaptations
only); the kernel deletes arm 1's result JSON before arm 2 starts, so arm 2 cannot resume from it. Both arms also equal the
original gating job and its two repeats to the last decimal (C102, now five executions of this configuration).

## Decision (pre-registered rule)

Difference < 0.1 pp: **the pretrain-in-process explanation is REJECTED.** The pre-registered consequence was that the
gap is reported as unexplained, which is a stronger caveat than the current one. The existing rule stands: arms are never
crossed between jobs.

## Post-hoc diagnosis (code inspection plus one CPU check; NOT isolated by a run)

The fold job that produced the headline leaky and clean arms (`physgate-m1-f*`, 2026-09-13) ran runner revision
`2e02bc3`. Every execution that gives 56.762 ran a revision at or after `d9ad845` (2026-09-14), which added the C81 gate
hook. Fold A clean, same seed: 58.36 in the fold job, 56.76 in every later execution.

Revision `d9ad845` wraps SDALR's `tools.cal_acc` in `recording_cal_acc`, which iterates the evaluation loader once more,
to dump per-window predictions, before calling the original. The wrapper is active for every gate arm including `none`.
The networks are in `eval()` at that point, so BatchNorm statistics are untouched and the extra pass cannot change the
model directly. Creating a PyTorch DataLoader iterator, however, draws a base seed from the global torch generator even
when `shuffle=False`. Checked on CPU (torch 2.14): with `torch.manual_seed(2024)`, one extra unshuffled pass over a
DataLoader changes the next `torch.rand` draw from 0.9718 to 0.1669. Every subsequent random operation in adaptation
(batch shuffling, mixing) therefore follows a different trajectory, as a change of seed would.

This mechanism accounts for everything measured: executions within one revision are bit-identical (C102), pretraining state
is irrelevant (this result), the wrapper first runs at the pre-update evaluation, before any training step, and the two revisions differ by an amount inside the between-seed range of the ungated fold
mean (fold A 56.47-59.69 over seeds 0, 1, 2024, range 3.2 pp; the cross-job gap is 1.6 pp). It was identified after the
C103 rule was evaluated and has not been isolated by a controlled run (the same revision with the wrapper disabled). The
manuscript states it as the probable cause identified from the code, not as a measured cause.

## What changes

- Manuscript Section 4: "non-deterministic GPU reductions" is gone (C102). The pretraining-state explanation is tested and
  rejected (C103). The probable cause is the random-stream shift from the evaluation wrapper, stated as a code-level
  diagnosis, with the size of the gap set against the between-seed range.
- Section 6.2: the sentence calling the 56.0 vs 56.8 difference "the run-to-run spread" is withdrawn. It is a
  difference between two code revisions that amounts to a change of random trajectory.
- No headline number changes. The leaky-clean contrast and the gated-ungated contrasts were each computed within one job,
  so within one revision.
