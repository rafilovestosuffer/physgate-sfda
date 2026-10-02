"""Refuse to push while a kernel is queued or running. Protects the 30 h/week GPU quota.

Read-only: lists the account's kernels and queries status. Never modifies or deletes anything.
Only kernels run within RECENT_HOURS are status-checked, because a queued or running kernel is by
definition recent, and one status call per kernel costs ~5 s.
"""
from __future__ import annotations

import csv
import io
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli  # noqa: E402

BUSY = {"queued", "running"}
RECENT_HOURS = 12  # > the 9 h GPU session cap


def list_kernels(user: str, page_size: int = 50) -> list[dict]:
    cp = _cli.run("kernels", "list", "--user", user, "--csv",
                  "--page-size", str(page_size), "--sort-by", "dateRun", check=False)
    if cp.returncode != 0:
        raise RuntimeError(f"kaggle kernels list failed: {cp.stderr.strip()}")
    text = "\n".join(line for line in cp.stdout.splitlines() if line.strip())
    return list(csv.DictReader(io.StringIO(text)))


def _parse_time(s: str) -> datetime | None:
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


def kernel_status(ref: str) -> str:
    cp = _cli.run("kernels", "status", ref, check=False)
    txt = (cp.stdout + cp.stderr).lower()
    for s in ("complete", "error", "cancel", "running", "queued"):
        if s in txt:
            return s
    return "unknown"


def recent(user: str, hours: int = RECENT_HOURS) -> list[dict]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    out = []
    for k in list_kernels(user):
        t = _parse_time(k.get("lastRunTime", ""))
        if t is None or t >= cutoff:
            out.append(k)
    return out


def clear_to_push(user: str, verbose: bool = True) -> bool:
    busy = []
    for k in recent(user):
        st = kernel_status(k["ref"])
        if verbose:
            print(f"  recent: {k['ref']:55s} {st}", flush=True)
        if st in BUSY:
            busy.append((k["ref"], st))
    for ref, st in busy:
        print(f"BUSY: {ref} is {st}", flush=True)
    return not busy


if __name__ == "__main__":
    u = _cli.username()
    ks = list_kernels(u)
    print(f"kaggle user: {u} | kernels on account: {len(ks)} | "
          f"status-checking those run in the last {RECENT_HOURS} h", flush=True)
    ok = clear_to_push(u)
    print("CLEAR TO PUSH" if ok else "NOT CLEAR -- a kernel is queued or running", flush=True)
    raise SystemExit(0 if ok else 3)
