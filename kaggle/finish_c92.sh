#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
( PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh python -u kaggle/poll.py --name physgate-run-c92-rf-g3 --interval 300 --timeout 43000
  for a in 1 2 3 4; do PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh python -u kaggle/pull.py --name physgate-run-c92-rf-g3
    find results/artifacts/physgate-run-c92-rf-g3 -name "c92_result.json" | grep -q . && break; sleep 120; done ) &
( python -u kaggle/poll.py --name physgate-run-c92-rf-g4 --interval 300 --timeout 43000
  for a in 1 2 3 4; do python -u kaggle/pull.py --name physgate-run-c92-rf-g4
    find results/artifacts/physgate-run-c92-rf-g4 -name "c92_result.json" | grep -q . && break; sleep 120; done ) &
wait
echo "$(date) c92 g3+g4 collected"
