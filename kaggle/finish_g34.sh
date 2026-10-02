#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
( PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh python -u kaggle/poll.py --name physgate-run-k10-g3 --interval 300 --timeout 33000
  for a in 1 2 3 4 5 6; do PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh python -u kaggle/pull.py --name physgate-run-k10-g3
    find results/artifacts/physgate-run-k10-g3 -name "result_*.json" | grep -q . && break; sleep 120; done ) &
( python -u kaggle/poll.py --name physgate-run-k10-g4 --interval 300 --timeout 33000
  for a in 1 2 3 4 5 6; do python -u kaggle/pull.py --name physgate-run-k10-g4
    find results/artifacts/physgate-run-k10-g4 -name "result_*.json" | grep -q . && break; sleep 120; done ) &
wait
echo "$(date) g3+g4 collected"
