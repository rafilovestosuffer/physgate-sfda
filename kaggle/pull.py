"""Pull kernel output and RETAIN THE ARTIFACT alongside the ledger row [C15]."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli

ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--out", default=None)
    a = p.parse_args()
    user = _cli.username(); ref = f"{user}/{a.name}"
    dest = Path(a.out) if a.out else ROOT / "results" / "artifacts" / a.name
    dest.mkdir(parents=True, exist_ok=True)
    cp = _cli.run("kernels", "output", ref, "-p", str(dest), check=False)
    print(cp.stdout.strip() or cp.stderr.strip())
    got = sorted(x.name for x in dest.iterdir())
    print(f"artifact retained at {dest.relative_to(ROOT)}: {got}")
    return 0 if got else 1

if __name__ == "__main__":
    raise SystemExit(main())
