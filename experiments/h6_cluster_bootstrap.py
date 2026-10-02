"""Disclosure analysis for H6 (not a decision rule): records within a bearing are not independent
(80 per bearing), so record-level Wilson CIs are too narrow. Bearing-cluster bootstrap, 10,000 resamples."""
import csv, io, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
run = sys.argv[1] if len(sys.argv) > 1 else "h6_c35"
R = list(csv.DictReader(io.open(ROOT / "results" / run / "h6_records.csv", encoding="utf-8")))
rng = np.random.default_rng(20260913)
out = {}
for arm in ("none", "cepstrum"):
    X = [x for x in R if x["arm"] == arm]
    by = {}
    for x in X:
        by.setdefault(x["bearing_id"], []).append(x)
    B = sorted(by)
    def stats(ids):
        rows = [x for b in ids for x in by[b]]
        so = [x for x in rows if x["physical_class"] == "outer_race"]
        prec = np.mean([x["fault_type"] == "outer_race" for x in so]) if so else np.nan
        prev = np.mean([x["fault_type"] == "outer_race" for x in rows])
        return prec, prev
    p0, v0 = stats(B)
    boot = np.array([stats(list(rng.choice(B, size=len(B), replace=True))) for _ in range(10000)])
    diff = boot[:, 0] - boot[:, 1]
    speaking = sorted({x["bearing_id"] for x in X if x["physical_class"] != "normal" and x["fault_type"] != "normal"})
    out[arm] = {"outer_precision": p0, "prevalence": v0,
                "cluster_boot95_precision": [float(np.nanpercentile(boot[:, 0], 2.5)), float(np.nanpercentile(boot[:, 0], 97.5))],
                "cluster_boot95_precision_minus_prevalence": [float(np.nanpercentile(diff, 2.5)), float(np.nanpercentile(diff, 97.5))],
                "resamples_with_no_outer_call": int(np.isnan(boot[:, 0]).sum()),
                "n_bearings": len(B), "fault_bearings_with_any_fault_verdict": speaking}
(ROOT / "results" / run / "h6_cluster_bootstrap.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
