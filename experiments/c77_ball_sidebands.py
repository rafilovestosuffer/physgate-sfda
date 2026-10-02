"""C77: BPFB family with J=2 (frozen) vs J=0, CWRU DE + UORED, cepstrum arm, comb C30 decision otherwise unchanged."""
import csv, io, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, cwru, prewhiten, ses, uored
from harmonic_coords import K_HARM, J_SIDE
from kinematics import kinematics
OUT = ROOT / "results" / "c77"; OUT.mkdir(parents=True, exist_ok=True)
_orig = comb.family_specs

def specs_ball_j0(k, label_space="L3", J=J_SIDE):
    return [comb.FamilySpec(s.name, s.order, 0, s.sb, s.scale_sb) if s.name == "BPFB" else s for s in _orig(k, label_space, J)]

def verdict(x, fs, rpm, bearing, f_hi=None):
    k = kinematics(bearing); fr = rpm / 60
    y = prewhiten.prewhiten(x, "cepstrum")
    kw = {"f_hi": f_hi} if f_hi else {}
    b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * fr, **kw)
    f, S = ses.squared_envelope_spectrum(y, fs, band=(b.lo_hz, b.hi_hz))
    comb.family_specs = _orig
    a = comb.decide(f, S, k, fr, 0.05, "L4")
    comb.family_specs = specs_ball_j0
    c = comb.decide(f, S, k, fr, 0.05, "L4")
    comb.family_specs = _orig
    return a["physical_class"], c["physical_class"], a["tests"]["BPFB"]["p"], c["tests"]["BPFB"]["p"]

ftf = {r["record_id"]: float(r["fr_ftf"]) * 60 for r in csv.DictReader(open(ROOT / "results/b7_uored/b7_ftf_records.csv")) if r["fr_ftf"]}
rows = []
for r in cwru.load():
    x = r.signal[: int(5 * r.fs_hz)].astype(np.float64)
    j2, j0, p2, p0 = verdict(x, r.fs_hz, r.rpm, r.bearing_model)
    rows.append(dict(dataset="CWRU", arm="measured", record_id=r.record_id, fault_type=r.fault_type, J2=j2, J0=j0, pB_J2=p2, pB_J0=p0))
for r in uored.load():
    x = r.signal.astype(np.float64)
    arms = [("logged", r.rpm)] + ([("ftf", ftf[r.record_id])] if r.record_id in ftf else [])
    for arm, rpm in arms:
        j2, j0, p2, p0 = verdict(x, r.fs_hz, rpm, r.bearing_model, 15000.0)
        rows.append(dict(dataset="UORED", arm=arm, record_id=r.record_id, fault_type=r.fault_type, J2=j2, J0=j0, pB_J2=p2, pB_J0=p0))
with io.open(OUT / "c77_records.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
summ = {}
for ds, arm in (("CWRU", "measured"), ("UORED", "logged"), ("UORED", "ftf")):
    R = [x for x in rows if x["dataset"] == ds and x["arm"] == arm]
    s = {}
    for J in ("J2", "J0"):
        s[J] = {"ball_detected": sum(x["fault_type"] == "ball" and x[J] == "ball" for x in R), "ball_n": sum(x["fault_type"] == "ball" for x in R),
                "healthy_FA": sum(x["fault_type"] == "normal" and x[J] != "normal" for x in R), "healthy_n": sum(x["fault_type"] == "normal" for x in R),
                "false_ball_calls_on_nonball": sum(x["fault_type"] != "ball" and x[J] == "ball" for x in R),
                "changed_nonball_verdicts": sum(x["fault_type"] != "ball" and x["J2"] != x["J0"] for x in R)}
    summ[f"{ds}|{arm}"] = s
(OUT / "c77_summary.json").write_text(json.dumps(summ, indent=2))
print(json.dumps(summ, indent=1))
