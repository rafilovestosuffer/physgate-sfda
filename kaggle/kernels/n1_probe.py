"""Kaggle kernel: C87 negative control N1 -- bearing-ID probes (all-bearing and within-class) on UN-REMEDIATED SDALR source
models, both M1 source folds, seed 2024, pretrain only (no adaptation, no BIST)."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
WORK = Path("/kaggle/working/n1"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m1 = next(Path("/kaggle/input").rglob("PU_M1_foldA_N15_M01_F10.npz")).parent
import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0))}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"
log = []
for src, tgt in (("A", "B"), ("B", "A")):
    t0 = time.time()
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m1), "--dataset", "PU_M1", "--src-fold", src,
           "--tgt-fold", tgt, "--variant", "final_checkpoint", "--work", str(WORK / f"F{src}"), "--seed", "2024", "--probe",
           "--pretrain-only"]
    print("RUN", " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    log.append({"src": src, "rc": rc, "seconds": round(time.time() - t0)})
    (WORK / "kernel_log.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))
for p in list(WORK.rglob("sdalr_*")) + list(WORK.rglob("weight_*")):
    shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
