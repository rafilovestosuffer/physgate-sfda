#!/usr/bin/env bash
# Retry of n1_k10_after_queue.sh after: stale code dataset (paginated listing), dropped N1 push, 409 on kernel slugs equal to
# dataset slugs. Kernels are named physgate-run-*; pushes retry; pulls repeat until a result json exists.
set -u
cd "$(dirname "$0")/.."
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1
U=rhrhrhrhrh
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
python -u kaggle/sync_runner.py physgate-m0-code
sleep 300
run() {
  local k=$1; shift; local n=physgate-run-$(echo $k | tr 'A-Z_' 'a-z-'); local ds=()
  for d in "$@"; do ds+=(--dataset "$U/$d"); done
  local ok=0
  for attempt in 1 2 3 4 5 6; do
    python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n "${ds[@]}" --timeout-s 30600 && { ok=1; break; }
    echo "push failed $n (attempt $attempt)"; sleep 300
  done
  [ $ok = 1 ] || return
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  for attempt in 1 2 3 4 5 6; do
    python -u kaggle/pull.py --name $n
    find results/artifacts/$n -name "result_*.json" -o -name "kernel_log*.json" | grep -q . && find results/artifacts/$n -name "result_*.json" | grep -q . && break
    echo "pull incomplete $n (attempt $attempt)"; sleep 120
  done
}
run n1_probe physgate-m0-code physgate-m1-data
run k10_g1 physgate-m0-code physgate-k10-g1
run k10_g2 physgate-m0-code physgate-k10-g2
echo "$(date) retry queue done"
