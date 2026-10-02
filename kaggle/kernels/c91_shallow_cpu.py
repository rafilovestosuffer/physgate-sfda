"""Kaggle CPU kernel: C91 shallow non-adaptive baseline on the M1 paired design (no GPU). Writes /kaggle/working/c91/."""
import json, time
from pathlib import Path
import numpy as np
from scipy.signal import hilbert
from scipy.stats import kurtosis, skew, wilcoxon
from sklearn.ensemble import RandomForestClassifier

OUT = Path("/kaggle/working/c91"); OUT.mkdir(parents=True, exist_ok=True)
D = next(Path("/kaggle/input").rglob("PU_M1_foldA_N15_M01_F10.npz")).parent
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


cache = {}
for fold in "AB":
    for a, c in COND.items():
        d = np.load(D / f"PU_M1_fold{fold}_{c}.npz")
        cache[(fold, a)] = (feats(d["X"]), d["y"], d["bearing_id"])
print("features", round(time.time() - t0), "s", flush=True)

res = {}
for fs in ("T", "F", "E", "TFE"):
    rows = []
    for fold, other in (("A", "B"), ("B", "A")):
        for s, t in TASKS:
            Xs, ys, _ = cache[(fold, s)]
            clf = RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(Xs[fs], ys)
            Xl, yl, _ = cache[(fold, t)]
            Xc, yc, bc = cache[(other, t)]
            pc = clf.predict(Xc[fs])
            purity = {b: float(np.bincount(pc[bc == b]).max() / (bc == b).sum()) for b in np.unique(bc)}
            rows.append({"src_fold": fold, "task": f"{s}->{t}", "leaky": 100 * float((clf.predict(Xl[fs]) == yl).mean()),
                         "clean": 100 * float((pc == yc).mean()), "clean_purity": purity})
    L = np.array([r["leaky"] for r in rows]); C = np.array([r["clean"] for r in rows])
    res[fs] = {"rows": rows, "leaky_mean": L.mean(), "clean_mean": C.mean(), "delta": L.mean() - C.mean(),
               "wilcoxon_p": float(wilcoxon(L, C, alternative="greater", zero_method="zsplit").pvalue),
               "mean_clean_purity": float(np.mean([np.mean(list(r["clean_purity"].values())) for r in rows]))}
    print(fs, {k: v for k, v in res[fs].items() if k != "rows"}, round(time.time() - t0), "s", flush=True)
    (OUT / "c91_result.json").write_text(json.dumps(res, indent=2))
print("done", round(time.time() - t0), "s")
