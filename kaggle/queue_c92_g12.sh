#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
n=physgate-run-c92-rf-g12
python -u kaggle/poll.py --name $n --interval 300 --timeout 43000
for a in 1 2 3 4 5 6; do python -u kaggle/pull.py --name $n; find results/artifacts/$n -name "c92_result.json" | grep -q . && break; sleep 120; done
echo "$(date) c92 g12 done"
