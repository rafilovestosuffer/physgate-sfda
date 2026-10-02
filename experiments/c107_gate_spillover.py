"""C107 - Where the envelope-gate gain comes from, and a label-free coverage (post-hoc, descriptive; no decision rule).

(a) Spillover. In each of the ten C88 splits the clean arm is run ungated and with the envelope threshold rule (pcv).
Windows are grouped by their record's gate verdict: certified (a fault verdict), uncovered faulty, uncovered healthy.
The split's gain is decomposed into the contributions of the three groups (count share x within-group accuracy change).
SFDA scores the windows it adapts on, so a gain on certified windows is partly the gate's own label; only a gain on
uncovered windows would show that the gate improved what the model learned about records it said nothing about.
(b) Coverage. C98 reported coverage as fault verdicts on faulty target records / faulty target records, which needs target
labels. The label-free version is fault verdicts / all target records. Both are correlated with the per-split gain
(Spearman, split = unit), with leave-one-split-out ranges and the textbook partial Spearman correlation against headroom
(oracle - ungated clean) with df = n - 3. Also lists which bearings carry each split's certified records.
Output: results/c107/c107_gate_spillover.json
"""
from __future__ import annotations

import collections
import json

import numpy as np
from scipy.stats import spearmanr
from scipy.stats import t as tdist

from rev6_load import ROOT, SPLITS, TASKS, bearing_of, dump, load, mean6

GROUPS = ("certified", "uncovered_faulty", "uncovered_healthy")


def spill(u, g, verdict):
    n = {k: 0 for k in GROUPS}
    cu = {k: 0 for k in GROUPS}
    cg = {k: 0 for k in GROUPS}
    by_bearing = collections.Counter()
    for t in TASKS:
        for which, a in (("u", u), ("g", g)):
            p = a["preds"][t]
            v = np.array([verdict[r] for r in p["rec"]])
            lab = p["label"]
            grp = np.where(v != "normal", "certified", np.where(lab == 0, "uncovered_healthy", "uncovered_faulty"))
            for k in GROUPS:
                m = grp == k
                hit = int((p["pred"][m] == lab[m]).sum())
                if which == "u":
                    n[k] += int(m.sum())
                    cu[k] += hit
                else:
                    cg[k] += hit
            if which == "u":
                for r in p["rec"][v != "normal"]:
                    by_bearing[bearing_of(r)] += 1
    N = sum(n.values())
    out = {}
    for k in GROUPS:
        acc_u = 100 * cu[k] / n[k] if n[k] else None
        acc_g = 100 * cg[k] / n[k] if n[k] else None
        out[k] = {"windows": n[k], "share": n[k] / N, "acc_ungated": acc_u, "acc_gated": acc_g,
                  "change": (acc_g - acc_u) if n[k] else 0.0,
                  "contribution_pp": (n[k] / N) * ((acc_g - acc_u) if n[k] else 0.0)}
    total = {"ungated": 100 * sum(cu.values()) / N, "gated": 100 * sum(cg.values()) / N}
    return out, total, dict(by_bearing)


def partial_spearman(x, y, z):
    r = lambda a, b: spearmanr(a, b)[0]
    pr = (r(x, y) - r(x, z) * r(y, z)) / np.sqrt((1 - r(x, z) ** 2) * (1 - r(y, z) ** 2))
    n = len(x)
    tt = pr * np.sqrt((n - 3) / (1 - pr ** 2))
    return float(pr), float(2 * tdist.sf(abs(tt), n - 3))


def main():
    D = load()
    K = D["k10"]
    verdict = json.loads((ROOT / "results" / "m2" / "gate_verdicts.json").read_text(encoding="utf-8"))["pcv"]
    c98 = json.loads((ROOT / "results" / "c98" / "c98_coverage.json").read_text(encoding="utf-8"))["pcv_class"]
    rows = []
    for s in SPLITS:
        u, g = K[(s, s + "c", "none")], K[(s, s + "c", "pcv")]
        grp, total, byb = spill(u, g, verdict)
        rows.append({"split": s, "groups": grp, "total": total, "certified_windows_by_bearing": byb,
                     "gain": mean6(g, "adapted") - mean6(u, "adapted"),
                     "headroom": mean6(K[(s, s + "c", "oracle")], "adapted") - mean6(u, "adapted"),
                     "coverage_faulty": c98[s]["spoke_share_faulty"], "coverage_all_label_free": c98[s]["spoke_share"]})
    summ = {}
    for k in GROUPS:
        ch = np.array([r["groups"][k]["change"] for r in rows if r["groups"][k]["windows"]])
        co = np.array([r["groups"][k]["contribution_pp"] for r in rows])
        summ[k] = {"median_change_pp": float(np.median(ch)), "mean_change_pp": float(ch.mean()),
                   "positive": int((ch > 0).sum()), "n": int(len(ch)),
                   "median_contribution_pp": float(np.median(co)), "sum_contribution_pp": float(co.sum())}
    tot = sum(summ[k]["sum_contribution_pp"] for k in GROUPS)
    summ["share_of_summed_gain_from_certified"] = summ["certified"]["sum_contribution_pp"] / tot
    gain = [r["gain"] for r in rows]
    head = [r["headroom"] for r in rows]
    cf = [r["coverage_faulty"] for r in rows]
    ca = [r["coverage_all_label_free"] for r in rows]
    cov = {}
    for name, c in (("faulty_denominator", cf), ("label_free_all_records", ca)):
        rho, p = spearmanr(c, gain)
        loo = [spearmanr(np.delete(c, i), np.delete(gain, i))[0] for i in range(len(c))]
        pr, pp = partial_spearman(c, gain, head)
        cov[name] = {"rho": float(rho), "p": float(p), "loo_min": float(min(loo)), "loo_max": float(max(loo)),
                     "partial_rho_given_headroom": pr, "partial_p": pp, "median_coverage": float(np.median(c))}
    rho_h, p_h = spearmanr(head, gain)
    prh, pph = partial_spearman(head, gain, cf)
    cov["headroom"] = {"rho": float(rho_h), "p": float(p_h), "partial_rho_given_coverage_faulty": prh, "partial_p": pph}
    out = {"entry": "C107", "status": "post-hoc, descriptive", "gate": "envelope threshold rule (pcv), z = 10",
           "rows": rows, "spillover_summary": summ, "coverage": cov}
    dump(out, ROOT / "results" / "c107" / "c107_gate_spillover.json")
    for r in rows:
        print(r["split"], f"gain {r['gain']:+.2f}", " | ".join(
            f"{k} {v['share']:.2f} {v['change']:+.1f} ({v['contribution_pp']:+.2f})" for k, v in r["groups"].items()),
            r["certified_windows_by_bearing"])
    print(json.dumps(summ, indent=1, default=float))
    print(json.dumps(cov, indent=1, default=float))


if __name__ == "__main__":
    main()
