"""Kaggle kernel: C103 — does pretraining inside the arm's own process change the adapted result?

Two runs of the IDENTICAL configuration (PU M1, source fold A, target fold B, final_checkpoint, gate none, seed 2024).
The only difference is the one C102 identified as the remaining structural difference between our two jobs:

  arm 1  pretrains in-process, then adapts            (as the gating job did)
  arm 2  loads arm 1's checkpoint with --skip-pretrain (as the fold job did)

If the two differ by >= 1.0 pp the cross-job gap is explained by the random state adaptation starts from; if they agree
to < 0.1 pp the explanation is rejected. Results flush after every task to /kaggle/working/c103/.
"""
import json, os, subprocess, sys, time
from pathlib import Path

WORK = Path("/kaggle/working/c103"); WORK.mkdir(parents=True, exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
data = next(Path("/kaggle/input").rglob("PU_M1_foldA_N15_M01_F10.npz")).parent
print("runner:", runner, "\nsdalr:", sdalr, "\ndata:", data, flush=True)

import torch  # noqa: E402
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0))}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"

log = []
for i, (label, extra) in enumerate((("pretrain_in_process", []), ("skip_pretrain", ["--skip-pretrain"]))):
    w = WORK / label
    if label == "skip_pretrain":
        # reuse arm 1's source checkpoint: same --work tree, so the runner finds it and skips
        w = WORK / "pretrain_in_process"
    t0 = time.time()
    cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(data), "--dataset", "PU_M1",
           "--src-fold", "A", "--tgt-fold", "B", "--variant", "final_checkpoint", "--work", str(w),
           "--seed", "2024", "--gate", "none", *extra]
    print("RUN", label, " ".join(cmd), flush=True)
    rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
    # the two arms write the same filename, so keep arm 1's result before arm 2 overwrites it
    src = w / "result_PU_M1_final_checkpoint_FAtoB_s2024.json"
    if src.exists():
        (WORK / f"result_{label}.json").write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        if label == "pretrain_in_process":
            src.unlink()          # force arm 2 to recompute rather than resume from arm 1's json
    log.append({"arm": label, "rc": rc, "seconds": round(time.time() - t0)})
    (WORK / "kernel_log_c103.json").write_text(json.dumps({"env": env, "runs": log}, indent=2), encoding="utf-8")

# report immediately in the kernel log, so the comparison is visible without downloading anything
try:
    a = json.loads((WORK / "result_pretrain_in_process.json").read_text(encoding="utf-8"))["adapted"]
    b = json.loads((WORK / "result_skip_pretrain.json").read_text(encoding="utf-8"))["adapted"]
    tasks = sorted(set(a) & set(b))
    d = [a[t] - b[t] for t in tasks]
    print("\nper task:", {t: round(a[t] - b[t], 3) for t in tasks}, flush=True)
    print(f"fold means: pretrain_in_process {sum(a[t] for t in tasks) / len(tasks):.3f} "
          f"vs skip_pretrain {sum(b[t] for t in tasks) / len(tasks):.3f} "
          f"-> difference {sum(d) / len(d):+.3f} pp", flush=True)
except Exception as exc:
    print("comparison failed:", exc, flush=True)
print("done", json.dumps(log), flush=True)
