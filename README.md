# physgate-sfda

Code, protocol, run ledger and retained artifacts for:

> M. R. Rahman, *Bearing leakage survives source-free adaptation: a bearing-wise evaluation of SDALR and SHOT with
> physics-gated pseudo-labels*. Submitted to Mechanical Systems and Signal Processing, 2026.

## Contents

| Path | What it holds |
|---|---|
| `PROTOCOL.md` | Pre-specified hypotheses and decision rules. Change-log entries C1-C112 record what was fixed before each run and what changed afterwards. |
| `results/ledger/*.csv` | Append-only run ledger: one row per run and task, with kernel, commit and artifact path. |
| `results/` | Retained artifacts and per-experiment notes. `c105`-`c112` hold the final-revision analyses. |
| `paper/tex/` | Manuscript source. `paper/make_tables.py` regenerates every table from `results/`, `paper/figures/build_figures.py` every figure, and `paper/check_manuscript.py` checks headline numbers against their sources. |
| `paper/supplementary_S4_traceability.md` | Number-to-artifact map and script checksums. |
| `experiments/`, `physics/`, `runners/`, `kaggle/kernels/` | Analysis, gate, adaptation-runner and compute-job code. |

## Reproducing

1. Python 3.11; `pip install -r requirements.txt`.
2. Raw data are not redistributed. Download them from their owners:
   - Paderborn (KAt-DataCenter, Universität Paderborn)
   - HUST bearing (Mendeley Data, doi:10.17632/cbv7jyx4p9)
   - CWRU
   - UORED-VAFCLS
   - JNU

   Place them under `data/` as listed in `DATA_MANIFEST.csv`.
3. SDALR is not included, because its repository carries no licence. Run `bash scripts/fetch_sdalr.sh` to fetch the exact
   commit used in the paper.
4. Analyses of retained artifacts run locally: `python paper/make_tables.py`, `python paper/check_manuscript.py`, and the
   scripts in `experiments/`. The adaptation runs used Kaggle Tesla T4 kernels (`kaggle/kernels/`).

## Notes

`CLAUDE.md`, `PLAN.md` and `notes/` are the working instructions and notes of the project. An AI coding assistant
(Claude, Anthropic) executed analyses and compute jobs under these instructions, as disclosed in the paper.

## Licence

Code: MIT (`LICENSE`). Results, ledger and documentation: CC BY 4.0.
