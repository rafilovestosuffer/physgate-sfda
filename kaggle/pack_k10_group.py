"""Upload one C88 split group's window files as a PRIVATE Kaggle dataset on the active account.

The split window data live on whichever account first ran that group, and a private dataset is only visible to its owner.
Mirroring a group onto the other account lets the two accounts run different split groups at the same time instead of
queueing behind one another.

Usage (Git Bash):  python kaggle/pack_k10_group.py g2
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("group", help="g1 | g2 | g3 | g4")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    src = ROOT / "data" / "k10" / a.group
    files = sorted(src.glob("*.npz"))
    if not files:
        raise SystemExit(f"no .npz under {src}")
    user = _cli.username()
    slug = f"physgate-k10-{a.group}"
    size_mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"{user}/{slug}: {len(files)} files, {size_mb:.0f} MB")
    if a.dry_run:
        return 0

    tmp = Path(tempfile.mkdtemp()) / slug
    shutil.copytree(src, tmp)
    (tmp / "dataset-metadata.json").write_text(
        json.dumps({"title": slug, "id": f"{user}/{slug}", "licenses": [{"name": "other"}], "isPrivate": True},
                   indent=2), encoding="utf-8")
    exists = _cli.run("datasets", "status", f"{user}/{slug}", check=False).returncode == 0
    args = (["datasets", "version", "-p", ".", "-m", f"{a.group} windows", "--dir-mode", "zip"] if exists
            else ["datasets", "create", "-p", ".", "--dir-mode", "zip"])   # Windows path bug: run inside the folder
    cp = _cli.run(*args, check=False, cwd=str(tmp))
    print("rc", cp.returncode, (cp.stdout + cp.stderr).strip()[-300:])
    shutil.rmtree(tmp.parent, ignore_errors=True)
    return cp.returncode


if __name__ == "__main__":
    raise SystemExit(main())
