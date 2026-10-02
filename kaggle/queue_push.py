"""Wait until no kernel is queued/running, then push. Respects preflight rather than bypassing it."""
import subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli, preflight

args = sys.argv[1:]
user = _cli.username()
while not preflight.clear_to_push(user, verbose=False):
    print(time.strftime("%H:%M:%S"), "waiting for running kernel to finish...", flush=True)
    time.sleep(180)
print(time.strftime("%H:%M:%S"), "clear -> pushing", flush=True)
sys.exit(subprocess.run([sys.executable, str(Path(__file__).parent / "push.py"), *args]).returncode)
