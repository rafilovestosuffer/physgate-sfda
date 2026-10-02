"""Mirror the project's private Kaggle datasets to the active runner's account (C15 multi-runner).

Usage (Git Bash):  PHYSGATE_RUNNER=coauthor python kaggle/sync_runner.py
Creates or versions  <runner>/physgate-m0-code  and  <runner>/physgate-m1-data  as PRIVATE datasets from runs/_stage/.
Reads only the username field of the runner's kaggle.json.
"""
import json, shutil, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli
ROOT = Path(__file__).resolve().parents[1]
STAGES = sys.argv[1:] or ["physgate-m0-code", "physgate-m1-data"]

def main():
    user = _cli.username()
    print("runner account:", user)
    listing = _cli.run("datasets", "list", "--mine", "--csv", check=False).stdout
    for name in STAGES:
        src = ROOT / "runs" / "_stage" / name
        tmp = Path(tempfile.mkdtemp()) / name
        shutil.copytree(src, tmp)
        meta = {"title": name, "id": f"{user}/{name}", "licenses": [{"name": "other"}], "isPrivate": True}
        (tmp / "dataset-metadata.json").write_text(json.dumps(meta, indent=2))
        # the --mine listing is paginated; ask for the dataset directly
        exists = f"{user}/{name}" in listing or _cli.run("datasets", "status", f"{user}/{name}", check=False).returncode == 0
        args = (["datasets", "version", "-p", ".", "-m", "sync from primary", "--dir-mode", "zip"] if exists
                else ["datasets", "create", "-p", ".", "--dir-mode", "zip"])   # Windows path bug: run inside the folder
        cp = _cli.run(*args, check=False, cwd=str(tmp))
        print(name, "version" if exists else "create", "rc", cp.returncode, (cp.stdout + cp.stderr).strip()[-160:])
        shutil.rmtree(tmp.parent, ignore_errors=True)

if __name__ == "__main__":
    main()
