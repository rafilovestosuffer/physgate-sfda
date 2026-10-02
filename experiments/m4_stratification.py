"""M4 -- does the physics gate's agreement with ground truth track Smith & Randall's expert diagnosability?

Pre-registered in PROTOCOL.md C29 (commit 61961b8) BEFORE any gate result on CWRU existed.

Population : 64 CWRU DE records; first 5.000 s of each (uniform df = 0.2 Hz).
Pipeline   : H6 `cepstrum` arm, L4 families {BPFO, BPFI, BPFB}, alpha = 0.05, per-file RPM.
Outcome    : agreement = (gate physical class == true class).
Primary    : one-sided Spearman rho(ordinal grade, agreement) over the 60 fault records;
             SUPPORTED iff rho > 0 and p < 0.05.   Y1=4, Y2=3, P1/P2=2, N1/N2=1.
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
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep")]

import band_select, comb, cwru, gate, prewhiten, ses  # noqa: E402,E401
from harmonic_coords import harmonic_coordinates, K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402

ALPHA, T_SEC = 0.05, 5.0
ORD = {"Y1": 4, "Y2": 3, "P1": 2, "P2": 2, "N1": 1, "N2": 1}
OUT = ROOT / "results" / "m4b"   # C31: second run after the C29 defect; original kept in results/m4


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, c - h, c + h


def run_arm(records, arm):
    rows = []
    for r in records:
        k = kinematics(r.bearing_model)
        f_r = r.rpm / 60.0
        n = int(T_SEC * r.fs_hz)
        if r.signal.size < n:
            raise ValueError(f"{r.record_id}: shorter than {T_SEC} s")
        y = prewhiten.prewhiten(r.signal[:n], arm)
        band = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r)
        f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(band.lo_hz, band.hi_hz))
        v = comb.decide(f, S, k, f_r, ALPHA, "L4")   # C31: frozen C30 detector
        rows.append({
            "record_id": r.record_id, "arm": arm, "fault_type": r.fault_type,
            "fault_size_in": r.meta["fault_diameter_in"], "or_position": r.meta["or_position"],
            "load_hp": r.meta["load_hp"], "fs_hz": r.fs_hz, "rpm": round(r.rpm, 1), "rpm_source": r.rpm_source,
            "grade": r.meta["sr2015_grade"] or "normal", "physical_class": v["physical_class"],
            "agree": int(v["physical_class"] == r.fault_type),
            "band_lo_hz": band.lo_hz, "band_hi_hz": band.hi_hz, "band_kurtosis": round(band.kurtosis, 3),
            **{f"p_{fam}": v["tests"][fam]["p"] for fam in ("BPFO", "BPFI", "BPFB")},
            **{f"lines_{fam}": v["tests"][fam]["n_lines"] for fam in ("BPFO", "BPFI", "BPFB")},
            **{f"delta_{fam}": v["tests"][fam]["best_delta"] for fam in ("BPFO", "BPFI", "BPFB")},
        })
    return rows


def summarise(rows):
    out = {}
    for arm in sorted({x["arm"] for x in rows}):
        R = [x for x in rows if x["arm"] == arm]
        faults = [x for x in R if x["fault_type"] != "normal"]
        rho, p_two = spearmanr([ORD[x["grade"]] for x in faults], [x["agree"] for x in faults])
        p_one = p_two / 2 if rho > 0 else 1 - p_two / 2
        by_grade, by_type = defaultdict(list), defaultdict(list)
        for x in faults:
            by_grade[x["grade"]].append(x["agree"]); by_type[x["fault_type"]].append(x["agree"])
        normals = [x for x in R if x["fault_type"] == "normal"]
        out[arm] = {
            "spearman_rho": float(rho), "p_one_sided": float(p_one),
            "M4_supported": bool(rho > 0 and p_one < 0.05),
            "agreement_by_grade": {g: {"n": len(v), "rate": wilson(sum(v), len(v))[0],
                                       "ci95": list(wilson(sum(v), len(v))[1:])} for g, v in sorted(by_grade.items())},
            "agreement_by_fault_type": {t: {"n": len(v), "rate": wilson(sum(v), len(v))[0],
                                            "ci95": list(wilson(sum(v), len(v))[1:])} for t, v in sorted(by_type.items())},
            "normals_called_faulty": f"{sum(x['physical_class'] != 'normal' for x in normals)}/{len(normals)}",
            "overall_fault_agreement": sum(x["agree"] for x in faults) / len(faults),
        }
    return {"arms": out, "primary_arm": "cepstrum", "decision_rule": "PROTOCOL C29 via C31 (M4b)", "alpha": ALPHA,
            "grade_source": "predictive-maintenance-mcp sr2015_grade (collapsed; CC BY-NC-SA 4.0)"}


def main():
    recs = cwru.load()
    assert len(recs) == 64
    OUT.mkdir(parents=True, exist_ok=True)
    rows = run_arm(recs, "cepstrum") + run_arm(recs, "none")
    with io.open(OUT / "m4_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    s = summarise(rows)
    (OUT / "m4_summary.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(json.dumps(s, indent=2))


if __name__ == "__main__":
    main()
