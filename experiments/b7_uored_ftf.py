"""C74 third speed arm: gate UORED files whose cage comb qualifies, at f_r = f_FTF / 0.3812. C30 and comb_v2."""
import csv, io, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import comb, comb_v2, prewhiten, ses, uored, band_select
from kinematics import kinematics
from harmonic_coords import K_HARM, J_SIDE
OUT = ROOT / "results" / "b7_uored"
k = kinematics("6203_UORED")

def ftf_speed(z, df):
    grid = np.arange(10.6, 12.2, 0.005)
    def sc(g): return sum(np.log1p(min(20.0, z[int(round(h*g/df))-1:int(round(h*g/df))+2].max())) for h in range(1, 5))
    g = grid[int(np.argmax([sc(v) for v in grid]))]
    n = sum(z[int(round(h*g/df))-1:int(round(h*g/df))+2].max() > 20 for h in range(1, 5))
    return (g / k.FTF if n >= 3 else None), g, n

rows = []
for r in uored.load():
    x = r.signal.astype(np.float64); y = prewhiten.prewhiten(x, "cepstrum")
    f0, S0 = ses.squared_envelope_spectrum(y, r.fs_hz, band=(500.0, 15000.0))
    fr, g, n = ftf_speed(comb.normalise(f0, S0), f0[1] - f0[0])
    row = {"record_id": r.record_id, "fault_type": r.fault_type, "bearing_id": r.bearing_id, "ftf_hz": round(g, 3), "ftf_lines": n,
           "fr_ftf": None if fr is None else round(fr, 3), "fr_logged": round(r.rpm / 60, 3)}
    if fr is not None:
        b = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * fr, f_hi=15000.0)
        f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(b.lo_hz, b.hi_hz))
        row["c30"] = comb.decide(f, S, k, fr, 0.05, "L4")["physical_class"]
        row["v2"] = comb_v2.decide(f, S, k, fr, 0.05, "L4")["physical_class"]
    rows.append(row)
keys = sorted({kk for r in rows for kk in r})
with io.open(OUT / "b7_ftf_records.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
q = [r for r in rows if r["fr_ftf"] is not None]
for r in q:
    print(r["record_id"], r["fault_type"], r["fr_ftf"], "c30:", r["c30"], "v2:", r["v2"])
