"""C113 integrity check (post-hoc, descriptive; no decision rule): duplicate windows in the evaluation sets.

The Paderborn distribution contains byte-identical vibration signals under different record ids (KA04, N15_M07_F04:
records 5 = 19 and 6 = 15 = 20). They stay inside one bearing, so the bearing-wise split keeps every copy on one side,
but they re-weight the evaluation set. This recomputes every C113 split Delta_leak from the retained per-window
predictions, once on all windows and once keeping only the first copy of each identical window, and checks that the
prediction files reproduce the reported accuracies. Output: results/c113/c113_dedup_check.json
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
from c96_clustered_stats import cluster_bootstrap, sign_flip_p  # noqa: E402

DOM = ["N15_M01_F10", "N15_M07_F10", "N15_M07_F04"]           # SDALR code order (runners/sdalr_runner.py)
PL = {"N15_M01_F10": "A1", "N15_M07_F04": "A2", "N15_M07_F10": "A3"}
GROUP = {**{s: "g1" for s in ("S00", "S01", "S02")}, **{s: "g2" for s in ("S03", "S04", "S05")},
         **{s: "g3" for s in ("S06", "S07")}, **{s: "g4" for s in ("S08", "S09")}}


def arm(sid: str, tgt: str):
    base = ROOT / f"results/artifacts/physgate-shot2-k10-{GROUP[sid]}/shot2_k10/{sid}"
    reported = json.load(open(base / f"result_PU_M1_shot_F{sid}to{tgt}_s2024.json", encoding="utf-8"))["adapted"]
    full, dedup, dev, n_dup = {}, {}, 0.0, 0
    for s in range(3):
        for t in range(3):
            if s == t:
                continue
            p = np.load(base / f"logs_PU_M1_shot_F{sid}to{tgt}_s2024/pred_{s}{t}.npz")
            X = np.load(glob.glob(str(ROOT / f"data/k10/*/PU_M1_fold{tgt}_{DOM[t]}.npz"))[0])["X"]
            correct = p["prob"].argmax(1) == p["label"]
            h = np.array([hashlib.md5(X[i].tobytes()).hexdigest() for i in p["index"]])
            _, first = np.unique(h, return_index=True)
            k = f"{PL[DOM[s]]}->{PL[DOM[t]]}"
            full[k], dedup[k] = 100 * correct.mean(), 100 * correct[first].mean()
            dev = max(dev, abs(full[k] - reported[k]))
            n_dup = max(n_dup, len(h) - len(first))
    return full, dedup, dev, n_dup


def summary(clusters):
    m = [float(c.mean()) for c in clusters]
    mean, lo, hi = cluster_bootstrap(clusters)
    return {"median": float(np.median(m)), "mean": mean, "ci": [lo, hi], "p": sign_flip_p(clusters),
            "positive": int(sum(x > 0 for x in m)), "per_split": m}


def main() -> int:
    full, dedup, rows, maxdev = [], [], {}, 0.0
    for sid in sorted(GROUP):
        lf, ld, d1, n1 = arm(sid, sid)
        cf, cd, d2, n2 = arm(sid, sid + "c")
        full.append(np.array([lf[k] - cf[k] for k in lf]))
        dedup.append(np.array([ld[k] - cd[k] for k in ld]))
        maxdev = max(maxdev, d1, d2)
        rows[sid] = {"delta_full": float(full[-1].mean()), "delta_dedup": float(dedup[-1].mean()),
                     "max_duplicate_windows_leaky": n1, "max_duplicate_windows_clean": n2}
        print(sid, rows[sid])
    out = {"max_abs_pred_vs_reported_pp": maxdev, "full": summary(full), "dedup": summary(dedup), "rows": rows}
    (ROOT / "results/c113").mkdir(parents=True, exist_ok=True)
    (ROOT / "results/c113/c113_dedup_check.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("max_abs_pred_vs_reported_pp",)}),
          "full median %.2f, dedup median %.2f" % (out["full"]["median"], out["dedup"]["median"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
