#!/usr/bin/env bash
# C113 amendment (2026-10-22): mirror the code dataset and the g1/g3/g4 split datasets to the third credential (k4 runner,
# Kaggle user shahedtheboss), wait for Kaggle to process them, then run the three groups there serially.
#   & 'C:\Users\Rafi\Desktop\Git\bin\bash.exe' --login -c 'bash kaggle/k4_bootstrap.sh'
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1 PHYSGATE_RUNNER=k4 PHYSGATE_KAGGLE_USER=shahedtheboss
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }

log "code dataset -> k4"
python -u kaggle/sync_runner.py physgate-m0-code || { log "code dataset sync failed"; exit 1; }
for g in g1 g3 g4; do
  log "split dataset $g -> k4"
  for attempt in 1 2 3; do
    python -u kaggle/pack_k10_group.py $g && break
    log "upload of $g failed (attempt $attempt); retrying in 5 min"; sleep 300
  done
done
log "uploads done; waiting 10 min for dataset processing"
sleep 600
for g in g1 g3 g4; do
  python -c "import sys,os; sys.path.insert(0,'kaggle'); import _cli; cp=_cli.run('datasets','status','shahedtheboss/physgate-k10-$g',check=False); print('$g', (cp.stdout+cp.stderr).strip()[:40]); sys.exit(cp.returncode)" \
    || { log "dataset physgate-k10-$g not ready on k4; aborting before any push"; exit 1; }
done
log "starting the k4 queue"
bash kaggle/shot2_k10_queue.sh k4
log "K4 BOOTSTRAP END"
