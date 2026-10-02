"""Kaggle kernel: M2/M3 (PROTOCOL C81) -- gates inside SDALR obtain_label on the 12 M1 clean tasks, one SOURCE fold per kernel.

For source fold F and complement F': final_checkpoint, arms none -> c30 -> v2 -> pcv -> eagle -> oracle, each its own process.
The first arm pretrains the shared fold-F source model; the others reuse it. Results flushed per task to /kaggle/working/m2/.
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
SRC_FOLD = os.environ.get("M2_SRC_FOLD", "A")
OTHER = {"A": "B", "B": "A"}[SRC_FOLD]
SEED = os.environ.get("M2_SEED", "2024")
WORK = Path("/kaggle/working/m2"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
verdicts = next(Path("/kaggle/input").rglob("gate_verdicts.json"))
m1 = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SRC_FOLD}_N15_M01_F10.npz")).parent
import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)), "src_fold": SRC_FOLD}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"
log = []
for i, gate in enumerate(("none", "c30", "v2", "pcv", "eagle", "oracle")):
    t0 = time.time()
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m1), "--dataset", "PU_M1",
           "--src-fold", SRC_FOLD, "--tgt-fold", OTHER, "--variant", "final_checkpoint", "--work", str(WORK),
           "--seed", SEED, "--gate", gate, "--gate-verdicts", str(verdicts)] + ([] if i == 0 else ["--skip-pretrain"])
    print("RUN", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    log.append({"gate": gate, "rc": rc, "seconds": round(time.time() - t0)})
    (WORK / f"kernel_log_F{SRC_FOLD}.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))
for p in list(WORK.glob("sdalr_*")) + list(WORK.glob("weight_*")):
    shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
