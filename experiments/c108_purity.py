"""C108 - Is block labelling specific to unseen bearings? (post-hoc, descriptive; no decision rule)

Purity of a bearing = share of its windows receiving its most frequent predicted label. Computed for SDALR (final
checkpoint, seed 2024, ungated) on every leaky and clean arm of the ten C88 splits, (i) per task and (ii) pooled over the
six tasks of a split, and for both directions of the gating job (fold A and fold B as source). If block labelling were a
signature of unseen specimens, it would be frequent on clean arms and rare on leaky arms.
Output: results/c108/c108_purity.json
"""
from __future__ import annotations

import collections

import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, dump, load


def purity(a, pooled):
    vals = []
    groups = [TASKS] if pooled else [[t] for t in TASKS]
    for ts in groups:
        P = collections.defaultdict(list)
        C = {}
        for t in ts:
            p = a["preds"][t]
            bb = np.array([bearing_of(r) for r in p["rec"]])
            for b in np.unique(bb):
                m = bb == b
                P[b].append(p["pred"][m])
                C[b] = int(p["label"][m][0])
        for b, v in P.items():
            v = np.concatenate(v)
            c = np.bincount(v, minlength=3)
            vals.append({"bearing": b, "purity": float(c.max() / c.sum()), "majority_correct": bool(c.argmax() == C[b])})
    return vals


def stats(v):
    x = np.array([e["purity"] for e in v])
    return {"n": int(len(x)), "median": float(np.median(x)), "share_ge_0.99": float(np.mean(x >= 0.99)),
            "share_ge_0.9": float(np.mean(x >= 0.9)), "min": float(x.min())}


def main():
    K = load()["k10"]
    F = load()["fold"]
    res = {}
    for side, suf in (("leaky", ""), ("clean", "c")):
        for pooled in (False, True):
            v = [e for s in SPLITS for e in purity(K[(s, s + suf, "none")], pooled)]
            res[f"{side}_{'pooled_over_tasks' if pooled else 'per_task'}"] = stats(v)
    folds = {}
    for f, o in (("A", "B"), ("B", "A")):
        a = F[(f"m2-f{f.lower()}", f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024")]
        folds[f"source fold {f}"] = {e["bearing"]: round(e["purity"], 3) for e in purity(a, True)}
    out = {"entry": "C108", "status": "post-hoc, descriptive", "ten_splits": res, "gating_job_directions_pooled": folds}
    dump(out, ROOT / "results" / "c108" / "c108_purity.json")
    for k, v in res.items():
        print(k, v)
    for k, v in folds.items():
        print(k, v)


if __name__ == "__main__":
    main()
