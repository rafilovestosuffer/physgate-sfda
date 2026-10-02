"""C79 evaluation: kurtogram-band C30 vs target-informed band gate, cepstrum arm."""
import csv, io, json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np, scipy.io as sio
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, cwru, iesfo_gate, prewhiten, pu, ses, uored
from harmonic_coords import K_HARM, J_SIDE
from kinematics import kinematics
from c78_fe_de_control import FE
from h6_prewhitening import N_SAMPLES, PU_BAND_HI_HZ
OUT = ROOT / "results" / "c79"

def both(x, fs, rpm, bearing, space, f_hi):
    k = kinematics(bearing); fr = rpm / 60
    y = prewhiten.prewhiten(x, "cepstrum")
    kw = {"f_hi": f_hi} if f_hi else {}
    b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * fr, **kw)
    f, S = ses.squared_envelope_spectrum(y, fs, band=(b.lo_hz, b.hi_hz))
    return comb.decide(f, S, k, fr, 0.05, space)["physical_class"], iesfo_gate.decide(y, fs, k, fr, 0.05, space, f_hi)["physical_class"]

def job(j):
    ds, rid, ft, x, fs, rpm, bearing, space, f_hi, arm = j
    a, b = both(x, fs, rpm, bearing, space, f_hi)
    return dict(dataset=ds, arm=arm, record_id=rid, fault_type=ft, kurtogram=a, iesfo=b)

def jobs():
    J = []
    for r in cwru.load("DE"):
        J.append(("CWRU_DE", r.record_id, r.fault_type, r.signal[: int(5 * r.fs_hz)].astype(float), r.fs_hz, r.rpm, "6205", "L4", None, "measured"))
    for i, (ft, _) in sorted(FE.items()):
        m = sio.loadmat(ROOT / "data" / "cwru_fe" / f"{i}.mat")
        J.append(("CWRU_FE", str(i), ft, np.asarray(m[f"X{i:03d}_FE_time"], float).ravel()[:60000], 12000.0,
                  float(np.asarray(m[f"X{i:03d}RPM"]).ravel()[0]), "6203", "L4", None, "measured"))
    ftf = {r["record_id"]: float(r["fr_ftf"]) * 60 for r in csv.DictReader(open(ROOT / "results/b7_uored/b7_ftf_records.csv")) if r["fr_ftf"]}
    for r in uored.load():
        x = r.signal.astype(float)
        J.append(("UORED", r.record_id, r.fault_type, x, r.fs_hz, r.rpm, "6203_UORED", "L4", 15000.0, "logged"))
        if r.record_id in ftf:
            J.append(("UORED", r.record_id, r.fault_type, x, r.fs_hz, ftf[r.record_id], "6203_UORED", "L4", 15000.0, "ftf"))
    return J

def pu_job(path):
    r = pu.read_one(Path(path))
    a, b = both(r.signal[:N_SAMPLES].astype(float), r.fs_hz, r.rpm, r.bearing_model, "L3", PU_BAND_HI_HZ)
    return dict(dataset="PU_healthy", arm="measured", record_id=r.record_id, fault_type=r.fault_type, kurtogram=a, iesfo=b)

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(4) as pool:
        rows = pool.map(job, jobs(), chunksize=2)
        rows += pool.map(pu_job, [str(p) for p in pu.files(bearings=["K001", "K002", "K003", "K004", "K005", "K006"])], chunksize=4)
    with io.open(OUT / "c79_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summ = {}
    for ds, arm in sorted({(r["dataset"], r["arm"]) for r in rows}):
        R = [r for r in rows if r["dataset"] == ds and r["arm"] == arm]
        summ[f"{ds}|{arm}"] = {g: {"healthy_FA": [sum(r["fault_type"] == "normal" and r[g] != "normal" for r in R), sum(r["fault_type"] == "normal" for r in R)],
                                   "ball": [sum(r["fault_type"] == "ball" and r[g] == "ball" for r in R), sum(r["fault_type"] == "ball" for r in R)],
                                   "IO_correct": [sum(r["fault_type"] in ("inner_race", "outer_race") and r[g] == r["fault_type"] for r in R),
                                                  sum(r["fault_type"] in ("inner_race", "outer_race") for r in R)],
                                   "wrong_family": sum(r["fault_type"] != "normal" and r[g] not in ("normal", r["fault_type"]) for r in R)}
                               for g in ("kurtogram", "iesfo")}
    (OUT / "c79_summary.json").write_text(json.dumps(summ, indent=2))
    print(json.dumps(summ, indent=1))
