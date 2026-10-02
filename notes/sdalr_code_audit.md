# notes/sdalr_code_audit.md — audit of the released SDALR implementation

**Repository:** `github.com/BdLab405/SDALR`, commit `fb9c379` ("Update README.md"), cloned 2026-09-13
to `third_party/SDALR/` (gitignored). README self-describes as the "Official implementation" of
*Both Reliable and Unreliable Predictions Matter* (Neurocomputing 657:131661, 2025).

**Licence: NONE.** No LICENSE file ⇒ all rights reserved by default. We may run it privately to
reproduce the published table; we may **not** redistribute it. Our public release fetches it by
commit hash instead of bundling it.

> Tone rule for the manuscript: state these as **properties of the released code**, with file and
> line references, never as claims about the authors' intent. Whether the published table was
> produced exactly this way is for the authors to confirm; we report what the released code does
> and what difference it makes when measured.

---

## A1 — Adapted checkpoint is selected using TARGET LABELS  ⚠ integrity-relevant

`tar_adaptation_RES_PU.py` (identical structure in the JNU script):

- **line 619**: `data_loaders = tools.args_data_load(args, {"train": 1, "val": 1, "test": 1}, separate=False)`
  With `separate=False` and ratio 1, `train`, `val` and `test` are **each the entire labelled target
  domain** (`tools.py` lines 389–394).
- **lines 329–356**, under the comment `## 正确率计算并且保存最佳模型` ("compute accuracy and save the
  best model"): at every `interval` (default 4 evaluations over 20 epochs) it computes
  `tools.cal_acc(dset_loaders["val"], networks)` — accuracy against **target labels** — and saves the
  checkpoint only `if acc_t_te > acc_init`.
- **lines 358–366**: at `max_iter` it reloads that best checkpoint and reports
  `tools.cal_acc(dset_loaders["test"], networks)` — the **same labelled target set**.

**Consequence:** the reported adapted accuracy is the maximum over checkpoints of target accuracy,
with the maximum chosen using the target labels that a source-free, unsupervised setting assumes are
unavailable. This is an oracle model-selection step.

**What we will measure (M0):** each task run twice from the same source model and seed —
1. `as_released` — oracle selection, to test whether we reproduce the published table;
2. `final_checkpoint` — the last iterate, no target labels touched.
The per-task gap is reported. It is a *measured* quantity, not an assertion.

## A2 — "Accuracy" is balanced accuracy

`tools.py` line 411–415, `cal_acc_matrix`: `overall_acc = round(per_class_acc.mean(), 2)`.
The reported metric is the **mean per-class recall** (balanced accuracy). With SDALR's 2000
samples/class it coincides numerically with plain accuracy; under any class imbalance it does not.
Our ledger records both.

## A3 — Domain index ≠ paper label  ⚠ reproduction trap

`src_pretrain_RES_PU.py` line 232: `domain_names = ['N15_M01_F10', 'N15_M07_F10', 'N15_M07_F04']`.
Paper Table 1: **A1 = N15_M01_F10, A2 = N15_M07_F04, A3 = N15_M07_F10.**
So code index 1 is paper **A3** and code index 2 is paper **A2**. Comparing reproduced numbers to the
paper table by index silently swaps four of the six tasks. Our runner maps by condition string only.

## A4 — Hyperparameters in the released scripts vs the paper

| | paper | `choose_s_t_PU.sh` / argparse default |
|---|---|---|
| target lr | 5e-4 | 5e-4 ✔ |
| target epochs | 20 | 20 ✔ |
| batch | 64 | 64 ✔ |
| source lr / epochs | 7e-3 / 10 | 7e-3 / 10 ✔ |
| reliability threshold ∂ | **0.6** (Figs 9–10 discussion) | `--threshold 0.4` |
| β / K | β = 0.6 | `--K 0.6` (comment: "近邻样本数量", number of neighbours) |
| feature-extractor lr multiplier | not stated | `lr_f = [0.1, 0.1, 1]` |
| seed | not stated | **single seed 2024** |

The ∂ discrepancy (0.6 in the paper, 0.4 in the script) must be resolved by running the **script as
released**, since that is what "reproduce the published code" means; the paper value is logged as a
known discrepancy. Our 5-seed protocol will also report seed variance that a single seed conceals.

## A5 — Source split and normalisation

- Source domain split **0.7 / 0.1 / 0.2** train/val/test, random at the *window* level
  (`src_pretrain_RES_PU.py` line 318). Windows from one continuous recording land in all three.
- z-score normalisation statistics computed from each split's full data array
  (`tools.py` line 401, `DataPreprocessor(..., normalized_choose="z_score")`).

## A6 — Preprocessed data is not independently available

README points to Baidu Pan archives `PU_1d_8c_2048` and `JNU_1d_2048_2000` (text files, one window per
file). We rebuild the windowing from the raw public data. **This is a reproduction risk**: SDALR's exact
window start positions, stride and file-level sampling are unrecorded. If M0 misses by > 2 pp, this is
the first suspect, before any conclusion about the method.
