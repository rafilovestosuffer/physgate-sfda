"""Kaggle kernel: C82 repeat control -- arms none, v2, pcv; one SOURCE fold and one repeat index per kernel."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
SRC_FOLD = "B"; REP = "1"
OTHER = {"A": "B", "B": "A"}[SRC_FOLD]
WORK = Path("/kaggle/working/m2rep"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
verdicts = next(Path("/kaggle/input").rglob("gate_verdicts.json"))
m1 = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SRC_FOLD}_N15_M01_F10.npz")).parent
import torch
assert torch.cuda.get_device_name(0) == "Tesla T4"
log = []
for i, gate in enumerate(("none", "v2", "pcv")):
    t0 = time.time(); w = WORK / f"rep{REP}"
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m1), "--dataset", "PU_M1", "--src-fold", SRC_FOLD,
           "--tgt-fold", OTHER, "--variant", "final_checkpoint", "--work", str(w), "--seed", "2024", "--gate", gate,
           "--gate-verdicts", str(verdicts)] + ([] if i == 0 else ["--skip-pretrain"])
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    log.append({"gate": gate, "rc": rc, "seconds": round(time.time() - t0)}); print(log[-1], flush=True)
    (WORK / f"kernel_log_F{SRC_FOLD}_rep{REP}.json").write_text(json.dumps(log, indent=2))
for p in list(WORK.rglob("sdalr_*")) + list(WORK.rglob("weight_*")):
    shutil.rmtree(p, ignore_errors=True)
