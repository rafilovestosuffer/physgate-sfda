# Research data and code for "Bearing leakage survives source-free adaptation"

This archive is the project repository at the commit named in its file name. It contains every script, protocol entry,
ledger row and retained result artifact behind the numbers in the manuscript. Raw vibration data are not included. They
are public from their owners: Paderborn (KAt-DataCenter), HUST (Mendeley Data, doi:10.17632/cbv7jyx4p9), CWRU, UORED-VAFCLS
and JNU.

- `PROTOCOL.md` holds the pre-specified hypotheses and decision rules. Change-log entries C1-C112 record what was fixed
  before each run and what changed afterwards.
- `results/ledger/*.csv` is the append-only run ledger: one row per run and task, with kernel, commit and artifact path.
- `results/` holds the retained artifacts and per-experiment result notes. `results/c105`-`c112` are the round-6 analyses.
- `paper/supplementary_S4_traceability.md` maps every reported number to its artifact and gives script checksums.
- `paper/make_tables.py` regenerates every table from the artifacts; `paper/figures/build_figures.py` regenerates every
  figure; `paper/check_manuscript.py` checks headline numbers against their sources.
- `experiments/`, `physics/`, `runners/` and `kaggle/kernels/` contain the analysis, gate, adaptation-runner and compute-job
  code. SDALR itself is in `third_party/SDALR` under its authors' terms.

Light analyses run with Python 3.11 and `requirements.txt`. Adaptation runs used Kaggle Tesla T4 kernels.

How to deposit (authors): upload the zip to Zenodo (or a similar DOI-minting repository), then replace
"[dataset reference to be added at deposit]" in `paper/tex/sections/99_declarations.tex` with the DOI, and add a
`[dataset]` entry to `references.bib`.
