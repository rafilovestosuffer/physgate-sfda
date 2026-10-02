"""Kaggle kernel: C88 K-split leakage, group g4 (['S08', 'S09']). Per split: pretrain + leaky none; clean none, pcv, oracle
(shared source model within a split). Seed 2024, final_checkpoint."""
import json, os, shutil, subprocess, sys, time
from pathlib import Path
SPLITS = ['S08', 'S09']
WORK = Path("/kaggle/working/k10"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
verdicts = next(Path("/kaggle/input").rglob("gate_verdicts.json"))
data = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SPLITS[0]}_N15_M01_F10.npz")).parent
import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)), "group": "g4"}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"
log = []
for sid in SPLITS:
    w = WORK / sid
    for i, (tgt, gate) in enumerate(((sid, "none"), (sid + "c", "none"), (sid + "c", "pcv"), (sid + "c", "oracle"))):
        t0 = time.time()
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(data), "--dataset", "PU_M1",
               "--src-fold", sid, "--tgt-fold", tgt, "--variant", "final_checkpoint", "--work", str(w), "--seed", "2024",
               "--gate", gate, "--gate-verdicts", str(verdicts)] + ([] if i == 0 else ["--skip-pretrain"])
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
        log.append({"split": sid, "tgt": tgt, "gate": gate, "rc": rc, "seconds": round(time.time() - t0)})
        (WORK / "kernel_log_g4.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))
    for p in list(w.glob("sdalr_*")) + list(w.glob("weight_*")):
        shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
