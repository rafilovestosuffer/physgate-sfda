#!/usr/bin/env bash
# C113 resume (2026-10-22): both accounts exhausted their 30 GPU-h week after g2 completed. Wait for the Saturday
# 00:00 UTC reset, then run the remaining groups on both accounts at once: primary g1 then g4, co-author g3.
#   & 'C:\Users\Rafi\Desktop\Git\bin\bash.exe' --login -c 'bash kaggle/shot2_k10_resume.sh'
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*"; }
RESET=${RESET:-2026102400}     # YYYYMMDDHH UTC
until [ "$(date -u +%Y%m%d%H)" -ge "$RESET" ]; do sleep 600; done
log "quota reset reached; starting"

run() {  # run <group> <user>  (same as shot2_k10_queue.sh; retries the push hourly for up to 6 h in case the reset lags)
  local g=$1 u=$2 n=physgate-shot2-k10-$1
  for attempt in 1 2 3 4 5 6; do
    python -u kaggle/preflight.py || { log "preflight refused ($u busy)"; sleep 1800; continue; }
    python -u kaggle/push.py --code kaggle/kernels/shot2_k10_$g.py --name $n --title $n \
      --dataset $u/physgate-m0-code --dataset $u/physgate-k10-$g --timeout-s 30600 && break
    log "push failed $n (attempt $attempt); retrying in 1 h"; sleep 3600
  done
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000 || log "poll returned $? for $n"
  python -u kaggle/pull.py --name $n || log "pull returned $? for $n"
}

( unset PHYSGATE_RUNNER PHYSGATE_KAGGLE_USER; run g1 rafiurrahman01; run g4 rafiurrahman01; log "primary g1+g4 done" ) \
  > tmp/c113/resume_primary.log 2>&1 &
P1=$!
( export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh; run g3 rhrhrhrhrh; log "co-author g3 done" ) \
  > tmp/c113/resume_coauthor.log 2>&1 &
P2=$!
wait $P1 $P2
log "ALL REMAINING GROUPS DONE"
