"""Download the 64-record CWRU 12k DE subset and verify every file against published SHA-256.

Checksums: predictive-maintenance-mcp benchmarks/cwru/checksums.json (CC BY-NC-SA 4.0).
A file that fails its checksum is deleted and the run exits non-zero. Never silently accepted.
"""
import hashlib, io, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "cwru"
OPS = json.load(io.open(ROOT / "notes" / "_pmmcp_records_ops.json", encoding="utf-8"))
SUMS = json.load(io.open(ROOT / "notes" / "_pmmcp_checksums.json", encoding="utf-8"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    bad = []
    for i, o in enumerate(OPS, 1):
        name = o["cache_filename"]; dst = OUT / name; want = SUMS[name]
        if dst.exists() and dst.stat().st_size == want["bytes"] and sha256(dst) == want["sha256"]:
            print(f"[{i:2d}/64] {name:9s} cached, verified", flush=True); continue
        for attempt in range(3):
            try:
                req = urllib.request.Request(o["url"], headers={"User-Agent": "Mozilla/5.0 (research download)"})
                with urllib.request.urlopen(req, timeout=120) as r, open(dst, "wb") as fh:
                    fh.write(r.read())
                break
            except Exception as e:  # noqa: BLE001
                print(f"  retry {attempt+1}: {e}", flush=True); time.sleep(3)
        got = sha256(dst) if dst.exists() else ""
        ok = got == want["sha256"]
        print(f"[{i:2d}/64] {name:9s} {dst.stat().st_size/1e6 if dst.exists() else 0:6.2f} MB  {'OK' if ok else 'CHECKSUM FAIL'}", flush=True)
        if not ok:
            bad.append(name); dst.unlink(missing_ok=True)
        time.sleep(0.5)  # be polite to the host
    print(f"done: {64-len(bad)}/64 verified" + (f"; FAILED: {bad}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
