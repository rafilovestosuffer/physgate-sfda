"""C104: same-condition, bearing-disjoint control (PROTOCOL C104, pre-registered before this run).

Holds the operating condition identical on both sides, so the only thing that differs between the leaky and the clean
target is whether the bearings were seen in training. Random forest on the ten time statistics of C91 (set T), trained on
the TRAIN half of the source bearings' recordings (CRC32 parity of record_id, as C87/C97), tested at the same condition on
the held-out recordings of the same bearings (leaky) and of the complementary bearings (clean). Balanced accuracy.
CPU, from the M1 window files. Writes results/c104/.
"""
from __future__ import annotations

import itertools
import json
import zlib
from pathlib import Path

import numpy as np
import yaml
from scipy.stats import kurtosis, skew
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "c104"
CONDS = ["N15_M01_F10", "N15_M07_F04", "N15_M07_F10"]
CLASSES = ["normal", "inner_race", "outer_race"]
PITTING, PLASTIC = {"KA04", "KA16", "KA22"}, {"KA15", "KA30"}


def feats(X):   # identical to kaggle/kernels/c91_shallow_cpu.py set T
    ab = np.abs(X)
    rms = np.sqrt((X ** 2).mean(1))
    pk = ab.max(1)
    return np.c_[X.mean(1), X.std(1), rms, pk, X.max(1) - X.min(1), skew(X, 1), kurtosis(X, 1), pk / rms,
                 rms / ab.mean(1), pk / ab.mean(1)]


def load():
    """{cond: dict(F, y, bearing, record, test_half)} pooled over both fold files, so all 17 bearings are present."""
    out = {}
    for c in CONDS:
        parts = []
        for fold in "AB":
            d = np.load(ROOT / "data" / "m1" / f"PU_M1_fold{fold}_{c}.npz", allow_pickle=True)
            names = [str(n) for n in d["class_names"]]
            y = np.array([CLASSES.index(names[i]) for i in d["y"]])
            parts.append((feats(d["X"].astype(np.float64)), y, d["bearing_id"].astype(str), d["record_id"].astype(str)))
        F, y, b, r = (np.concatenate(z) for z in zip(*parts))
        te = np.array([zlib.crc32(x.encode()) % 2 == 1 for x in r])
        out[c] = {"F": F, "y": y, "b": b, "r": r, "te": te}
    return out


def bal_acc(y, p):
    return float(np.mean([(p[y == k] == k).mean() for k in np.unique(y)]))


def splits():
    cfg = yaml.safe_load(open(ROOT / "configs" / "splits_k10.yaml", encoding="utf-8"))["splits"]
    out = {s: ({b for v in d["source"].values() for b in v}, {b for v in d["target"].values() for b in v})
           for s, d in cfg.items()}
    folds = yaml.safe_load(open(ROOT / "configs" / "splits.yaml", encoding="utf-8"))
    return out, folds


def fold_sets():
    import sys
    sys.path.insert(0, str(ROOT / "data_prep"))
    from make_m1 import fold_bearings
    a = {b for v in fold_bearings("A").values() for b in v}
    bb = {b for v in fold_bearings("B").values() for b in v}
    return {"fold A": (a, bb), "fold B": (bb, a)}


def run_one(D, src, tgt):
    per_cond, or_recall = {}, {"pitting": [], "plastic": []}
    for c in CONDS:
        d = D[c]
        s_tr = np.isin(d["b"], list(src)) & ~d["te"]
        leak = np.isin(d["b"], list(src)) & d["te"]
        clean = np.isin(d["b"], list(tgt)) & d["te"]
        clf = RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(d["F"][s_tr], d["y"][s_tr])
        pl, pc = clf.predict(d["F"][leak]), clf.predict(d["F"][clean])
        per_cond[c] = {"leaky": 100 * bal_acc(d["y"][leak], pl), "clean": 100 * bal_acc(d["y"][clean], pc)}
        for grp, bs in (("pitting", PITTING), ("plastic", PLASTIC)):
            m = np.isin(d["b"][clean], list(bs & tgt))
            if m.any():
                or_recall[grp].append(float((pc[m] == CLASSES.index("outer_race")).mean()))
    lk = np.mean([v["leaky"] for v in per_cond.values()])
    cl = np.mean([v["clean"] for v in per_cond.values()])
    return {"per_condition": per_cond, "leaky": lk, "clean": cl, "delta": lk - cl,
            "outer_recall_clean": {k: (float(np.mean(v)) if v else None) for k, v in or_recall.items()}}


def sign_flip_p(x):
    x = np.asarray(x)
    obs = x.mean()
    null = [np.mean(x * np.array(s)) for s in itertools.product([1, -1], repeat=len(x))]
    return float(np.mean(np.array(null) >= obs - 1e-12))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    D = load()
    k10, _ = splits()
    res = {s: run_one(D, src, tgt) for s, (src, tgt) in k10.items()}
    fres = {f: run_one(D, src, tgt) for f, (src, tgt) in fold_sets().items()}
    deltas = np.array([res[s]["delta"] for s in sorted(res)])
    med, p = float(np.median(deltas)), sign_flip_p(deltas)
    decision = "IDENTITY ALONE PRODUCES THE COLLAPSE" if (med >= 10 and p < 0.05) else \
        "NOT MET: part of the collapse is condition shift"
    c101 = json.load(open(ROOT / "results" / "c101" / "c101_rf_splits.json", encoding="utf-8"))["T"]
    cross = {s: c101["rows"][s]["leaky"] - c101["rows"][s]["clean"] for s in c101["splits"]}
    json.dump({"splits": res, "folds": fres, "median_delta": med, "p": p, "positive": int((deltas > 0).sum()),
               "decision": decision, "cross_condition_rf_delta": cross}, open(OUT / "c104_same_condition.json", "w"),
              indent=1)
    L = ["# C104 - same-condition, bearing-disjoint control", "",
         "Random forest, ten time statistics, trained on half of the source bearings' recordings at one condition and",
         "tested at the SAME condition. Balanced accuracy (%), mean over the three conditions.", "",
         "| Split | Leaky (same bearings, held-out recordings) | Clean (other bearings) | Delta same-condition | "
         "Delta cross-condition (C101) |", "|---|---|---|---|---|"]
    for s in sorted(res):
        r = res[s]
        L.append(f"| {s} | {r['leaky']:.1f} | {r['clean']:.1f} | {r['delta']:.1f} | {cross.get(s, float('nan')):.1f} |")
    for f, r in fres.items():
        L.append(f"| {f} | {r['leaky']:.1f} | {r['clean']:.1f} | {r['delta']:.1f} | -- |")
    pit = [r["outer_recall_clean"]["pitting"] for r in list(res.values()) + list(fres.values())
           if r["outer_recall_clean"]["pitting"] is not None]
    pla = [r["outer_recall_clean"]["plastic"] for r in list(res.values()) + list(fres.values())
           if r["outer_recall_clean"]["plastic"] is not None]
    L += ["", f"Ten splits: median Delta_same **{med:.1f} pp**, positive in {(deltas > 0).sum()}/10, exact sign-flip "
              f"p = {p:.4f}. Cross-condition RF (C101, same features): median {np.median(list(cross.values())):.1f} pp.",
          "", f"Pre-registered rule (median >= 10 pp and p < 0.05): **{decision}**.", "",
          "## Secondary (descriptive): outer-race recall on clean targets, by damage mechanism", "",
          f"- fatigue pitting (KA04, KA16, KA22): median {100 * np.median(pit):.0f} % over {len(pit)} target sets",
          f"- plastic deformation (KA15, KA30): median {100 * np.median(pla):.0f} % over {len(pla)} target sets", ""]
    (OUT / "C104_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
