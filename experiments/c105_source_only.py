"""C105 - Source-only arm and the effect of adaptation on the leak (post-hoc, descriptive; no decision rule).

Every adaptation log records target accuracy at batch 0, before any update: the accuracy of the source model alone. The
leaky and clean arms of a split share that source model, so pre_leaky - pre_clean is the collapse WITHOUT adaptation,
and (adapted Delta) - (pre Delta) is what adaptation adds to it. Split = unit. Also records the cross-job provenance check:
pre-update accuracy of the fold job (physgate-m1-*) against the gating job (physgate-m2-*) for the same task.
Output: results/c105/c105_source_only.json
"""
from __future__ import annotations

import numpy as np

from rev6_load import ROOT, SPLITS, TASKS, boot_median_ci, dump, load, mean6, sign_flip_p


def summarise(rows):
    pre_d = np.array([r["pre_delta"] for r in rows])
    ad_d = np.array([r["adapted_delta"] for r in rows])
    amp = ad_d - pre_d
    cg = np.array([r["clean_adapt_gain"] for r in rows])
    lg = np.array([r["leaky_adapt_gain"] for r in rows])
    return {
        "median_pre_delta": float(np.median(pre_d)), "ci_pre_delta": boot_median_ci(pre_d),
        "pre_delta_positive": int((pre_d > 0).sum()), "p_pre_delta_greater": sign_flip_p(pre_d, "greater"),
        "median_adapted_delta": float(np.median(ad_d)),
        "median_amplification": float(np.median(amp)), "ci_amplification": boot_median_ci(amp),
        "amplification_positive": int((amp > 0).sum()), "p_amplification_two_sided": sign_flip_p(amp),
        "median_clean_adapt_gain": float(np.median(cg)), "clean_adapt_gain_positive": int((cg > 0).sum()),
        "median_leaky_adapt_gain": float(np.median(lg)),
        "mean_pre_leaky": float(np.mean([r["pre_leaky"] for r in rows])),
        "mean_pre_clean": float(np.mean([r["pre_clean"] for r in rows])),
    }


def row(L, C, name):
    pl, pc, al, ac = mean6(L, "pre"), mean6(C, "pre"), mean6(L, "adapted"), mean6(C, "adapted")
    return {"split": name, "pre_leaky": pl, "pre_clean": pc, "pre_delta": pl - pc, "adapted_leaky": al,
            "adapted_clean": ac, "adapted_delta": al - ac, "amplification": (al - ac) - (pl - pc),
            "clean_adapt_gain": ac - pc, "leaky_adapt_gain": al - pl}


def main():
    D = load()
    K, S, F = D["k10"], D["shot"], D["fold"]
    sdalr = [row(K[(s, s, "none")], K[(s, s + "c", "none")], s) for s in SPLITS]
    shot = [row(S[(s, s)], S[(s, s + "c")], s) for s in SPLITS]
    folds = []
    for f, o in (("A", "B"), ("B", "A")):
        job = f"m1-f{f.lower()}"
        folds.append(row(F[(job, f"result_PU_M1_final_checkpoint_F{f}to{f}_s2024")],
                         F[(job, f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024")], f"fold {f}"))
    prov = {}
    for f, o in (("A", "B"), ("B", "A")):
        stem = f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024"
        a, b = F[(f"m1-f{f.lower()}", stem)], F[(f"m2-f{f.lower()}", stem)]
        prov[f"fold {f}"] = {"fold_job_pre": [a["pre"][t] for t in TASKS], "gating_job_pre": [b["pre"][t] for t in TASKS],
                             "max_abs_pre_diff": float(max(abs(a["pre"][t] - b["pre"][t]) for t in TASKS)),
                             "fold_job_adapted_mean": mean6(a, "adapted"), "gating_job_adapted_mean": mean6(b, "adapted")}
    out = {"entry": "C105", "status": "post-hoc, descriptive",
           "sdalr_ten_splits": {"rows": sdalr, "summary": summarise(sdalr)},
           "shot_ten_splits": {"rows": shot, "summary": summarise(shot)},
           "sdalr_folds_fold_job": folds, "cross_job_pre_update": prov}
    dump(out, ROOT / "results" / "c105" / "c105_source_only.json")
    for k in ("sdalr_ten_splits", "shot_ten_splits"):
        print(k, {a: (round(b, 3) if isinstance(b, float) else b) for a, b in out[k]["summary"].items()})
    for r in folds:
        print(r["split"], {a: round(b, 2) for a, b in r.items() if isinstance(b, float)})
    for k, v in prov.items():
        print(k, "max |pre diff| fold vs gating job:", round(v["max_abs_pre_diff"], 2))


if __name__ == "__main__":
    main()
