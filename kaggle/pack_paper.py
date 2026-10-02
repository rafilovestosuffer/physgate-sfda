"""Version paper/tex as the PRIVATE Kaggle Dataset that the build_pdf kernel compiles.

Ships the LaTeX sources only (main.tex, sections/, tables/, figures/, references.bib). No data, no credentials.
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
TEX = ROOT / "paper" / "tex"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--slug", default="physgate-paper")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    user = _cli.username()
    sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.strip()
    stage = ROOT / "runs" / "_pack" / a.slug
    shutil.rmtree(stage, ignore_errors=True)
    shutil.copytree(TEX, stage, ignore=shutil.ignore_patterns("*.aux", "*.log", "*.out", "__pycache__"))
    assert (stage / "main.tex").exists(), "main.tex missing from the stage"
    meta = {"title": a.slug, "id": f"{user}/{a.slug}", "licenses": [{"name": "other"}], "isPrivate": True}
    (stage / "dataset-metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    n = sum(1 for _ in stage.rglob("*") if _.is_file())
    print(f"staged {user}/{a.slug}: {n} files -> {stage}")
    if a.dry_run:
        return 0

    exists = _cli.run("datasets", "status", f"{user}/{a.slug}", check=False).returncode == 0
    cp = (_cli.run("datasets", "version", "-p", str(stage), "-m", f"tex @ {sha}", "--dir-mode", "zip") if exists
          else _cli.run("datasets", "create", "-p", str(stage), "--dir-mode", "zip"))
    print(cp.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
