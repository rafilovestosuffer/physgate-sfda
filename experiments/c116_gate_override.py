"""C116 - Gate-override comparison and gate gain by certifiable bearings (post-hoc, descriptive; no decision rule).

On the ten C88 clean (bearing-disjoint) targets:
  ungated   SDALR final checkpoint, seed 2024, no gate;
  gated     the same with the envelope threshold gate (z = 10) inside adaptation (C88 arm);
  override  the ungated predictions, with every window of a recording the gate certifies replaced by the gate's verdict;
  gated+override  the gated predictions with the same replacement.
Accuracy is SDALR's metric (mean per-class recall), averaged over the six tasks of a split. The override needs no
adaptation change and no target label: the verdict comes from the recording alone. Also the number of gate-certifiable
bearings (KA04, KA16, KI16, KI18; C106) in each clean target beside the in-loop gain, and its expectation under the C88
draw (2 of 5 outer-race and 3 of 6 inner-race bearings in every clean target).
Retained artifacts only (per-window predictions, results/m2/gate_verdicts.json, configs/splits_k10.yaml).
Output: results/c116/c116_gate_override.json
"""
from __future__ import annotations

import json

import numpy as np
import yaml

from c115_exact_intervals import order_ci
from rev6_load import ROOT, SPLITS, TASKS, dump, load

CLASS = {"normal": 0, "inner_race": 1, "outer_race": 2}
CERTIFIABLE = ("KA04", "KA16", "KI16", "KI18")


def bacc(pred, lab):
    return 100 * float(np.mean([np.mean(pred[lab == c] == c) for c in np.unique(lab)]))


def override(p, verdict):
    v = np.array([verdict[r] for r in p["rec"]])
    cert = np.isin(v, ("inner_race", "outer_race"))
    out = p["pred"].copy()
    out[cert] = np.array([CLASS[x] for x in v[cert]], dtype=out.dtype)
    return out, cert, v


def main():
    K = load()["k10"]
    verdict = json.loads((ROOT / "results" / "m2" / "gate_verdicts.json").read_text(encoding="utf-8"))["pcv"]
    splits = yaml.safe_load((ROOT / "configs" / "splits_k10.yaml").read_text(encoding="utf-8"))["splits"]
    rows = {}
    for s in SPLITS:
        u, g = K[(s, s + "c", "none")], K[(s, s + "c", "pcv")]
        acc = {k: [] for k in ("ungated", "gated", "override", "gated_override", "certified_pct", "verdict_precision_pct")}
        for t in TASKS:
            pu, pg = u["preds"][t], g["preds"][t]
            ou, cert, v = override(pu, verdict)
            og, _, _ = override(pg, verdict)
            acc["ungated"].append(bacc(pu["pred"], pu["label"]))
            acc["gated"].append(bacc(pg["pred"], pg["label"]))
            acc["override"].append(bacc(ou, pu["label"]))
            acc["gated_override"].append(bacc(og, pg["label"]))
            acc["certified_pct"].append(100 * float(cert.mean()))
            if cert.any():
                acc["verdict_precision_pct"].append(100 * float(np.mean(ou[cert] == pu["label"][cert])))
        m = {k: (float(np.mean(v)) if v else None) for k, v in acc.items()}
        target = {b for cls in splits[s]["target"].values() for b in cls}
        m["certifiable_in_target"] = sorted(target & set(CERTIFIABLE))
        for k in ("gated", "override", "gated_override"):
            m[f"{k}_gain"] = m[k] - m["ungated"]
        rows[s] = m
    summary = {}
    for k in ("gated_gain", "override_gain", "gated_override_gain"):
        x = [rows[s][k] for s in SPLITS]
        summary[k] = {"median_pp": float(np.median(x)), "positive": int(sum(v > 0 for v in x)),
                      "order_statistic_interval": order_ci(x)}
    d = [rows[s]["override_gain"] - rows[s]["gated_gain"] for s in SPLITS]
    summary["override_minus_gated"] = {"median_pp": float(np.median(d)), "override_higher": int(sum(v > 0 for v in d))}
    by_count = {}
    for s in SPLITS:
        by_count.setdefault(len(rows[s]["certifiable_in_target"]), []).append(round(rows[s]["gated_gain"], 2))
    summary["gated_gain_by_certifiable_count"] = {str(k): sorted(v) for k, v in sorted(by_count.items())}
    summary["certifiable_per_target_mean"] = float(np.mean([len(rows[s]["certifiable_in_target"]) for s in SPLITS]))
    summary["certifiable_per_target_expected"] = 2 * 2 / 5 + 2 * 3 / 6   # KA04, KA16 of 5 outer (2 drawn); KI16, KI18 of 6 inner (3)
    # SDALR's own reliability split, as logged by the gate hook in every pseudo-labelling round of the gated arms
    share = []
    for s in SPLITS:
        log = json.loads((ROOT / K[(s, s + "c", "pcv")]["path"]).read_text(encoding="utf-8"))["gate_log"]
        share += [100 * r["sdalr_rejected"] / r["n"] for t in TASKS for r in log[t]]
    summary["sdalr_unreliable_share_per_round_pct"] = {"rounds": len(share), "median": float(np.median(share)),
                                                       "p95": float(np.percentile(share, 95)), "max": float(np.max(share)),
                                                       "rounds_above_10pct": int(sum(v > 10 for v in share))}
    # seed check on the two mechanical folds, where three seeds exist (gating jobs: 2024 in m2, 0 and 1 in m2seed)
    from rev6_load import arm
    art = ROOT / "results" / "artifacts"
    seeds = {}
    for seed in (0, 1, 2024):
        gains = {"gated": [], "override": []}
        for f, o in (("A", "B"), ("B", "A")):
            base = (art / f"physgate-m2-f{f.lower()}" / "m2" if seed == 2024
                    else art / f"physgate-m2seed-f{f.lower()}-s{seed}" / "m2rep" / f"reps{seed}")
            u = arm(base / f"result_PU_M1_final_checkpoint_F{f}to{o}_s{seed}.json")
            g = arm(base / f"result_PU_M1_final_checkpoint_F{f}to{o}_gatepcv_s{seed}.json")
            for t in TASKS:
                pu, pg = u["preds"][t], g["preds"][t]
                ou, _, _ = override(pu, verdict)
                base_acc = bacc(pu["pred"], pu["label"])
                gains["gated"].append(bacc(pg["pred"], pg["label"]) - base_acc)
                gains["override"].append(bacc(ou, pu["label"]) - base_acc)
        dg = np.array(gains["override"]) - np.array(gains["gated"])
        seeds[str(seed)] = {"tasks": len(dg), "mean_gated_gain_pp": float(np.mean(gains["gated"])),
                            "mean_override_gain_pp": float(np.mean(gains["override"])),
                            "tasks_override_higher": int((dg > 0).sum()), "tasks_tied": int((np.abs(dg) < 1e-9).sum())}
    summary["fold_seed_check"] = seeds
    out = {"entry": "C116", "status": "post-hoc, descriptive", "gate": "envelope threshold rule (pcv), z = 10",
           "rows": rows, "summary": summary}
    dump(out, ROOT / "results" / "c116" / "c116_gate_override.json")
    for s in SPLITS:
        r = rows[s]
        print(f"{s}: ungated {r['ungated']:.2f} gated {r['gated_gain']:+.2f} override {r['override_gain']:+.2f} "
              f"gated+override {r['gated_override_gain']:+.2f} cert {r['certified_pct']:.1f}% {r['certifiable_in_target']}")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
