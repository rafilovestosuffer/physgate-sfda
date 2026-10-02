# Project: Bearing-wise evaluation of SFDA on a single rig (leakage, memorisation, ceiling of physics-gated pseudo-labels)

Scope is cross-condition transfer with bearing-disjoint targets on Paderborn. NOT cross-machine: never write that.

Read `PROTOCOL.md` before any task. It is the contract. `PLAN.md` is the execution plan.
`notes/POSITIONING.md` records what survived contact with the literature.

## Current milestone
**Manuscript final pending author details (2026-09-29).** Source of truth: `paper/tex/` (LaTeX, elsarticle); the markdown
draft `paper/manuscript.md` is SUPERSEDED. All experiments are complete: C88 ten splits, C94 HUST replication (median
33.5 pp), C100 SHOT on ten splits (median 21.7 pp, 10/10, p = 0.001), C101 RF ten splits, C102 A/A floor 0.00 pp
(11 pairs, 66 tasks), C103 pretrain-state explanation REJECTED (cross-job gap diagnosed post-hoc as an RNG-stream shift
from the gate-hook eval wrapper; not isolated by a run). BH family final stage in `results/c96/c96_family.json`; tables
read it, and `paper/check_manuscript.py` fails on any p_BH that is not a member. Ledger 1246 rows, both accounts.
Round 4 (2026-09-29): C104 same-condition control run (median 29.7 pp, identity alone produces the collapse); title
shortened; BH family has 10 members with a BY column (HUST fails BY, 0.065, and is described as a directional
replication). Response to review has Parts A-D; Part C must be re-keyed to the third-round reviewer numbering.
Round 6 (2026-10-02, internal review in `paper/review_2026-10-02/`): reframed - the leak is in the source model (C105 source-only gap 35.1 pp), within-bearing contrast (C106), under-sampling not identity (C110 pre-registered, 45.9 -> 74.6 %), kinematic forest (C112), gate gain on certified windows only (C107), fold jobs used different source checkpoints (C103b), slip moved to Supplementary S5. Title changed; response Part F.
**Human-only items before submission:** data deposit DOI (MSSP requires it at submission), separate highlights file, declarations .docx; author list, affiliations, CRediT names, corresponding author (main.tex,
99_declarations.tex, cover_letter.md); suggested reviewers approved; repository DOI on acceptance.

## Non-negotiable rules
1. `[FROZEN]` items in PROTOCOL.md do not change. If a task seems to need it, STOP and ask.
2. Never estimate bearing geometry. Unverified bearings RAISE. Every number carries a `source:`.
3. **C19 — compute before you build.** Before implementing any component, compute its governing
   quantities (bins per window, separations, revolutions, sample counts) and assert they are workable.
   Two blockers in this project were invisible in prose and only surfaced in arithmetic.
4. Never train locally. All GPU work goes to Kaggle GPU; heavy CPU analysis (sweeps, data builds, multiprocessing) goes to Kaggle CPU kernels — the local PC overheats (2026-09-16). Local = editing, git, light scripts, push/poll queues.
5. `kaggle/push.py` rejects any accelerator other than `NvidiaTeslaT4`, in code. Never bypass it.
   P100 is sm_60 and fails at the first CUDA op. GPU sessions cap at 9 h; ~30 GPU-h/week.
6. Never `import kaggle` (PATH python is 3.11 without it). Shell out via `kaggle/_cli.py`.
7. Never read, print, log or commit `~/.kaggle/kaggle.json` beyond the `username` field.
8. No number enters the manuscript unless it traces to a row in `results/ledger/` with a retained
   artifact. Pending values are `null`, never placeholders that look real.
9. **Suspiciously good results are treated as failures** until leakage is ruled out.
10. Reporting that our method loses is authorised and expected.
11. BSF/BPFB are asserted against the closed-form formula, never a published table (C13).
12. The gate is per RECORD (C17) and is the frozen harmonic-comb test with a record-specific surrogate-order
    null and the >=2-line multiplicity rule (C30; CA-CFAR/C24 is superseded).
13. Kinematics resolve PER BEARING (C35) and, on JNU, per class (C45). A bearing designation is not a
    geometry: use the rig's own documentation, never another rig's entry with the same part number.
14. No novelty sentence without a named nearest neighbour and a one-sentence delta (C50).

## Environment
- Local: Windows + Git Bash, CPU only. `python` = 3.11. Kaggle CLI 2.2.2 under Python 3.13.
- Kaggle accounts: `rafiurrahman01` (primary, ~/.kaggle) and co-author `rhrhrhrhrh` (runner, ~/.kaggle_coauthor/access_token,
  select with `PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh`). All kernels and datasets PRIVATE. Never read tokens.
- Tests: `python -m pytest tests/ -q` (CPU, < 60 s).

## Workflow per experiment
1. C19 feasibility for the component.  2. Unit tests on CPU.  3. `kaggle/preflight.py`.
4. `kaggle/push.py`.  5. `kaggle/poll.py`.  6. `kaggle/pull.py` (artifact retained).
7. Append ledger row.  8. Evaluate the decision rule. PASS → commit. FAIL → `results/FAILURE_*.md`, stop.
