"""C72 evaluation: comb_v2 beside the frozen C30 gate on identical spectra (cepstrum arm).

Populations: PU H6 C35 (2,319 records, 3.9 s, L3), CWRU M4b (64 DE records, 5 s, L4), UORED (60 records, 10 s, L4,
both speed arms). Each record's SES is computed once; both gates read the same (f, S).
"""
from __future__ import annotations

import csv
import io
import json
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, comb_v2, cwru, prewhiten, pu, ses, uored  # noqa: E402,E401
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402
from h6_prewhitening import N_SAMPLES, UNREADABLE, PU_BAND_HI_HZ, SINGLE_FAULT, wilson  # noqa: E402
from b7_uored import spectral_rpm  # noqa: E402

OUT = ROOT / "results" / "comb_v2"
ALPHA = 0.05


def verdicts(x, fs, rpm, bearing, space, f_hi=None):
    k = kinematics(bearing)
    f_r = rpm / 60.0
    y = prewhiten.prewhiten(x, "cepstrum")
    kw = {"f_hi": f_hi} if f_hi else {}
    b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r, **kw)
    f, S = ses.squared_envelope_spectrum(y, fs, band=(b.lo_hz, b.hi_hz))
    v1 = comb.decide(f, S, k, f_r, ALPHA, space)
    v2 = comb_v2.decide(f, S, k, f_r, ALPHA, space)
    return v1["physical_class"], v2["physical_class"], v2["v2"]


def pu_job(path):
    r = pu.read_one(Path(path))
    c1, c2, info = verdicts(r.signal[:N_SAMPLES].astype(np.float64), r.fs_hz, r.rpm, r.bearing_model, "L3", PU_BAND_HI_HZ)
    return {"dataset": "PU", "record_id": r.record_id, "bearing_id": r.bearing_id, "fault_type": r.fault_type,
            "speed": "measured", "c30": c1, "v2": c2,
            **{f"alias_{n}": round(v["shaft_aliased_fraction"], 3) for n, v in info.items()}}


def small_jobs():
    rows = []
    for r in cwru.load():
        n = int(5.0 * r.fs_hz)
        c1, c2, info = verdicts(r.signal[:n].astype(np.float64), r.fs_hz, r.rpm, r.bearing_model, "L4")
        rows.append({"dataset": "CWRU", "record_id": r.record_id, "bearing_id": r.bearing_id, "fault_type": r.fault_type,
                     "speed": r.rpm_source, "c30": c1, "v2": c2,
                     **{f"alias_{n}": round(v["shaft_aliased_fraction"], 3) for n, v in info.items()}})
    for r in uored.load():
        x = r.signal.astype(np.float64)
        for src, rpm in (("logged", r.rpm), ("spectral_1x", spectral_rpm(x, r.fs_hz))):
            c1, c2, info = verdicts(x, r.fs_hz, rpm, r.bearing_model, "L4", 15000.0)
            rows.append({"dataset": "UORED", "record_id": r.record_id, "bearing_id": r.bearing_id,
                         "fault_type": r.fault_type, "speed": src, "c30": c1, "v2": c2,
                         **{f"alias_{n}": round(v["shaft_aliased_fraction"], 3) for n, v in info.items()}})
    return rows


def block(R, key, classes):
    out = {}
    H = [x for x in R if x["fault_type"] == "normal"]
    fa = sum(x[key] != "normal" for x in H)
    out["healthy_FA"] = [fa, len(H)]
    for c in classes:
        said = [x for x in R if x[key] == c]
        tp = sum(x["fault_type"] == c for x in said)
        truth = [x for x in R if x["fault_type"] == c]
        eng = {x["bearing_id"] for x in truth if x[key] == c}
        out[c] = {"says": len(said), "tp": tp, "precision": wilson(tp, len(said))[0] if said else None,
                  "recall": tp / len(truth) if truth else None,
                  "bearings_engaged": f"{len(eng)}/{len({x['bearing_id'] for x in truth})}"}
    out["I->O"] = sum(x["fault_type"] == "inner_race" and x[key] == "outer_race" for x in R)
    out["O->I"] = sum(x["fault_type"] == "outer_race" and x[key] == "inner_race" for x in R)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = small_jobs()
    files = [str(p) for p in pu.files(bearings=SINGLE_FAULT) if p.stem not in UNREADABLE]
    with Pool(4) as pool:
        rows += pool.map(pu_job, files, chunksize=4)
    keys = sorted({k for r in rows for k in r})
    with io.open(OUT / "v2_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    summary = {}
    for (ds, sp), cls in ((("PU", "measured"), ("outer_race", "inner_race")),
                          (("CWRU", "measured_in_file"), ("outer_race", "inner_race", "ball")),
                          (("CWRU", "nominal_table"), ("outer_race", "inner_race", "ball")),
                          (("UORED", "logged"), ("outer_race", "inner_race", "ball")),
                          (("UORED", "spectral_1x"), ("outer_race", "inner_race", "ball"))):
        R = [x for x in rows if x["dataset"] == ds and x["speed"] == sp]
        if R:
            summary[f"{ds}|{sp}"] = {"n": len(R), "c30": block(R, "c30", cls), "v2": block(R, "v2", cls)}
    cw = [x for x in rows if x["dataset"] == "CWRU"]
    summary["CWRU|all"] = {"n": len(cw), "c30": block(cw, "c30", ("outer_race", "inner_race", "ball")),
                           "v2": block(cw, "v2", ("outer_race", "inner_race", "ball"))}
    (OUT / "v2_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
