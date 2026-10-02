"""Version the repository's CODE as a PRIVATE Kaggle Dataset, so kernels run exactly this commit.

Ships only source and configs. Never ships data, credentials, runs/, or results/.
Refuses to pack a dirty working tree: a kernel must be traceable to a git SHA.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INCLUDE = ["physics", "configs", "models", "sfda", "eval", "data_prep", "metadata",
           "PROTOCOL.md", "requirements.txt"]
NEVER = {"kaggle.json", ".kaggle", "data", "runs", "results", ".git", "__pycache__"}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", default="physgate-code")
    p.add_argument("--allow-dirty", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    if git("status", "--porcelain") and not a.allow_dirty:
        raise SystemExit("REFUSED: working tree is dirty. Commit first so the kernel maps to a SHA.")
    sha = git("rev-parse", "--short", "HEAD")
    user = _cli.username()

    stage = ROOT / "runs" / "_pack" / a.slug
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    for item in INCLUDE:
        src = ROOT / item
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, stage / item,
                            ignore=shutil.ignore_patterns(*NEVER, "*.pyc", "*.mat", "*.pt"))
        else:
            shutil.copy2(src, stage / item)
    (stage / "GIT_SHA").write_text(sha + "\n", encoding="utf-8")
    meta = {"title": a.slug, "id": f"{user}/{a.slug}", "licenses": [{"name": "other"}], "isPrivate": True}
    (stage / "dataset-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    for bad in NEVER:
        assert not any(stage.rglob(bad)), f"packaging leak: {bad} found in stage"
    print(f"staged {user}/{a.slug} @ {sha} -> {stage}")
    if a.dry_run:
        return 0

    exists = _cli.run("datasets", "status", f"{user}/{a.slug}", check=False).returncode == 0
    if exists:
        cp = _cli.run("datasets", "version", "-p", str(stage), "-m", f"code @ {sha}", "--dir-mode", "zip")
    else:
        cp = _cli.run("datasets", "create", "-p", str(stage), "--dir-mode", "zip")
    print(cp.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
