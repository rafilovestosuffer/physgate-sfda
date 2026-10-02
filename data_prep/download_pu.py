"""Download and extract all 32 Paderborn bearings (Lessmeier et al. 2016, KAt-DataCenter).

Citation condition applies: cite Lessmeier et al. 2016 in any use.
No checksums are published, so each archive is verified against the server's Content-Length and our
own SHA-256 is recorded in data/pu/_provenance.json. Extraction uses 7-Zip (RAR support).
Archives are deleted only after extraction is verified to yield the expected .mat files.
"""
import hashlib, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "pu"
BASE = "https://groups.uni-paderborn.de/kat/BearingDataCenter"
SEVENZIP = r"C:\Program Files\7-Zip\7z.exe"
# Priority order: M0 needs SDALR's 8 bearings first; then the rest of the real-damage population
# (M1, B3 target); then healthy; then artificial (B3 source); compound last (stress test only).
BEARINGS = (["K001", "KA04", "KA15", "KA22", "KA30", "KI14", "KI17", "KI21"]
            + ["KA16", "KI04", "KI16", "KI18"]
            + ["K002", "K003", "K004", "K005", "K006"]
            + ["KA01", "KA03", "KA05", "KA06", "KA07", "KA08", "KA09"]
            + ["KI01", "KI03", "KI05", "KI07", "KI08"]
            + ["KB23", "KB24", "KB27"])
assert len(BEARINGS) == 32 and len(set(BEARINGS)) == 32


def head_len(url, attempts=30, wait=20):
    """Retry through transient outages (a DNS failure previously failed 28 bearings in seconds)."""
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return int(r.headers["Content-Length"])
        except Exception as e:  # noqa: BLE001
            last = e
            print(f"  HEAD retry {i+1}/{attempts} in {wait}s: {e}", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"HEAD failed after {attempts} attempts: {last}")


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 22), b""):
            h.update(c)
    return h.hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prov_p = OUT / "_provenance.json"
    prov = json.loads(prov_p.read_text()) if prov_p.exists() else {}
    fails = []
    for i, b in enumerate(BEARINGS, 1):
        dest_dir = OUT / b
        if prov.get(b, {}).get("extracted") and dest_dir.exists() and len(list(dest_dir.glob("*.mat"))) >= 80:
            print(f"[{i:2d}/32] {b} already extracted ({len(list(dest_dir.glob('*.mat')))} .mat)", flush=True)
            continue
        url = f"{BASE}/{b}.rar"; rar = OUT / f"{b}.rar"
        try:
            want = head_len(url)
            if not (rar.exists() and rar.stat().st_size == want):
                t0 = time.time()
                for attempt in range(8):
                    try:
                        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=300) as r, open(rar, "wb") as fh:
                            while True:
                                chunk = r.read(1 << 22)
                                if not chunk:
                                    break
                                fh.write(chunk)
                        if rar.stat().st_size == want:
                            break
                        print(f"  size mismatch {rar.stat().st_size} != {want}, retry", flush=True)
                    except Exception as e:  # noqa: BLE001
                        print(f"  retry {attempt+1}: {e}", flush=True); time.sleep(30)
                print(f"[{i:2d}/32] {b} downloaded {want/1e6:.0f} MB in {time.time()-t0:.0f}s", flush=True)
            if rar.stat().st_size != want:
                raise RuntimeError(f"size {rar.stat().st_size} != {want}")
            digest = sha256(rar)
            cp = subprocess.run([SEVENZIP, "x", "-y", f"-o{OUT}", str(rar)], capture_output=True, text=True)
            if cp.returncode != 0:
                raise RuntimeError(f"7z failed: {cp.stderr[-400:]}")
            mats = sorted(dest_dir.glob("*.mat")) if dest_dir.exists() else []
            if len(mats) < 80:
                raise RuntimeError(f"expected >=80 .mat in {dest_dir}, found {len(mats)}")
            prov[b] = {"url": url, "bytes": want, "sha256": digest, "n_mat": len(mats), "extracted": True,
                       "downloaded_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            prov_p.write_text(json.dumps(prov, indent=1))
            rar.unlink()
            print(f"[{i:2d}/32] {b} extracted {len(mats)} .mat, sha256 {digest[:12]}..., archive removed", flush=True)
        except Exception as e:  # noqa: BLE001
            fails.append(b); print(f"[{i:2d}/32] {b} FAILED: {e}", flush=True)
    print(f"PU done: {32-len(fails)}/32 ok" + (f"; FAILED {fails}" if fails else ""), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
