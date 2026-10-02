# Single-instance guard: . kaggle/lock.sh <name>. Exits if another live instance holds the lock.
LOCK="runs/.lock_$1"
if [ -f "$LOCK" ] && kill -0 "$(cat "$LOCK")" 2>/dev/null; then echo "$(date) $1 already running (pid $(cat "$LOCK"))"; exit 0; fi
echo $$ > "$LOCK"
trap 'rm -f "$LOCK"' EXIT
