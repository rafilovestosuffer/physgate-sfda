"""C114 - Labels SDALR gives each bearing when seen and when unseen, and a KI04/KI14 sensitivity (post-hoc, descriptive).

(a) For every one of the 17 Paderborn bearings, the share of its windows predicted healthy, inner race and outer race by
    ungated SDALR (final checkpoint, seed 2024), pooled over every task of every C88 split in which it is unseen (clean
    target) and in which it is seen (leaky target). This shows whether the unseen-bearing error is a missed fault or a
    confusion between the two fault families.
(b) KI04 and KI14 carry particle-caused indentations on the outer ring besides inner-ring pitting (datasheet page 2,
    combination M). The split-level gap is recomputed with their windows dropped from both targets, each alone and both.

Reads retained artifacts only (per-window prediction dumps, via rev6_load); no training, no GPU. Accuracy is SDALR's
metric, the mean per-class recall over the remaining windows of a task, averaged over the six tasks of a split.
Output: results/c114/c114_unseen_labels.json and results/c114/c114_table.md (the S6.10 table).
"""
from __future__ import annotations

import collections
import json

import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, dump, load, sign_flip_p

CLASSES = ("healthy", "inner", "outer")
TRUE = {"K0": "healthy", "KA": "outer", "KI": "inner"}


def bacc(pred, lab):
    return 100 * float(np.mean([np.mean(pred[lab == c] == c) for c in np.unique(lab)]))


def shares(K, arm_of):
    cnt = collections.defaultdict(lambda: np.zeros(3))
    tasks = collections.Counter()
    for s in SPLITS:
        for t in TASKS:
            p = K[arm_of(s)]["preds"][t]
            b = np.array([bearing_of(r) for r in p["rec"]])
            for bid in np.unique(b):
                cnt[bid] += np.bincount(p["pred"][b == bid], minlength=3)
                tasks[bid] += 1
    return {bid: {"windows": int(v.sum()), "tasks": tasks[bid],
                  **{c: float(100 * v[i] / v.sum()) for i, c in enumerate(CLASSES)}} for bid, v in sorted(cnt.items())}


def gap(K, drop=()):
    out = []
    for s in SPLITS:
        acc = []
        for arm in ((s, s, "none"), (s, s + "c", "none")):
            per = []
            for t in TASKS:
                p = K[arm]["preds"][t]
                keep = np.array([bearing_of(r) not in drop for r in p["rec"]])
                per.append(bacc(p["pred"][keep], p["label"][keep]))
            acc.append(np.mean(per))
        out.append(acc[0] - acc[1])
    return out


def main():
    K = load()["k10"]
    unseen = shares(K, lambda s: (s, s + "c", "none"))
    seen = shares(K, lambda s: (s, s, "none"))
    damaged = {b: v for b, v in unseen.items() if not b.startswith("K0")}
    worst = max(damaged, key=lambda b: damaged[b]["healthy"])
    other = {b: v["outer" if b.startswith("KI") else "inner"] for b, v in damaged.items()}
    summary = {
        "max_healthy_share_unseen_damaged_pct": damaged[worst]["healthy"], "max_healthy_share_bearing": worst,
        "ka22_healthy_share_unseen_pct": damaged["KA22"]["healthy"],
        "median_other_family_share_unseen_damaged_pct": float(np.median(list(other.values()))),
        "min_healthy_share_unseen_healthy_pct": min(v["healthy"] for b, v in unseen.items() if b.startswith("K0")),
    }
    sens = {}
    for name, drop in (("all", ()), ("without_KI04", ("KI04",)), ("without_KI14", ("KI14",)),
                       ("without_KI04_KI14", ("KI04", "KI14"))):
        g = gap(K, drop)
        sens[name] = {"median_pp": float(np.median(g)), "positive": int(sum(x > 0 for x in g)),
                      "p_sign_flip_greater": sign_flip_p(g, "greater"), "per_split": dict(zip(SPLITS, g))}
    out = {"entry": "C114", "status": "post-hoc, descriptive", "arms": "SDALR final_checkpoint, seed 2024, ungated",
           "unseen": unseen, "seen": seen, "summary": summary, "ki04_ki14_sensitivity": sens}
    dump(out, ROOT / "results" / "c114" / "c114_unseen_labels.json")

    L = ["| Bearing | True class | Unseen: healthy / inner / outer (%) | Seen: healthy / inner / outer (%) |",
         "|---|---|---|---|"]
    for b in unseen:
        u, v = unseen[b], seen[b]
        L.append(f"| {b} | {TRUE[b[:2]]} | {u['healthy']:.1f} / {u['inner']:.1f} / {u['outer']:.1f} | "
                 f"{v['healthy']:.1f} / {v['inner']:.1f} / {v['outer']:.1f} |")
    (ROOT / "results" / "c114" / "c114_table.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "per_split"} for k, v in sens.items()}, indent=1))


if __name__ == "__main__":
    main()
