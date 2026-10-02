#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
. kaggle/lock.sh queue_coauthor_bistw_g2
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
U=rhrhrhrhrh
. kaggle/lib_run.sh
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
[ -f runs/.synced_coauthor_bistw ] || { python -u kaggle/sync_runner.py physgate-m0-code && touch runs/.synced_coauthor_bistw && sleep 300; }
run k10_g2 physgate-m0-code physgate-k10-g2
# C93: BIST-W fold B cut; co-author also takes g3 after g2 (primary attaches if it is already running)
[ -f runs/.synced_coauthor_g3 ] || { mkdir -p runs/_stage/physgate-k10-g3; cp -n data/k10/g3/*.npz runs/_stage/physgate-k10-g3/; python -u kaggle/sync_runner.py physgate-k10-g3 && touch runs/.synced_coauthor_g3 && sleep 900; }
until [ "$(date -u +%Y%m%d%H)" -ge 2026091900 ]; do sleep 600; done   # co-author quota resets with the week
run k10_g3 physgate-m0-code physgate-k10-g3
echo "$(date) coauthor BIST-W + g2 done"
