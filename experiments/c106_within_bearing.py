"""C106 - Within-bearing seen-vs-unseen contrast and the per-bearing table (post-hoc, descriptive; no decision rule).

Leaky and clean targets contain different bearings, so leaky - clean mixes overlap with how hard each bearing set is.
Across the ten C88 splits every real-damage bearing is sometimes in the source (scored in the leaky arm) and sometimes
not (scored in the clean arm). Per bearing: mean window accuracy of SDALR (final checkpoint, seed 2024, ungated) when
seen minus when unseen, over the splits and tasks in which it occurs. Bearing = unit (n = 17); exact sign-flip p over
bearings. Caveat recorded: the seen and unseen scores come from different adaptation runs (different target batches),
and bearings share splits, so the bearings are not independent.

The per-bearing table adds manufacturer, damage mode, extent, length, width and characteristic read from page 2 of each
bearing's own Paderborn datasheet (data/pu/<B>/<B>.pdf), and envelope-gate certification at the three adaptation
conditions from the retained verdicts (results/m2/gate_verdicts.json).
Output: results/c106/c106_within_bearing.json
"""
from __future__ import annotations

import collections
import json

import fitz
import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, boot_median_ci, dump, load, sign_flip_p

ADAPT_CONDS = ("N15_M01_F10", "N15_M07_F04", "N15_M07_F10")


def sheet(b):
    lines = [l.strip() for p in fitz.open(ROOT / "data" / "pu" / b / f"{b}.pdf") for l in p.get_text().split("\n")]

    def after(label, skip=("mm", "-", "pc.", "", "°", "Unit")):
        for i, l in enumerate(lines):
            if l == label:
                for v in lines[i + 1:i + 5]:
                    if v not in skip:
                        return v
        return ""
    return {"manufacturer": after("Manufacturer"), "pitch_mm": after("Pitch circle diameter"),
            "mode": after("Mode"), "symptom": after("Symptom"), "extent": after("Extent of damage"),
            "length_mm": after("Length"), "width_mm": after("Width"), "characteristic": after("Characteristic of", skip=("mm", "-", "", "damage")),
            "combination": after("Damage combination")}


def main():
    D = load()
    K = D["k10"]
    acc = collections.defaultdict(lambda: {"seen": [], "unseen": []})
    for s in SPLITS:
        for side, key in (("seen", (s, s, "none")), ("unseen", (s, s + "c", "none"))):
            for t in TASKS:
                p = K[key]["preds"][t]
                bb = np.array([bearing_of(r) for r in p["rec"]])
                for b in np.unique(bb):
                    m = bb == b
                    acc[b][side].append({"split": s, "task": t, "acc": float((p["pred"][m] == p["label"][m]).mean() * 100)})
    verdicts = json.loads((ROOT / "results" / "m2" / "gate_verdicts.json").read_text(encoding="utf-8"))
    rows = []
    for b in sorted(acc):
        se = [x["acc"] for x in acc[b]["seen"]]
        un = [x["acc"] for x in acc[b]["unseen"]]
        recs = [r for r in verdicts["pcv"] if bearing_of(r) == b and r[:11] in ADAPT_CONDS]
        cert = {g: sum(verdicts[g][r] != "normal" for r in recs) for g in ("pcv", "v2", "c30", "eagle")}
        truth = "normal" if b.startswith("K0") else ("outer_race" if b.startswith("KA") else "inner_race")
        correct = {g: sum(verdicts[g][r] == truth for r in recs) for g in ("pcv", "v2", "c30", "eagle")}
        row = {"bearing": b, "seen_acc": float(np.mean(se)), "unseen_acc": float(np.mean(un)),
               "diff": float(np.mean(se) - np.mean(un)), "n_splits_seen": len({x["split"] for x in acc[b]["seen"]}),
               "n_splits_unseen": len({x["split"] for x in acc[b]["unseen"]}), "records_adapt_conditions": len(recs),
               "fault_verdicts_adapt_conditions": cert, "correct_fault_verdicts_adapt_conditions": correct}
        row.update(sheet(b))
        rows.append(row)
    d = np.array([r["diff"] for r in rows])
    per_class = {}
    for cls, pre in (("healthy", "K0"), ("outer", "KA"), ("inner", "KI")):
        dd = np.array([r["diff"] for r in rows if r["bearing"].startswith(pre)])
        per_class[cls] = {"n": int(len(dd)), "median": float(np.median(dd)), "values": dd.round(2).tolist()}
    out = {"entry": "C106", "status": "post-hoc, descriptive", "method": "SDALR final_checkpoint seed 2024, ungated",
           "rows": rows,
           "summary": {"n_bearings": int(len(d)), "median_diff": float(np.median(d)), "ci_median_diff": boot_median_ci(d),
                       "positive": int((d > 0.05).sum()), "ties_abs_lt_0.05": int((np.abs(d) <= 0.05).sum()),
                       "negative": int((d < -0.05).sum()),
                       "p_sign_flip_greater": sign_flip_p(d, "greater"), "p_sign_flip_two_sided": sign_flip_p(d)},
           "per_class": per_class}
    dump(out, ROOT / "results" / "c106" / "c106_within_bearing.json")
    for r in rows:
        print(f"{r['bearing']} {r['manufacturer']:<10} {r['mode']:<20} ext {r['extent']:<3} L{r['length_mm']:<4} W{r['width_mm']:<4} "
              f"{r['characteristic']:<14} seen {r['seen_acc']:6.1f} unseen {r['unseen_acc']:6.1f} diff {r['diff']:+6.1f} "
              f"pcv {r['fault_verdicts_adapt_conditions']['pcv']}({r['correct_fault_verdicts_adapt_conditions']['pcv']})/{r['records_adapt_conditions']} "
              f"v2 {r['fault_verdicts_adapt_conditions']['v2']} c30 {r['fault_verdicts_adapt_conditions']['c30']} eagle {r['fault_verdicts_adapt_conditions']['eagle']}")
    print(out["summary"], per_class)


if __name__ == "__main__":
    main()
