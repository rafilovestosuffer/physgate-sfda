"""C78: CWRU fan-end (6203, lock-affected) vs drive-end (6205, immune) control. Frozen C30 + comb_v2 secondary."""
import csv, io, json, sys
from pathlib import Path
import numpy as np, scipy.io as sio
from scipy.stats import fisher_exact
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, comb_v2, cwru, prewhiten, ses
from harmonic_coords import K_HARM, J_SIDE
from kinematics import kinematics
OUT = ROOT / "results" / "c78"; OUT.mkdir(parents=True, exist_ok=True)
# Case Western 12k fan-end fault table (engineering.case.edu, read 2026-09-13)
FE = {}
for ids, ft, size, pos in (((278,279,280,281),"inner_race",.007,None), ((282,283,284,285),"ball",.007,None), ((294,295,296,297),"outer_race",.007,"@6"),
                           ((298,299,300,301),"outer_race",.007,"@3"), ((302,305,306,307),"outer_race",.007,"@12"), ((274,275,276,277),"inner_race",.014,None),
                           ((286,287,288,289),"ball",.014,None), ((313,),"outer_race",.014,"@6"), ((310,309,311,312),"outer_race",.014,"@3"),
                           ((270,271,272,273),"inner_race",.021,None), ((290,291,292,293),"ball",.021,None), ((315,),"outer_race",.021,"@6"),
                           ((316,317,318),"outer_race",.021,"@3")):
    for i in ids:
        FE[i] = (ft, f"fe_{ft}_{size}_{pos}")

def run(x, fs, rpm, bearing):
    k = kinematics(bearing); fr = rpm / 60; out = {}
    for arm in ("none", "cepstrum"):
        y = prewhiten.prewhiten(x, arm)
        b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * fr)
        f, S = ses.squared_envelope_spectrum(y, fs, band=(b.lo_hz, b.hi_hz))
        v1 = comb.decide(f, S, k, fr, 0.05, "L4"); v2 = comb_v2.decide(f, S, k, fr, 0.05, "L4")
        cls = v1["physical_class"]; fam = {"outer_race": "BPFO", "inner_race": "BPFI", "ball": "BPFB"}.get(cls)
        out[arm] = dict(c30=cls, v2=v2["physical_class"], winner_aliased=(v2["v2"][fam]["shaft_aliased_fraction"] >= 0.5) if fam else None)
    return out

rows = []
for i, (ft, bid) in sorted(FE.items()):
    m = sio.loadmat(ROOT / "data" / "cwru_fe" / f"{i}.mat")
    x = np.asarray(m[f"X{i:03d}_FE_time"], float).ravel()[:60000]; rpm = float(np.asarray(m[f"X{i:03d}RPM"]).ravel()[0])
    for arm, v in run(x, 12000.0, rpm, "6203").items():
        rows.append(dict(pop="FE_6203", record_id=i, bearing_id=bid, fault_type=ft, rpm=rpm, arm=arm, **v))
for r in cwru.load("DE"):
    if r.fs_hz != 12000.0 or r.fault_type == "normal":
        continue
    x = r.signal[:60000].astype(float)
    for arm, v in run(x, 12000.0, r.rpm, "6205").items():
        rows.append(dict(pop="DE_6205", record_id=r.record_id, bearing_id=r.bearing_id, fault_type=r.fault_type, rpm=r.rpm, arm=arm, **v))
with io.open(OUT / "c78_records.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
summ = {}
for arm in ("none", "cepstrum"):
    for gate in ("c30", "v2"):
        blk = {}
        for pop in ("FE_6203", "DE_6205"):
            R = [x for x in rows if x["pop"] == pop and x["arm"] == arm]
            IO = [x for x in R if x["fault_type"] in ("inner_race", "outer_race")]
            conf = sum((x["fault_type"] == "inner_race" and x[gate] == "outer_race") or (x["fault_type"] == "outer_race" and x[gate] == "inner_race") for x in IO)
            adm = [x for x in R if x["c30"] != "normal"]
            blk[pop] = {"n_IO": len(IO), "confusions": conf, "rate": conf / len(IO),
                        "correct_IO": sum(x[gate] == x["fault_type"] for x in IO),
                        "ball_detected": sum(x["fault_type"] == "ball" and x[gate] == "ball" for x in R), "ball_n": sum(x["fault_type"] == "ball" for x in R),
                        "c30_admitted": len(adm), "c30_admitted_shaft_aliased": sum(bool(x["winner_aliased"]) for x in adm)}
        a, b = blk["FE_6203"], blk["DE_6205"]
        p = fisher_exact([[a["confusions"], a["n_IO"] - a["confusions"]], [b["confusions"], b["n_IO"] - b["confusions"]]], alternative="greater")[1]
        blk["fisher_one_sided_p"] = p
        if gate == "c30":
            fa = a["c30_admitted_shaft_aliased"] / max(1, a["c30_admitted"]); fb = b["c30_admitted_shaft_aliased"] / max(1, b["c30_admitted"])
            blk["aliased_fraction_FE_DE"] = [fa, fb]
            blk["supported"] = bool(p < 0.05 and fa > fb)
        summ[f"{arm}|{gate}"] = blk
summ["decision"] = "PROTOCOL C78: primary = none|c30"
(OUT / "c78_summary.json").write_text(json.dumps(summ, indent=2, default=float))
print(json.dumps(summ, indent=1, default=float))
