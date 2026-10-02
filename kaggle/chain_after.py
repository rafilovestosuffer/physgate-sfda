"""Wait until a named kernel reaches a terminal state, then run the given shell steps in order."""
import subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli
name, steps = sys.argv[1], sys.argv[2:]
if sys.platform == "win32" and any("'" in st for st in steps):
    sys.exit("REFUSED: steps run under cmd.exe, which does not honour single quotes (M1 push failed this way on 2026-09-13)")
ref = f"{_cli.username()}/{name}"
while True:
    cp = _cli.run("kernels", "status", ref, check=False)
    txt = (cp.stdout + cp.stderr).lower()
    if "kernelworkerstatus" in txt and any(s in txt for s in ("complete", "error", "cancel")):
        print(time.strftime("%H:%M:%S"), ref, "terminal:", txt.strip()[-60:], flush=True)
        break
    time.sleep(240)
for step in steps:
    print(time.strftime("%H:%M:%S"), "STEP", step, flush=True)
    rc = subprocess.run(step, shell=True).returncode
    print(time.strftime("%H:%M:%S"), "rc", rc, flush=True)
    if rc != 0:
        sys.exit(f"step failed (rc={rc}); stopping the chain instead of polling a kernel that was never pushed")
