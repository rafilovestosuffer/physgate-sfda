"""Kaggle kernel: C94 HUST replication of the leakage design. Builds Track-R windows from the public HUST mirror, then runs
SDALR final_checkpoint leaky/clean for K = 6 bearing-type splits (source 3 types, clean target the other 2).

Views: HUST_M1_fold{Hk}_{PU domain name}.npz (H1 = 0 W, H2 = 200 W, H3 = 400 W) (source types) and ...fold{Hk}c_... (complement). Seed 2024.
"""
import itertools, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

import numpy as np
import scipy.io as sio

WORK = Path("/kaggle/working/hust"); WORK.mkdir(parents=True, exist_ok=True)
DATA = WORK / "npz"; DATA.mkdir(exist_ok=True)
runner = next(Path("/kaggle/input").rglob("sdalr_runner.py"))
sdalr = next(Path("/kaggle/input").rglob("tar_adaptation_RES_PU.py")).parent
src_dir = next(p for p in Path("/kaggle/input").rglob("N400.mat")).parent
W = 2048; PER_CLASS = 2000
CLASSES = [("N", 0), ("I", 1), ("O", 2)]          # normal, inner, outer (L3)
TYPES = ["4", "5", "6", "7", "8"]                  # 6204 .. 6208, one physical bearing each
# view file names use the PU script's domain names (runner CFG HUST_M1): H1 = 0 W, H2 = 200 W, H3 = 400 W
LOADS = {"N15_M01_F10": "0", "N15_M07_F04": "2", "N15_M07_F10": "4"}

rng = np.random.default_rng(20260919)
draws = list(itertools.combinations(TYPES, 3))
SPLITS = [draws[i] for i in rng.choice(len(draws), size=6, replace=False)]
print("splits", SPLITS, flush=True)


def windows(files, n_per_class):
    """Even split of n_per_class windows over the given files; no window crosses a record boundary."""
    per = [n_per_class // len(files) + (1 if i < n_per_class % len(files) else 0) for i in range(len(files))]
    X, rid, bid, ov = [], [], [], []
    for f, k in zip(files, per):
        m = sio.loadmat(f)
        x = np.asarray(m["data"], dtype=np.float32).ravel()
        starts = np.linspace(0, len(x) - W, k).astype(int)
        ov.append(max(0.0, 1.0 - float(np.diff(starts).min()) / W) if k > 1 else 0.0)
        X.append(np.stack([x[s:s + W] for s in starts]))
        rid += [f.stem] * k
        bid += [f.stem[-3]] * k                    # bearing type digit = physical bearing identity
    return np.concatenate(X), rid, bid, float(max(ov))


def build(view, types):
    for dom, ld in LOADS.items():
        p = DATA / f"HUST_M1_fold{view}_{dom}.npz"
        if p.exists():
            continue
        Xs, ys, rids, bids, ovs = [], [], [], [], []
        for pre, y in CLASSES:
            files = [src_dir / f"{pre}{t}0{ld}.mat" for t in types]
            files = [f for f in files if f.exists()]
            assert len(files) == len(types), f"missing files for {pre} {types} {ld}"
            X, rid, bid, o = windows(files, PER_CLASS)
            Xs.append(X); ys += [y] * len(X); rids += rid; bids += bid; ovs.append(o)
        np.savez(p, X=np.concatenate(Xs), y=np.asarray(ys, np.int64), bearing_id=np.asarray(bids),
                 record_id=np.asarray(rids), class_names=np.asarray([c for c, _ in CLASSES]),
                 overlap=np.asarray(ovs, np.float32))
        print("built", p.name, "max within-record overlap %.2f" % max(ovs), flush=True)


import torch
env = {"device": torch.cuda.get_device_name(0), "capability": list(torch.cuda.get_device_capability(0))}
print(env, flush=True)
assert env["device"] == "Tesla T4", f"refusing to run on {env['device']}"
log = []
for i, types in enumerate(SPLITS):
    view = f"H{i}"
    other = [t for t in TYPES if t not in types]
    build(view, list(types)); build(view + "c", other)
    w = WORK / view
    for j, tgt in enumerate((view, view + "c")):
        t0 = time.time()
        cmd = [sys.executable, "-u", str(runner), "--sdalr", str(sdalr), "--m0", str(DATA), "--dataset", "HUST_M1",
               "--src-fold", view, "--tgt-fold", tgt, "--variant", "final_checkpoint", "--work", str(w), "--seed", "2024"] + \
              ([] if j == 0 else ["--skip-pretrain"])
        print("RUN", " ".join(cmd), flush=True)
        rc = subprocess.run(cmd, env={**os.environ, "PYTHONUTF8": "1"}).returncode
        log.append({"split": view, "types": list(types), "tgt": tgt, "rc": rc, "seconds": round(time.time() - t0)})
        print(log[-1], flush=True)
        (WORK / "kernel_log_hust.json").write_text(json.dumps({"env": env, "splits": [list(s) for s in SPLITS], "runs": log}, indent=2))
    for p in list(w.glob("sdalr_*")) + list(w.glob("weight_*")):
        shutil.rmtree(p, ignore_errors=True)
shutil.rmtree(DATA, ignore_errors=True)
print("done", json.dumps(log), flush=True)
