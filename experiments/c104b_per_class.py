"""C104b (POST-HOC, descriptive; added after the C104 rule was evaluated, in response to review round 5).

Question: does the same-condition collapse survive inside a single damage mechanism? Per Lessmeier et al. (2016) Table 5,
all six real inner-race bearings are fatigue pitting, and healthy bearings carry no damage at all. If recall on unseen
bearings falls within those classes, the C104 loss cannot be explained by a change of damage mechanism there. Same design,
same forest, same record halves as C104; per-class recall instead of balanced accuracy. Writes results/c104/C104B_*.
"""
from __future__ import annotations

import json

import numpy as np

import c104_same_condition as C
from sklearn.ensemble import RandomForestClassifier


def main():
    D = C.load()
    k10, _ = C.splits()
    rows = {}
    for s, (src, tgt) in sorted(k10.items()):
        rec = {k: {"leaky": [], "clean": []} for k in C.CLASSES}
        for c in C.CONDS:
            d = D[c]
            tr = np.isin(d["b"], list(src)) & ~d["te"]
            clf = RandomForestClassifier(500, n_jobs=-1, random_state=0).fit(d["F"][tr], d["y"][tr])
            for arm, bs in (("leaky", src), ("clean", tgt)):
                m = np.isin(d["b"], list(bs)) & d["te"]
                p = clf.predict(d["F"][m]); y = d["y"][m]
                for k, name in enumerate(C.CLASSES):
                    rec[name][arm].append(float((p[y == k] == k).mean()))
        rows[s] = {n: {a: 100 * float(np.mean(v)) for a, v in r.items()} for n, r in rec.items()}
    out = {"splits": rows}
    L = ["# C104b (post-hoc, descriptive): same-condition recall per class", "",
         "Same design as C104. Recall (%) on held-out recordings of seen bearings (leaky) and of unseen bearings (clean),",
         "mean over the three conditions, median over the ten splits. Inner race is mechanism-homogeneous (all fatigue",
         "pitting, Lessmeier et al. 2016 Table 5); healthy bearings carry no damage.", "",
         "| Class | Leaky recall | Clean recall | Drop (median of per-split drops) | Splits with a drop |", "|---|---|---|---|---|"]
    for n in C.CLASSES:
        lk = np.array([rows[s][n]["leaky"] for s in rows]); cl = np.array([rows[s][n]["clean"] for s in rows])
        d = lk - cl
        out[n] = {"leaky_median": float(np.median(lk)), "clean_median": float(np.median(cl)),
                  "drop_median": float(np.median(d)), "positive": int((d > 0).sum()), "p": C.sign_flip_p(d)}
        L.append(f"| {n} | {np.median(lk):.1f} | {np.median(cl):.1f} | {np.median(d):.1f} | {(d > 0).sum()}/10 "
                 f"(sign-flip p = {out[n]['p']:.4f}) |")
    json.dump(out, open(C.OUT / "c104b_per_class.json", "w"), indent=1)
    (C.OUT / "C104B_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
