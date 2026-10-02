"""Kaggle CPU kernel: C110 source-diversity learning curve (PROTOCOL C110, pre-registered before this run).

Random forest on the ten C91 time statistics, same-condition design of C104 (record halves by CRC32 parity of record_id).
30 test triples (one healthy, one outer, one inner bearing), n in {1,2,3,4} source bearings per class from the remaining
pools, two draws per (triple, n), each of the three adaptation conditions. Balanced accuracy on the test triple (clean)
and on the held-out records of the training bearings (leaky). Writes /kaggle/working/c110/c110_result.json.
"""
import itertools
import json
import time
import zlib
from pathlib import Path

import numpy as np
from scipy.stats import kurtosis, skew
from sklearn.ensemble import RandomForestClassifier

OUT = Path("/kaggle/working/c110"); OUT.mkdir(parents=True, exist_ok=True)
D = next(Path("/kaggle/input").rglob("PU_M1_foldA_N15_M01_F10.npz")).parent
CONDS = ["N15_M01_F10", "N15_M07_F04", "N15_M07_F10"]
CLASSES = ["normal", "inner_race", "outer_race"]
POOLS = {"normal": ["K001", "K002", "K003", "K004", "K005", "K006"],
         "outer_race": ["KA04", "KA15", "KA16", "KA22", "KA30"],
         "inner_race": ["KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]}
N_TRIPLES, DRAWS, NS = 30, 2, (1, 2, 3, 4)
t0 = time.time()


def feats(X):
    X = X.astype(np.float64)
    ab = np.abs(X); rms = np.sqrt((X ** 2).mean(1)); pk = ab.max(1)
    return np.c_[X.mean(1), X.std(1), rms, pk, X.max(1) - X.min(1), skew(X, 1), kurtosis(X, 1), pk / rms,
                 rms / ab.mean(1), pk / ab.mean(1)]


def bal_acc(y, p):
    return float(np.mean([(p[y == k] == k).mean() for k in np.unique(y)]))


data = {}
for c in CONDS:
    parts = []
    for fold in "AB":
        d = np.load(D / f"PU_M1_fold{fold}_{c}.npz", allow_pickle=True)
        names = [str(n) for n in d["class_names"]]
        y = np.array([CLASSES.index(names[i]) for i in d["y"]])
        parts.append((feats(d["X"]), y, d["bearing_id"].astype(str), d["record_id"].astype(str)))
    F, y, b, r = (np.concatenate(z) for z in zip(*parts))
    te = np.array([zlib.crc32(x.encode()) % 2 == 1 for x in r])
    data[c] = {"F": F, "y": y, "b": b, "te": te}
print("features", round(time.time() - t0), "s", {c: len(v["y"]) for c, v in data.items()}, flush=True)

rng = np.random.default_rng(110)
all_triples = list(itertools.product(POOLS["normal"], POOLS["outer_race"], POOLS["inner_race"]))
triples = [all_triples[i] for i in rng.choice(len(all_triples), N_TRIPLES, replace=False)]
rows = []
for ti, tri in enumerate(triples):
    rest = {k: [x for x in POOLS[k] if x not in tri] for k in POOLS}
    for n in NS:
        for dr in range(DRAWS):
            src = [x for k in POOLS for x in rng.choice(rest[k], min(n, len(rest[k])), replace=False)]
            per = {}
            for c in CONDS:
                d = data[c]
                tr = np.isin(d["b"], src) & ~d["te"]
                lk = np.isin(d["b"], src) & d["te"]
                cl = np.isin(d["b"], list(tri)) & d["te"]
                clf = RandomForestClassifier(300, n_jobs=-1, random_state=0).fit(d["F"][tr], d["y"][tr])
                per[c] = {"clean": bal_acc(d["y"][cl], clf.predict(d["F"][cl])),
                          "leaky": bal_acc(d["y"][lk], clf.predict(d["F"][lk])), "n_train": int(tr.sum())}
            rows.append({"triple": list(tri), "n": n, "draw": dr, "source": [str(x) for x in src], "per_condition": per,
                         "clean": float(np.mean([v["clean"] for v in per.values()])),
                         "leaky": float(np.mean([v["leaky"] for v in per.values()]))})
    print(f"triple {ti + 1}/{N_TRIPLES}", round(time.time() - t0), "s", flush=True)
    (OUT / "c110_result.json").write_text(json.dumps({"triples": [list(t) for t in triples], "rows": rows}, indent=1))

# Decision statistic (C110): per triple, clean BA(n=4) - clean BA(n=1), averaged over draws and conditions.
by = {}
for r in rows:
    by.setdefault(tuple(r["triple"]), {}).setdefault(r["n"], []).append(r)
diff = np.array([100 * (np.mean([x["clean"] for x in v[4]]) - np.mean([x["clean"] for x in v[1]])) for v in by.values()])
flips = np.random.default_rng(0).choice([-1, 1], size=(100000, len(diff)))
p = float(((flips * diff).mean(1) >= diff.mean() - 1e-12).mean())
med = float(np.median(diff))
decision = "DIVERSITY IMPROVES TRANSFER" if (med >= 5 and p < 0.05) else ("FLAT" if abs(med) < 2 else "INCONCLUSIVE")
curve = {n: {"clean_median": float(100 * np.median([np.mean([x["clean"] for x in v[n]]) for v in by.values()])),
             "leaky_median": float(100 * np.median([np.mean([x["leaky"] for x in v[n]]) for v in by.values()]))}
         for n in NS}
summary = {"diff_n4_minus_n1": diff.round(3).tolist(), "median_diff_pp": med, "p_one_sided": p, "decision": decision,
           "curve": curve, "elapsed_s": round(time.time() - t0)}
(OUT / "c110_result.json").write_text(json.dumps({"triples": [list(t) for t in triples], "rows": rows,
                                                  "summary": summary}, indent=1))
print(json.dumps(summary, indent=1), flush=True)
