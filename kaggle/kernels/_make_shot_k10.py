"""Generate SHOT split kernels (one Kaggle dataset per group, the same groups as C88).

C100 (v1 patch):  shot_k10_g1..g4   -> physgate-shot-k10-*   (retained for audit only)
C113 (v2 patch):  shot2_k10_g1..g4  -> physgate-shot2-k10-*  (index-aligned pseudo-labels; the kernel refuses a v1 patch)

Usage:  python kaggle/kernels/_make_shot_k10.py [c100|c113]   (default c113)
"""
import sys
from pathlib import Path

GROUPS = {"g1": ["S00", "S01", "S02"], "g2": ["S03", "S04", "S05"], "g3": ["S06", "S07"], "g4": ["S08", "S09"]}
T = '''"""Kaggle kernel: {cid} SHOT on the C88 splits, group {g} ({splits}).

Per split, two runs sharing one source model: leaky (the source split as target) and clean (its complement).
Seed 2024, variant `shot`, no gates. Results flush after every task to /kaggle/working/{work}/.
"""
import importlib.util, json, os, shutil, subprocess, sys, time
from pathlib import Path
SPLITS = {splits!r}
WORK = Path("/kaggle/working/{work}"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
_spec = importlib.util.spec_from_file_location("shot_patch", runner.parent / "shot_patch.py")
_sp = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_sp)
assert getattr(_sp, "SHOT_PATCH_VERSION", 1) >= {minver}, "refusing: shot_patch in the code dataset is older than v{minver} (C113)"
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
data = next(Path("/kaggle/input").rglob(f"PU_M1_fold{{SPLITS[0]}}_N15_M01_F10.npz")).parent
import torch
env = {{"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0)), "group": "{g}", "shot_patch_version": _sp.SHOT_PATCH_VERSION, "experiment": "{cid}"}}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {{env['device']}}"
log = []
for sid in SPLITS:
    w = WORK / sid
    for i, tgt in enumerate((sid, sid + "c")):
        t0 = time.time()
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(data), "--dataset", "PU_M1",
               "--src-fold", sid, "--tgt-fold", tgt, "--variant", "shot", "--work", str(w), "--seed", "2024"
               ] + ([] if i == 0 else ["--skip-pretrain"])
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={{**os.environ, "PYTHONUTF8": "1"}}).returncode
        log.append({{"split": sid, "tgt": tgt, "rc": rc, "seconds": round(time.time() - t0)}})
        (WORK / "kernel_log_{g}.json").write_text(json.dumps({{"env": env, "runs": log}}, indent=2))
    for p in list(w.glob("sdalr_*")) + list(w.glob("weight_*")):
        shutil.rmtree(p, ignore_errors=True)
print("done", json.dumps(log), flush=True)
'''

VARIANTS = {"c100": dict(cid="C100", prefix="shot_k10", work="shot_k10", minver=1),
            "c113": dict(cid="C113", prefix="shot2_k10", work="shot2_k10", minver=2)}
here = Path(__file__).resolve().parent
v = VARIANTS[(sys.argv[1] if len(sys.argv) > 1 else "c113").lower()]
for g, splits in GROUPS.items():
    (here / f"{v['prefix']}_{g}.py").write_text(T.format(g=g, splits=splits, **v), encoding="utf-8")
    print("wrote", f"{v['prefix']}_{g}.py", splits)
