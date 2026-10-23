#!/usr/bin/env bash
# C113: corrected SHOT (shot_patch v2) on the ten C88 splits. One kernel at a time per account, groups balanced
# (g1+g4 = 5 splits on the primary, g2+g3 = 5 splits on the co-author). Each kernel ~3.5-4 h, under the 9 h cap.
#
#   bash kaggle/shot2_k10_queue.sh stage      # copy the fixed runner into runs/_stage/physgate-m0-code and version it on BOTH accounts
#   bash kaggle/shot2_k10_queue.sh primary    # g1 then g4 on rafiurrahman01
#   bash kaggle/shot2_k10_queue.sh coauthor   # g2 then g3 on rhrhrhrhrh
#
# Run `stage` once, then the two account queues in two terminals. Nothing here is executed by preparing the kernels.
set -u
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
log() { echo "[$(date +%H:%M:%S)] $*"; }

stage() {
  python -c "import importlib.util as u,sys; s=u.spec_from_file_location('sp','runners/shot_patch.py'); m=u.module_from_spec(s); s.loader.exec_module(m); sys.exit(0 if m.SHOT_PATCH_VERSION>=2 else 1)" \
    || { log "shot_patch.py is not v2; refusing to stage"; exit 1; }
  python -m pytest tests/test_shot_patch.py -q || { log "unit test failed; refusing to stage"; exit 1; }
  cp runners/sdalr_runner.py runners/shot_patch.py runners/bist.py results/m2/gate_verdicts.json runs/_stage/physgate-m0-code/
  echo "runner+shot_patch v2 (C113) @ $(git rev-parse --short HEAD)$(git status --porcelain runners/ | grep -q . && echo " (uncommitted runners/)")" >> runs/_stage/physgate-m0-code/SOURCE.txt
  log "versioning physgate-m0-code on the primary account"
  unset PHYSGATE_RUNNER PHYSGATE_KAGGLE_USER
  python -u kaggle/sync_runner.py physgate-m0-code || exit 1
  log "versioning physgate-m0-code on the co-author account"
  PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh python -u kaggle/sync_runner.py physgate-m0-code || exit 1
  log "staged; wait ~10 min for Kaggle to process the new dataset versions before pushing kernels"
}

run() {  # run <group> <user>
  local g=$1 u=$2 n=physgate-shot2-k10-$1
  python -u kaggle/preflight.py || { log "preflight refused ($u busy)"; exit 1; }
  python -u kaggle/push.py --code kaggle/kernels/shot2_k10_$g.py --name $n --title $n \
    --dataset $u/physgate-m0-code --dataset $u/physgate-k10-$g --timeout-s 30600 || { log "push failed $n"; exit 1; }
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000 || log "poll returned $? for $n"
  python -u kaggle/pull.py --name $n || log "pull returned $? for $n"
}

attach() {  # attach <group> : a kernel already pushed (e.g. by a queue that died): poll and pull only
  local n=physgate-shot2-k10-$1
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000 || log "poll returned $? for $n"
  python -u kaggle/pull.py --name $n || log "pull returned $? for $n"
}

case "${1:-}" in
  stage) stage ;;
  primary)  unset PHYSGATE_RUNNER PHYSGATE_KAGGLE_USER; run g1 rafiurrahman01; run g4 rafiurrahman01; log "primary done" ;;
  coauthor) export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh; run g2 rhrhrhrhrh; run g3 rhrhrhrhrh; log "co-author done" ;;
  # 2026-10-22: the primary account had no GPU quota left this week and the first queues were orphaned, so the whole
  # run goes serially on the co-author account: g2 is already running (attach), then g3, g1, g4 (~12 GPU-h in total).
  coauthor-all) export PHYSGATE_RUNNER=coauthor PHYSGATE_KAGGLE_USER=rhrhrhrhrh
                attach g2; run g3 rhrhrhrhrh; run g1 rhrhrhrhrh; run g4 rhrhrhrhrh; log "co-author all four groups done" ;;
  # 2026-10-22, later: both accounts exhausted after g2; the remaining groups run on the third credential (k4 runner).
  k4) export PHYSGATE_RUNNER=k4 PHYSGATE_KAGGLE_USER=shahedtheboss
      run g1 shahedtheboss; run g3 shahedtheboss; run g4 shahedtheboss; log "k4 g1, g3, g4 done" ;;
  # 2026-10-22, evening: the k4 bootstrap process died with the agent session while g1 was running; attach to g1, then g3, g4.
  k4-resume) export PHYSGATE_RUNNER=k4 PHYSGATE_KAGGLE_USER=shahedtheboss
             attach g1; run g3 shahedtheboss; run g4 shahedtheboss; log "k4 g1, g3, g4 done" ;;
  *) echo "usage: $0 stage|primary|coauthor|coauthor-all|k4|k4-resume"; exit 2 ;;
esac
