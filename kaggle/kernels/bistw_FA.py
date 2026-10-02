"""Kaggle kernel: C87 Step 2, BIST-W (class-conditional bearing adversary, lambda_max 1.0) on the M1 paired design, source fold A.
N1 passed (within-class record probe 507/508). Baselines: SDALR = M1/M2 artifacts, SHOT = C85 artifacts.
  1. SDALR final_checkpoint, BIST-W source model + probe on BIST-W features   (leaky A->A, clean A->B)
  2. SHOT on the same BIST-W source model                                      (leaky, clean)
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
SRC_FOLD = "A"
OTHER = "B"
WORK = Path("/kaggle/working/bistw"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m1 = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SRC_FOLD}_N15_M01_F10.npz")).parent
import torch
assert torch.cuda.get_device_name(0) == "Tesla T4"
plan = [("final_checkpoint", SRC_FOLD, ["--bist", "--probe"]), ("final_checkpoint", OTHER, ["--bist", "--skip-pretrain"]),
        ("shot", SRC_FOLD, ["--bist", "--skip-pretrain"]), ("shot", OTHER, ["--bist", "--skip-pretrain"])]
log = []
for variant, tgt, extra in plan:
    t0 = time.time()
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m1), "--dataset", "PU_M1", "--src-fold", SRC_FOLD,
           "--tgt-fold", tgt, "--variant", variant, "--work", str(WORK), "--seed", "2024", *extra]
    print("RUN", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    log.append({"variant": variant, "tgt": tgt, "extra": extra, "rc": rc, "seconds": round(time.time() - t0)}); print(log[-1], flush=True)
    (WORK / f"kernel_log_F{SRC_FOLD}.json").write_text(json.dumps({"runs": log}, indent=2))
for p in list(WORK.glob("sdalr_*")) + list(WORK.glob("weight_*")):
    shutil.rmtree(p, ignore_errors=True)
