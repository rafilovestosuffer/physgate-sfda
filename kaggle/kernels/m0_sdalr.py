"""Kaggle kernel: M0 -- reproduce SDALR (Track R) on T4, both model-selection variants.

Inputs (private Kaggle Datasets):
  physgate-m0-code : runners/sdalr_runner.py + third_party/SDALR (commit fb9c379, no licence -> private)
  physgate-m0-data : data/m0/*.npz built by data_prep/make_m0.py

Order per dataset, each in its OWN process so no module state leaks between variants:
  1. as_released       (pretrains the shared source model, then 6 tasks with label-selected checkpoint)
  2. final_checkpoint  (reuses that source model, 6 tasks with the last iterate)
Results are flushed after every task to /kaggle/working/m0/, so a killed session keeps finished work.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

DATASETS = os.environ.get("M0_DATASETS", "JNU").split(",")
SEED = os.environ.get("M0_SEED", "2024")
WORK = Path("/kaggle/working/m0")
WORK.mkdir(parents=True, exist_ok=True)


def find_input(marker: str) -> Path:
    for p in Path("/kaggle/input").rglob(marker):
        return p.parent
    raise FileNotFoundError(f"{marker} not found under /kaggle/input: "
                            f"{[str(x) for x in Path('/kaggle/input').iterdir()]}")


# The code dataset is staged FLAT (Kaggle datasets are simplest without subdirectories):
# sdalr_runner.py sits next to SDALR's own .py files.
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m0 = find_input("JNU_600rpm.npz")
print("runner:", runner, "\nsdalr:", sdalr, "\nm0:", m0, flush=True)

import torch  # noqa: E402
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
       "torch": torch.__version__, "python": sys.version.split()[0]}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"

log = []
for ds in DATASETS:
    for variant, extra in (("as_released", []), ("final_checkpoint", ["--skip-pretrain"])):
        t0 = time.time()
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m0), "--dataset", ds,
               "--variant", variant, "--work", str(WORK), "--seed", SEED, *extra]
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
        log.append({"dataset": ds, "variant": variant, "rc": rc, "seconds": round(time.time() - t0)})
        print(log[-1], flush=True)
        (WORK / "kernel_log.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))

# keep outputs small: drop checkpoints and copied code, keep results + logs
for p in WORK.glob("sdalr_*"):
    shutil.rmtree(p, ignore_errors=True)
for p in WORK.glob("weight_*"):
    shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
