#!/usr/bin/env bash
# C88 groups g3, g4 on the primary account (rafiurrahman01) after its weekly GPU quota resets (Sat 00:00 UTC).
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1; unset PHYSGATE_RUNNER PHYSGATE_KAGGLE_USER
until [ "$(date -u +%Y%m%d%H)" -ge 2026091900 ]; do sleep 600; done
while ps -ef | grep -v grep | grep -q "make_k10.py"; do sleep 60; done
U=rafiurrahman01
for g in g3 g4; do mkdir -p runs/_stage/physgate-k10-$g; cp -n data/k10/$g/*.npz runs/_stage/physgate-k10-$g/; done
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
python -u kaggle/sync_runner.py physgate-m0-code physgate-k10-g3 physgate-k10-g4
sleep 600
run() {
  local k=$1; shift; local n=physgate-run-$(echo $k | tr 'A-Z_' 'a-z-'); local ds=()
  for d in "$@"; do ds+=(--dataset "$U/$d"); done
  for attempt in $(seq 1 24); do   # quota may not be back yet: retry hourly
    python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n "${ds[@]}" --timeout-s 30600 && break
    echo "push failed $n (attempt $attempt)"; sleep 3600
  done
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  python -u kaggle/pull.py --name $n
}
run k10_g3 physgate-m0-code physgate-k10-g3
run k10_g4 physgate-m0-code physgate-k10-g4
echo "$(date) primary K10 g3/g4 done"
