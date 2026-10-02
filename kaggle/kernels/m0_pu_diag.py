"""Kaggle kernel: M0-PU diagnostic (results/M0_PU_RESULT.md). The two tasks INTO A2 (N15_M07_F04), where the
reproduction disagrees with the paper (A3->A2 -9.78 pp; A1->A2 +2.79 pp), x seeds {0,1,2} x threshold {0.4 script, 0.6 paper}.
as_released variant only (the paper's own selection rule). One process per (seed, threshold); results flushed per task."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
WORK = Path("/kaggle/working/m0diag"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
m0 = next(Path("/kaggle/input").rglob("PU_N15_M07_F04.npz")).parent
import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0))}
print(env, flush=True)
assert env["device"] == "Tesla T4"
log = []
for seed in ("0", "1", "2"):
    for thr in ("0.4", "0.6"):
        t0 = time.time()
        extra = [] if thr == "0.4" else ["--skip-pretrain"]      # source model depends on seed only
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(m0), "--dataset", "PU",
               "--variant", "as_released", "--work", str(WORK), "--seed", seed, "--threshold", thr,
               "--pairs", "1,2", "0,2", *extra]
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
        log.append({"seed": seed, "threshold": thr, "rc": rc, "seconds": round(time.time() - t0)})
        (WORK / "kernel_log.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))
for p in list(WORK.glob("sdalr_*")) + list(WORK.glob("weight_*")):
    shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
