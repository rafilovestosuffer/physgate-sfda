#!/usr/bin/env bash
set -u
cd "$(dirname "$0")/.."
. kaggle/lock.sh queue_primary_g34
export PYTHONUTF8=1; unset PHYSGATE_RUNNER PHYSGATE_KAGGLE_USER
U=rafiurrahman01
. kaggle/lib_run.sh
until [ "$(date -u +%Y%m%d%H)" -ge 2026091900 ]; do sleep 600; done
for g in g4; do mkdir -p runs/_stage/physgate-k10-$g; cp -n data/k10/$g/*.npz runs/_stage/physgate-k10-$g/; done
cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
[ -f runs/.synced_primary_g34 ] || { python -u kaggle/sync_runner.py physgate-m0-code physgate-k10-g4 && touch runs/.synced_primary_g34 && sleep 900; }
run k10_g4 physgate-m0-code physgate-k10-g4
echo "$(date) primary g3/g4 done"
