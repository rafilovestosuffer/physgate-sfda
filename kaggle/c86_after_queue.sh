#!/usr/bin/env bash
# After coauthor_queue.sh finishes: sync the updated code dataset to rhrhrhrhrh, then run C86 BIST kernels (both folds).
set -u
cd "$(dirname "$0")/.."
while pgrep -f coauthor_queue.sh >/dev/null 2>&1 || ps -ef | grep -v grep | grep -q coauthor_queue.sh; do sleep 120; done
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
python -u kaggle/sync_runner.py
sleep 240
for k in c86_bist_FA c86_bist_FB; do
  n=physgate-$(echo $k | tr 'A-Z_' 'a-z-')
  python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n --dataset rhrhrhrhrh/physgate-m0-code --dataset rhrhrhrhrh/physgate-m1-data --timeout-s 30600 || { echo "push failed $n"; continue; }
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  python -u kaggle/pull.py --name $n
done
echo "$(date) C86 queue done"
