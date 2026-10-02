"""Kaggle CLI shim.

NEVER `import kaggle`: the interpreter on PATH is Python 3.11 without the package, while the CLI
lives under a different Python. We shell out to the resolved executable instead.
NEVER read, print, log or commit the contents of ~/.kaggle/kaggle.json. The CLI reads it itself.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

# C15 multi-runner: PHYSGATE_RUNNER=coauthor switches every call to ~/.kaggle_coauthor (the co-author's own account).
RUNNER_DIRS = {"primary": Path.home() / ".kaggle", "coauthor": Path.home() / ".kaggle_coauthor"}


def config_dir() -> Path:
    name = os.environ.get("PHYSGATE_RUNNER", "primary")
    if name not in RUNNER_DIRS:
        raise RuntimeError(f"unknown PHYSGATE_RUNNER {name!r}; known: {sorted(RUNNER_DIRS)}")
    return RUNNER_DIRS[name]


CRED = config_dir() / "kaggle.json"


def kaggle_exe() -> str:
    exe = shutil.which("kaggle")
    if exe:
        return exe
    for c in (Path.home() / "AppData/Local/Programs/Python/Python313/Scripts/kaggle.exe",):
        if c.exists():
            return str(c)
    raise RuntimeError("kaggle CLI not found on PATH. Install it, do not `import kaggle`.")


def username() -> str:
    """Runner username. Legacy kaggle.json: read ONLY its username field. New-style `access_token` files carry no
    username, so it comes from PHYSGATE_KAGGLE_USER (not secret). The key/token is never read here."""
    if os.environ.get("PHYSGATE_KAGGLE_USER"):
        return os.environ["PHYSGATE_KAGGLE_USER"]
    if CRED.exists():
        with open(CRED, encoding="utf-8") as fh:
            return json.load(fh)["username"]
    if (config_dir() / "access_token").exists():
        raise RuntimeError("access_token found but no username: set PHYSGATE_KAGGLE_USER=<kaggle username>")
    raise RuntimeError(f"no Kaggle credentials in {config_dir()}")


def run(*args: str, check: bool = True, cwd: str | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["KAGGLE_CONFIG_DIR"] = str(config_dir())     # the CLI reads the key itself; we never do
    tok = config_dir() / "access_token"
    if os.environ.get("PHYSGATE_RUNNER", "primary") != "primary":
        if not tok.exists():
            raise RuntimeError(f"runner token file missing: {tok}")
        # kagglesdk.get_access_token_from_env accepts a PATH in KAGGLE_API_TOKEN and reads the file itself. It is checked
        # before ~/.kaggle/access_token and the OAuth credentials, so the runner cannot fall back to the primary account.
        env["KAGGLE_API_TOKEN"] = str(tok)
    cp = subprocess.run([kaggle_exe(), *args], capture_output=True, text=True, env=env, cwd=cwd)
    if check and cp.returncode != 0:
        raise RuntimeError(f"kaggle {' '.join(args)} failed ({cp.returncode}):\n{cp.stderr.strip()}")
    return cp
