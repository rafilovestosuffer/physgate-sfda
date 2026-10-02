#!/usr/bin/env bash
# C100 on the co-author account: wait for g1, pull it, then run g3. One kernel at a time per account.
set -u
cd "$(dirname "$0")/.."
export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh PYTHONUTF8=1

log() { echo "[$(date +%H:%M:%S)] $*"; }

log "waiting for g1"
python kaggle/poll.py --name physgate-shot-k10-g1 --timeout 32000 || log "g1 poll returned $?"
python kaggle/pull.py --name physgate-shot-k10-g1 || log "g1 pull returned $?"

log "pushing g3"
python kaggle/push.py --code kaggle/kernels/shot_k10_g3.py --name physgate-shot-k10-g3 \
  --dataset rhrhrhrhrh/physgate-m0-code --dataset rhrhrhrhrh/physgate-k10-g3 || { log "g3 push failed"; exit 1; }

log "waiting for g3"
python kaggle/poll.py --name physgate-shot-k10-g3 --timeout 32000 || log "g3 poll returned $?"
python kaggle/pull.py --name physgate-shot-k10-g3 || log "g3 pull returned $?"
log "co-author queue done"
