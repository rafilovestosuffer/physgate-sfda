"""Kaggle CPU kernel: C92 (C91 features on C88 splits) shallow non-adaptive baseline on the M1 paired design (no GPU). Writes /kaggle/working/c91/."""
import json, time
from pathlib import Path
import numpy as np
from scipy.signal import hilbert
from scipy.stats import kurtosis, skew, wilcoxon
from sklearn.ensemble import RandomForestClassifier

OUT = Path("/kaggle/working/c92"); OUT.mkdir(parents=True, exist_ok=True)
COND = {"A1": "N15_M01_F10", "A2": "N15_M07_F04", "A3": "N15_M07_F10"}
TASKS = [("A1", "A3"), ("A1", "A2"), ("A3", "A1"), ("A3", "A2"), ("A2", "A1"), ("A2", "A3")]
t0 = time.time()


def feats(X):
    X = X.astype(np.float64)
    ab = np.abs(X); rms = np.sqrt((X ** 2).mean(1)); pk = ab.max(1)
    T = np.c_[X.mean(1), X.std(1), rms, pk, X.max(1) - X.min(1), skew(X, 1), kurtosis(X, 1), pk / rms, rms / ab.mean(1), pk / ab.mean(1)]
    M = np.abs(np.fft.rfft(X, axis=1))[:, 1:1025]
    F = np.log(M.reshape(len(X), 64, 16).mean(2) + 1e-12)
    env = np.abs(hilbert(X, axis=1)) ** 2
    env -= env.mean(1, keepdims=True)
    E = np.log(np.abs(np.fft.rfft(env, axis=1))[:, 1:65] + 1e-12)
    return {"T": T, "F": F, "E": E, "TFE": np.c_[T, F, E]}


import re
files = {p.name: p for p in Path("/kaggle/input").rglob("PU_M1_foldS*_N15_*.npz")}
splits = sorted({re.match(r"PU_M1_fold(S\d\d)_", n).group(1) for n in files if re.match(r"PU_M1_fold(S\d\d)_", n)})
print("splits", splits, flush=True)
res = {}
for sid in splits:
    cache = {}
    for view in (sid, sid + "c"):
        for a, c in COND.items():
            d = np.load(files[f"PU_M1_fold{view}_{c}.npz"])
            cache[(view, a)] = (feats(d["X"]), d["y"])
    res[sid] = {}
    for fs in ("T", "TFE"):
        rows = []
        for s, t in TASKS:
            clf = RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(cache[(sid, s)][0][fs], cache[(sid, s)][1])
            rows.append({"task": f"{s}->{t}", "leaky": 100 * float((clf.predict(cache[(sid, t)][0][fs]) == cache[(sid, t)][1]).mean()),
                         "clean": 100 * float((clf.predict(cache[(sid + "c", t)][0][fs]) == cache[(sid + "c", t)][1]).mean())})
        res[sid][fs] = {"rows": rows, "leaky_mean": float(np.mean([r["leaky"] for r in rows])),
                        "clean_mean": float(np.mean([r["clean"] for r in rows]))}
        print(sid, fs, round(res[sid][fs]["leaky_mean"], 2), round(res[sid][fs]["clean_mean"], 2), round(time.time() - t0), "s", flush=True)
    (OUT / "c92_result.json").write_text(json.dumps(res, indent=2))
print("done", round(time.time() - t0), "s")
