# Shared robust push/poll/pull. Needs U (account) set. Usage: run <kernel-file-stem> <dataset>...
run() {
  local k=$1; shift; local n=physgate-run-$(echo $k | tr 'A-Z_' 'a-z-'); local ds=()
  for d in "$@"; do ds+=(--dataset "$U/$d"); done
  if find results/artifacts/$n -name "result_*.json" 2>/dev/null | grep -q .; then echo "skip $n: results present"; return; fi
  local st; st=$(python -c "import sys;sys.path.insert(0,'kaggle');import _cli;cp=_cli.run('kernels','status','$U/$n',check=False);print(cp.stdout)" 2>/dev/null)
  if ! echo "$st" | grep -q "RUNNING\|QUEUED\|COMPLETE"; then
    local ok=0
    for attempt in 1 2 3 4 5 6 7 8 9 10 11 12; do
      python -u kaggle/push.py --code kaggle/kernels/$k.py --name $n --title $n "${ds[@]}" --timeout-s 30600 && { ok=1; break; }
      echo "push failed $n (attempt $attempt)"; sleep 900
    done
    [ $ok = 1 ] || return
  else echo "attach $n: $st"; fi
  python -u kaggle/poll.py --name $n --interval 300 --timeout 33000
  for attempt in 1 2 3 4 5 6; do
    python -u kaggle/pull.py --name $n
    find results/artifacts/$n -name "result_*.json" | grep -q . && break
    echo "pull incomplete $n (attempt $attempt)"; sleep 120
  done
}
