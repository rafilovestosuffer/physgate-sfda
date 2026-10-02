#!/usr/bin/env bash
# After coauthor_queue.sh (C83 seed 1, C85 SHOT): sync code + C88 data to rhrhrhrhrh, run C87 N1 probe, then C88 groups g1, g2.
# Groups g3, g4 run on the primary account after the weekly reset (kaggle/k10_primary_queue.sh).
set -u
cd "$(dirname "$0")/.."
while ps -ef | grep -v grep | grep -q "coauthor_queue.sh"; do sleep 120; done
while ps -ef | grep -v grep | grep -q "make_k10.py"; do sleep 60; done
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
U=rhrhrhrhrh
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
for g in g1 g2; do mkdir -p runs/_stage/physgate-k10-$g; cp -n data/k10/$g/*.npz runs/_stage/physgate-k10-$g/; done
python -u kaggle/sync_runner.py physgate-m0-code physgate-k10-g1 physgate-k10-g2
sleep 600   # large dataset versions need processing time
run() {  # kernel-file name, datasets...
  local k=$1; shift; local n=physgate-$(echo $k | tr 'A-Z_' 'a-z-'); local ds=()
  for d in "$@"; do ds+=(--dataset "$U/$d"); done
  python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n "${ds[@]}" --timeout-s 30600 || { echo "push failed $n"; return; }
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  python -u kaggle/pull.py --name $n
}
run n1_probe physgate-m0-code physgate-m1-data
run k10_g1 physgate-m0-code physgate-k10-g1
run k10_g2 physgate-m0-code physgate-k10-g2
echo "$(date) N1 + K10 g1/g2 queue done"
