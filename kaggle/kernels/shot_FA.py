"""Kaggle kernel: C85 SHOT on the M1 paired design on PU L3, one SOURCE fold per kernel.

For source fold F (set below) and its complement F':
  as_released      F -> F   (pretrains the shared fold-F source model; leaky target)
  as_released      F -> F'  (clean target, same source model)
  final_checkpoint F -> F
  final_checkpoint F -> F'
Each call is its own process; results flush after every task to /kaggle/working/m1/.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SRC_FOLD = "A"
OTHER = {"A": "B", "B": "A"}[SRC_FOLD]
SEED = os.environ.get("M1_SEED", "2024")
WORK = Path("/kaggle/working/shot")
WORK.mkdir(parents=True, exist_ok=True)

runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m1 = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SRC_FOLD}_N15_M01_F10.npz")).parent
print("runner:", runner, "\nsdalr:", sdalr, "\nm1:", m1, flush=True)

import torch  # noqa: E402
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)),
       "torch": torch.__version__, "python": sys.version.split()[0], "src_fold": SRC_FOLD}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"

plan = [("shot", SRC_FOLD, []), ("shot", OTHER, ["--skip-pretrain"])]
_unused = [
        ("final_checkpoint", SRC_FOLD, ["--skip-pretrain"]), ("final_checkpoint", OTHER, ["--skip-pretrain"])]
log = []
for variant, tgt, extra in plan:
    t0 = time.time()
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m1), "--dataset", "PU_M1",
           "--src-fold", SRC_FOLD, "--tgt-fold", tgt, "--variant", variant, "--work", str(WORK), "--seed", SEED, *extra]
    print("RUN", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    log.append({"variant": variant, "src": SRC_FOLD, "tgt": tgt, "rc": rc, "seconds": round(time.time() - t0)})
    print(log[-1], flush=True)
    (WORK / f"kernel_log_F{SRC_FOLD}.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))

for p in WORK.glob("sdalr_*"):
    shutil.rmtree(p, ignore_errors=True)
for p in WORK.glob("weight_*"):
    shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
