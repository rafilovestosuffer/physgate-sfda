"""H6 -- does discrete/random separation rescue the physics gate on the 6203 shaft-harmonic lock?

Pre-registered in PROTOCOL.md C28 (commit 3fe29ae) BEFORE any gate result on real data existed.
Implements C28 exactly; any deviation must be a new §13 entry, not an edit here.

Population : every PU single-fault record (29 bearings x 4 conditions x 20 = 2320), full 4 s record.
Pipeline   : [prewhiten arm] -> fast-kurtogram band -> SES (1 segment) -> harmonic-coordinate gate bins
             -> gate.decide(alpha=0.05, L3).
Arms       : prewhiten = none | cepstrum.
Primary    : outer-race gate precision = P(truly outer | gate says outer); chance = outer prevalence.
Decision   : SUPPORTED iff `none` CI contains prevalence AND `cepstrum` precision - prevalence >= 0.15
             with CI excluding prevalence. Wilson 95 % intervals.
"""
from __future__ import annotations

import csv
import io
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep")]

import band_select  # noqa: E402
import comb  # noqa: E402
import gate  # noqa: E402
import prewhiten  # noqa: E402
import pu  # noqa: E402
import ses  # noqa: E402
from harmonic_coords import harmonic_coordinates, K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402

ALPHA = 0.05
N_SAMPLES = 249_600       # C34: shortest readable single-fault record is 249,940; keep df identical for all
UNREADABLE = {"N15_M01_F10_KA08_2"}   # C34: malformed .mat in the Paderborn distribution (scipy TypeError)
PU_BAND_HI_HZ = 15000.0   # C33, from configs/datasets.yaml band_search_hz
ARMS = ("none", "cepstrum")
OUT = ROOT / "results" / os.environ.get("H6_OUT", "h6")   # C35 corrected-geometry run -> results/h6_c35
SINGLE_FAULT = ["K001", "K002", "K003", "K004", "K005", "K006",
                "KA01", "KA03", "KA05", "KA06", "KA07", "KA08", "KA09",
                "KI01", "KI03", "KI05", "KI07", "KI08",
                "KA04", "KA15", "KA16", "KA22", "KA30",
                "KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def process(path: str) -> list[dict]:
    r = pu.read_one(Path(path))
    k = kinematics(r.bearing_model)
    f_r = r.rpm / 60.0
    max_fault_hz = (K_HARM * k.BPFI + J_SIDE) * f_r
    n4 = N_SAMPLES                             # C34: uniform 249,600 samples = 3.9 s, df = 0.2564 Hz
    if r.signal.size < n4:
        raise ValueError(f"{r.record_id}: {r.signal.size} samples < {n4}")
    sig = r.signal[:n4]
    rows = []
    for arm in ARMS:
        y = prewhiten.prewhiten(sig, arm)
        band = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=max_fault_hz,
                                       f_lo=0.0, f_hi=PU_BAND_HI_HZ)   # C33: below 16 kHz inverter switching
        f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(band.lo_hz, band.hi_hz))
        v = comb.decide(f, S, k, f_r, ALPHA, "L3")   # C31: frozen C30 detector
        rows.append({
            "record_id": r.record_id, "bearing_id": r.bearing_id, "damage_origin": r.meta["damage_origin"],
            "fault_type": r.fault_type, "condition": r.condition, "rpm": round(r.rpm, 2), "arm": arm, "geometry": r.bearing_model,
            "band_lo_hz": round(band.lo_hz, 1), "band_hi_hz": round(band.hi_hz, 1),
            "band_kurtosis": round(band.kurtosis, 4), "physical_class": v["physical_class"],
            "p_BPFO": v["tests"]["BPFO"]["p"], "excess_BPFO": v["tests"]["BPFO"]["excess"], "lines_BPFO": v["tests"]["BPFO"]["n_lines"], "delta_BPFO": v["tests"]["BPFO"]["best_delta"],
            "p_BPFI": v["tests"]["BPFI"]["p"], "excess_BPFI": v["tests"]["BPFI"]["excess"], "lines_BPFI": v["tests"]["BPFI"]["n_lines"], "delta_BPFI": v["tests"]["BPFI"]["best_delta"],
        })
    return rows


def summarise(rows: list[dict]) -> dict:
    out = {}
    for arm in ARMS:
        R = [x for x in rows if x["arm"] == arm]
        n = len(R)
        prev = sum(x["fault_type"] == "outer_race" for x in R) / n
        said_outer = [x for x in R if x["physical_class"] == "outer_race"]
        tp = sum(x["fault_type"] == "outer_race" for x in said_outer)
        prec, lo, hi = wilson(tp, len(said_outer))
        said_inner = [x for x in R if x["physical_class"] == "inner_race"]
        tpi = sum(x["fault_type"] == "inner_race" for x in said_inner)
        prev_i = sum(x["fault_type"] == "inner_race" for x in R) / n
        confusion = {}
        for t in ("normal", "inner_race", "outer_race"):
            confusion[t] = {p: sum(1 for x in R if x["fault_type"] == t and x["physical_class"] == p)
                            for p in ("normal", "inner_race", "outer_race")}
        out[arm] = {
            "n_records": n, "outer_prevalence": prev, "gate_says_outer": len(said_outer),
            "outer_precision": prec, "outer_precision_ci95": [lo, hi],
            "at_chance": (lo <= prev <= hi) if not math.isnan(lo) else None,
            "materially_above": (prec - prev >= 0.15 and lo > prev) if not math.isnan(lo) else False,
            "inner_prevalence": prev_i, "gate_says_inner": len(said_inner),
            "inner_precision": wilson(tpi, len(said_inner))[0], "inner_precision_ci95": list(wilson(tpi, len(said_inner))[1:]),
            "confusion_true_to_gate": confusion,
            "fraction_called_normal": sum(x["physical_class"] == "normal" for x in R) / n,
        }
    for arm in ARMS:   # C31: real-data null for claim 3
        H = [x for x in rows if x["arm"] == arm and x["fault_type"] == "normal"]
        fa = sum(x["physical_class"] != "normal" for x in H)
        r, lo, hi = wilson(fa, len(H))
        out[arm]["healthy_false_acceptance"] = {"n": len(H), "false": fa, "rate": r, "ci95": [lo, hi]}
    supported = bool(out["none"]["at_chance"]) and bool(out["cepstrum"]["materially_above"])
    return {"arms": out, "H6_supported": supported, "decision_rule": "PROTOCOL C28 via C31", "alpha": ALPHA}


def main() -> int:
    missing = [b for b in SINGLE_FAULT if not (pu.DATA / b).is_dir() or len(list((pu.DATA / b).glob("*.mat"))) < 80]
    if missing:
        raise SystemExit(f"REFUSED: C28 fixes the population as all 29 single-fault bearings; missing {missing}")
    files = [str(p) for p in pu.files(bearings=SINGLE_FAULT) if p.stem not in UNREADABLE]
    assert len(files) == 29 * 80 - len(UNREADABLE), len(files)   # 2319 (C34)
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows: list[dict] = []
    with Pool(4) as pool:
        for i, rr in enumerate(pool.imap_unordered(process, files, chunksize=4), 1):
            rows.extend(rr)
            if i % 100 == 0:
                print(f"{i}/{len(files)} records, {time.time() - t0:.0f}s", flush=True)
    with io.open(OUT / "h6_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: (x["arm"], x["record_id"])))
    summary = summarise(rows)
    summary["seconds"] = round(time.time() - t0)
    (OUT / "h6_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
