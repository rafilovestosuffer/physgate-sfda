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
RUNNER_DIRS = {"primary": Path.home() / ".kaggle", "coauthor": Path.home() / ".kaggle_coauthor",
               "k4": Path.home() / ".kaggle" / "k 4",   # third credential (legacy kaggle.json); C113 amendment, 2026-10-22
               "abrar": Path.home() / ".kaggle" / "3"}  # fourth credential (abrarbangladesh); C113 amendment 3, 2026-10-23


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
        if tok.exists():
            # kagglesdk.get_access_token_from_env accepts a PATH in KAGGLE_API_TOKEN and reads the file itself. It is checked
            # before ~/.kaggle/access_token and the OAuth credentials, so the runner cannot fall back to the primary account.
            env["KAGGLE_API_TOKEN"] = str(tok)
        elif (config_dir() / "kaggle.json").exists():
            # Legacy-key runner. The CLI authenticates in the order access token (KAGGLE_API_TOKEN, then
            # ~/.kaggle/access_token) -> legacy key (kaggle.json in KAGGLE_CONFIG_DIR) -> OAuth (~/.kaggle/credentials.json),
            # so the PRIMARY account's token files under ~/.kaggle would win silently (observed 2026-10-22: the k4 runner
            # listed the primary account's datasets). Point HOME/USERPROFILE at an empty directory for this call so that
            # only the runner's kaggle.json is visible; the CLI reads the key itself, this code never does.
            import tempfile
            home = Path(tempfile.gettempdir()) / f"physgate_home_{os.environ['PHYSGATE_RUNNER']}"
            home.mkdir(exist_ok=True)
            # Uploads go through kagglesdk, which reads the legacy key from the hard-coded ~/.kaggle/kaggle.json, so the
            # redirected home gets a directory junction .kaggle -> the runner's folder (no copy of the key is made).
            link = home / ".kaggle"
            if not link.exists():
                subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(config_dir())], capture_output=True, check=True)
            env["HOME"] = env["USERPROFILE"] = str(home)
            for k in ("KAGGLE_API_TOKEN", "KAGGLE_USERNAME", "KAGGLE_KEY"):
                env.pop(k, None)
        else:
            raise RuntimeError(f"runner credentials missing in {config_dir()} (neither access_token nor kaggle.json)")
    cp = subprocess.run([kaggle_exe(), *args], capture_output=True, text=True, env=env, cwd=cwd)
    if check and cp.returncode != 0:
        raise RuntimeError(f"kaggle {' '.join(args)} failed ({cp.returncode}):\n{cp.stderr.strip()}")
    return cp
