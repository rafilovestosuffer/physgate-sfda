"""Kaggle kernel: C113 SHOT on the C88 splits, group g2 (['S03', 'S04', 'S05']).

Per split, two runs sharing one source model: leaky (the source split as target) and clean (its complement).
Seed 2024, variant `shot`, no gates. Results flush after every task to /kaggle/working/shot2_k10/.
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path
SPLITS = ['S03', 'S04', 'S05']
WORK = Path("/kaggle/working/shot2_k10"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
_spec = importlib.util.spec_from_file_location("shot_patch", runner.parent / "shot_patch.py")
_sp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_sp)
assert getattr(_sp, "SHOT_PATCH_VERSION", 1) >= 2, "refusing: shot_patch in the code dataset is older than v2 (C113)"
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
data = next(Path("/kaggle/input").rglob(f"PU_M1_fold{SPLITS[0]}_N15_M01_F10.npz")).parent
import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)), "group": "g2", "shot_patch_version": _sp.SHOT_PATCH_VERSION, "experiment": "C113"}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"
log = []
for sid in SPLITS:
    w = WORK / sid
    for i, tgt in enumerate((sid, sid + "c")):
        t0 = time.time()
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(data), "--dataset", "PU_M1",
               "--src-fold", sid, "--tgt-fold", tgt, "--variant", "shot", "--work", str(w), "--seed", "2024"
               ] + ([] if i == 0 else ["--skip-pretrain"])
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
        log.append({"split": sid, "tgt": tgt, "rc": rc, "seconds": round(time.time() - t0)})
        (WORK / "kernel_log_g2.json").write_text(json.dumps({"env": env, "runs": log}, indent=2))
    for p in list(w.glob("sdalr_*")) + list(w.glob("weight_*")):
        shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
