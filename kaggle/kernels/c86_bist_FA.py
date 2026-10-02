"""Kaggle kernel: C86 BIST on the M1 paired design, one SOURCE fold per kernel.
  1. SDALR final_checkpoint, baseline source model with identity probe   (leaky F->F, clean F->F')
  2. SDALR final_checkpoint, BIST source model (+probe)                  (leaky, clean)
  3. SHOT on the BIST source model                                       (leaky, clean)   [SHOT baseline = C85 kernel]
"""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
SRC_FOLD = "A"
OTHER = {"A": "B", "B": "A"}[SRC_FOLD]
WORK = Path("/kaggle/working/c86"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m1 = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SRC_FOLD}_N15_M01_F10.npz")).parent
import torch
assert torch.cuda.get_device_name(0) == "Tesla T4"
plan = [("final_checkpoint", SRC_FOLD, ["--probe"]), ("final_checkpoint", OTHER, ["--probe", "--skip-pretrain"]),
        ("final_checkpoint", SRC_FOLD, ["--bist"]), ("final_checkpoint", OTHER, ["--bist", "--skip-pretrain"]),
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
