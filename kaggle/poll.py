"""Poll a kernel until it leaves the queued/running state."""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli, preflight

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--interval", type=int, default=60)
    p.add_argument("--timeout", type=int, default=9 * 3600)  # Kaggle GPU session cap is 9 h
    a = p.parse_args()
    user = _cli.username(); ref = f"{user}/{a.name}"
    t0 = time.time()
    unknown_streak = 0
    while True:
        cp = _cli.run("kernels", "status", ref, check=False)
        txt = (cp.stdout + cp.stderr).strip()
        low = txt.lower()
        # Only trust a real status line; exception text (e.g. "NameResolutionError") must never read as "error" (2026-09-15).
        st = next((s for s in ("complete", "error", "cancel", "running", "queued") if s in low), "unknown")             if "kernelworkerstatus" in low else "unknown"
        el = time.time() - t0
        print(f"[{el/60:6.1f} min] {ref}: {st}")
        # A kernel that was never pushed reports "unknown" forever (2026-09-13: 40 min lost). Fail fast.
        unknown_streak = unknown_streak + 1 if st == "unknown" else 0
        if unknown_streak >= 12:   # ~1 h of no valid status (DNS outages happen); a never-pushed kernel still fails
            print(f"NOT FOUND -- {ref} returned no status 3 times in a row; was it pushed? ({txt[-120:]})")
            return 3
        if st in ("complete", "error", "cancel"):
            return 0 if st == "complete" else 1
        if el > a.timeout:
            print("TIMEOUT -- Kaggle GPU sessions cap at 9 h; assume the run was killed.")
            return 2
        time.sleep(a.interval)

if __name__ == "__main__":
    raise SystemExit(main())
