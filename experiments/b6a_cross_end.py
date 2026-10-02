"""B6a (PROTOCOL C52) -- does the CWRU fan-end sensor carry the drive-end fault signature?

Tests the assumption behind Vieira et al. (MSSP 2026)'s CWRU healthy split. Pre-registered in C52.
Primary: FE channel of DE-fault records, gated with DE (6205) kinematics, L4, alpha 0.05, cepstrum arm.
Outcome: gate accepts the DE record's true fault family. Measurable iff Wilson 95 % lower bound > alpha.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep")]
import band_select, comb, cwru, prewhiten, ses  # noqa: E402,E401
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402

ALPHA, T_SEC = 0.05, 5.0
OUT = ROOT / "results" / "b6a"
FAMILY_OF = {"outer_race": "outer_race", "inner_race": "inner_race", "ball": "ball"}


def wilson(k, n, z=1.96):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def load_fe():
    """cwru.load raises on files without FE_time; load record by record and keep those that have it."""
    import scipy.io as sio
    ops = json.load(io.open(cwru.OPS, encoding="utf-8"))
    labs = json.load(io.open(cwru.LABELS, encoding="utf-8"))
    recs, skipped = [], []
    for o in ops:
        m = sio.loadmat(cwru.DATA / o["cache_filename"])
        key = o["internal_mat_key"].replace("_DE_", "_FE_")
        if key not in m:
            skipped.append(str(o["file_id"]))
            continue
        rpm_keys = [k for k in m if k.endswith("RPM")]
        rpm = float(np.asarray(m[rpm_keys[0]]).ravel()[0]) if rpm_keys else float(o["nominal_rpm"])
        lab = labs[o["opaque_id"]]
        recs.append(dict(record_id=str(o["file_id"]), fault_type=lab["fault_type"],
                         size=lab.get("fault_diameter_in"), load=o["load_hp"], fs=float(o["fs_hz"]),
                         rpm=rpm, rpm_source="measured_in_file" if rpm_keys else "nominal_table",
                         x=np.asarray(m[key], dtype=np.float64).ravel()))
    return recs, skipped


def gate(x, fs, rpm, bearing):
    k = kinematics(bearing)
    f_r = rpm / 60.0
    y = prewhiten.prewhiten(x[: int(T_SEC * fs)], "cepstrum")
    b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r)
    f, S = ses.squared_envelope_spectrum(y, fs, band=(b.lo_hz, b.hi_hz))
    return comb.decide(f, S, k, f_r, ALPHA, "L4"), b


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    recs, skipped = load_fe()
    rows = []
    for r in recs:
        if r["x"].size < int(T_SEC * r["fs"]):
            skipped.append(r["record_id"] + ":short")
            continue
        for bearing in ("6205", "6203"):
            v, b = gate(r["x"], r["fs"], r["rpm"], bearing)
            rows.append({"record_id": r["record_id"], "fault_type": r["fault_type"], "size_in": r["size"],
                         "load_hp": r["load"], "fs_hz": r["fs"], "rpm": round(r["rpm"], 1),
                         "rpm_source": r["rpm_source"], "kinematics": bearing,
                         "physical_class": v["physical_class"],
                         "accepts_true_de_family": int(r["fault_type"] in FAMILY_OF and v["physical_class"] == r["fault_type"]),
                         "any_fault_call": int(v["physical_class"] != "normal"),
                         "band_lo_hz": round(b.lo_hz, 1), "band_hi_hz": round(b.hi_hz, 1),
                         **{f"lines_{fam}": v["tests"][fam]["n_lines"] for fam in ("BPFO", "BPFI", "BPFB")},
                         **{f"p_{fam}": v["tests"][fam]["p"] for fam in ("BPFO", "BPFI", "BPFB")}})
        print(r["record_id"], r["fault_type"], [x["physical_class"] for x in rows[-2:]], flush=True)
    with io.open(OUT / "b6a_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    prim = [x for x in rows if x["kinematics"] == "6205" and x["fault_type"] in FAMILY_OF]
    k = sum(x["accepts_true_de_family"] for x in prim)
    p, lo, hi = wilson(k, len(prim))
    by = defaultdict(lambda: [0, 0])
    for x in prim:
        by[(x["fault_type"], x["size_in"])][0] += x["accepts_true_de_family"]; by[(x["fault_type"], x["size_in"])][1] += 1
    sec = {}
    for bearing in ("6205", "6203"):
        for grp, cond in (("de_fault_records", lambda x: x["fault_type"] in FAMILY_OF), ("normal_records", lambda x: x["fault_type"] == "normal")):
            R = [x for x in rows if x["kinematics"] == bearing and cond(x)]
            if R:
                n1 = sum(x["any_fault_call"] for x in R)
                sec[f"{bearing}|{grp}"] = {"n": len(R), "any_fault_call": n1, "rate_ci95": list(wilson(n1, len(R)))}
    summary = {"decision_rule": "PROTOCOL C52", "alpha": ALPHA, "n_primary": len(prim), "accepted": k,
               "rate": p, "wilson95": [lo, hi], "contamination_measurable": bool(lo > ALPHA),
               "by_fault_and_size": {f"{a}|{b}": {"accepted": v[0], "n": v[1]} for (a, b), v in sorted(by.items(), key=str)},
               "secondary": sec, "skipped": skipped}
    (OUT / "b6a_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
