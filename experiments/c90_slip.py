"""C90: empirical slip distribution from fault lines with measured shaft speed (pre-registered in PROTOCOL C90).

Per record: cepstrum pre-whitening -> band selection -> SES (as comb_v2_eval.verdicts). Family = true fault type.
  outer: k*BPFO0*(1-s)*f_r      inner: k*(BPFI0 + s*BPFO0)*f_r      k = 1..3,  s in [-1 %, +6 %] step 0.01 %
Location on an 8x zero-padded SES; validity (>= 2 of 3 positions with z > Z_LINE) on the native SES.
Arms: unmasked, shaft-masked (z within 1.5 native bins of an integer multiple of f_r set to 0). UORED excluded (no
independent speed). Writes results/c90/.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import scipy.io as sio
from scipy.stats import binomtest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, cwru, prewhiten, pu, ses  # noqa: E402,E401
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402
from h6_prewhitening import N_SAMPLES, UNREADABLE, PU_BAND_HI_HZ  # noqa: E402

OUT = ROOT / "results" / "c90"
S_GRID = np.round(np.arange(-0.01, 0.06 + 1e-9, 0.0001), 6)
KS = (1, 2, 3)
PAD = 8
MASK_BINS = 1.5
T_A = 3.0
PU_FAULT = ["KA01", "KA03", "KA05", "KA06", "KA07", "KA08", "KA09", "KI01", "KI03", "KI05", "KI07", "KI08",
            "KA04", "KA15", "KA16", "KA22", "KA30", "KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]


def s_star(k) -> float:
    return (k.BPFO - math.floor(k.BPFO)) / k.BPFO


def positions(fault: str, k, f_r: float) -> np.ndarray:
    """(len(S_GRID), 3) line frequencies in Hz under the C75 slip model."""
    hs = np.asarray(KS, float)[None, :]
    if fault == "outer_race":
        return hs * (k.BPFO * (1.0 - S_GRID))[:, None] * f_r
    return hs * (k.BPFI + S_GRID * k.BPFO)[:, None] * f_r


def estimate(x: np.ndarray, fs: float, rpm: float, bearing: str, fault: str, f_hi=None) -> dict:
    k = kinematics(bearing)
    f_r = rpm / 60.0
    y = prewhiten.prewhiten(x, "cepstrum")
    kw = {"f_hi": f_hi} if f_hi else {}
    b = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r, **kw)
    yb = ses.bandpass(y, fs, b.lo_hz, b.hi_hz)
    e = ses.squared_envelope(yb)
    n = e.size
    P = positions(fault, k, f_r)
    f_lim = P.max() + 4 * comb.FLOOR_BW_HZ          # crop before normalising (speed); floor window stays inside the crop
    f_nat = np.fft.rfftfreq(n, 1.0 / fs)
    m_n = f_nat <= f_lim
    f_nat = f_nat[m_n]
    z_nat = comb.normalise(f_nat, (np.abs(np.fft.rfft(e)) ** 2 / n)[m_n])
    df = f_nat[1]
    f_pad = np.fft.rfftfreq(PAD * n, 1.0 / fs)
    m_p = f_pad <= f_lim
    f_pad = f_pad[m_p]
    z_pad = comb.normalise(f_pad, (np.abs(np.fft.rfft(e, PAD * n)) ** 2 / n)[m_p])
    dfp = f_pad[1]
    out = {"f_r": f_r, "df": df, "s_star": s_star(k), "tol": 1.0 / (T_A * k.BPFO * f_r)}
    for arm in ("unmasked", "masked"):
        zp = z_pad.copy()
        if arm == "masked":
            dist = np.abs(f_pad - np.rint(f_pad / f_r) * f_r) / df
            zp[(dist <= MASK_BINS) & (f_pad > 0.5 * f_r)] = 0.0
        # score: max padded z within +/- 1 native bin of each position
        half = PAD
        idx = np.rint(P / dfp).astype(int)
        from scipy.ndimage import maximum_filter1d
        zmax = maximum_filter1d(zp, size=2 * half + 1, mode="nearest")
        ok = idx < zmax.size
        vals = np.where(ok, zmax[np.clip(idx, 0, zmax.size - 1)], 0.0)
        score = np.minimum(vals, comb.Z_CAP).sum(1)
        # smoke-test bug fix (before the full run): capped scores plateau and argmax took the lowest s; tie-break on uncapped z
        j = int(np.lexsort((-vals.sum(1), -score))[0])
        s_hat = float(S_GRID[j])
        # validity on the native SES at s_hat (same arm mask applied at native resolution)
        zn = z_nat.copy()
        if arm == "masked":
            distn = np.abs(f_nat - np.rint(f_nat / f_r) * f_r) / df
            zn[(distn <= MASK_BINS) & (f_nat > 0.5 * f_r)] = 0.0
        zn_max = maximum_filter1d(zn, size=3, mode="nearest")
        ni = np.rint(P[j] / df).astype(int)
        lit = int(sum(zn_max[i] > comb.Z_LINE for i in ni if i < zn_max.size))
        out[arm] = {"s_hat": s_hat, "lit": lit, "valid": lit >= 2, "score": float(score[j]),
                    "in_lock": abs(s_hat - out["s_star"]) <= out["tol"], "at_grid_edge": j in (0, S_GRID.size - 1)}
    return out


def pu_job(path):
    r = pu.read_one(Path(path))
    e = estimate(r.signal[:N_SAMPLES].astype(np.float64), r.fs_hz, r.rpm, r.bearing_model, r.fault_type, PU_BAND_HI_HZ)
    return {"dataset": "PU", "record_id": r.record_id, "bearing_id": r.bearing_id, "geometry": r.bearing_model,
            "fault_type": r.fault_type, "condition": r.condition, "damage": r.meta.get("damage_origin"),
            "rpm": r.rpm, "rpm_std": r.meta.get("rpm_std"), **flat(e)}


def flat(e):
    row = {k: e[k] for k in ("f_r", "df", "s_star", "tol")}
    for arm in ("unmasked", "masked"):
        for k, v in e[arm].items():
            row[f"{arm}_{k}"] = v
    return row


def cwru_rows():
    rows = []
    for r in cwru.load("DE"):
        if r.fs_hz != 12000.0 or r.fault_type not in ("outer_race", "inner_race"):
            continue
        e = estimate(r.signal.astype(np.float64), r.fs_hz, r.rpm, "6205", r.fault_type)
        rows.append({"dataset": "CWRU_DE", "record_id": r.record_id, "bearing_id": r.bearing_id, "geometry": "6205",
                     "fault_type": r.fault_type, "condition": r.condition, "damage": "seeded", "rpm": r.rpm, "rpm_std": None, **flat(e)})
    from c78_fe_de_control import FE  # noqa: E402  (FE fault table, engineering.case.edu)
    for i, (ft, bid) in sorted(FE.items()):
        if ft not in ("outer_race", "inner_race"):
            continue
        m = sio.loadmat(ROOT / "data" / "cwru_fe" / f"{i}.mat")
        x = np.asarray(m[f"X{i:03d}_FE_time"], float).ravel()
        rpm = float(np.asarray(m[f"X{i:03d}RPM"]).ravel()[0])
        e = estimate(x, 12000.0, rpm, "6203", ft)
        rows.append({"dataset": "CWRU_FE", "record_id": str(i), "bearing_id": bid, "geometry": "6203", "fault_type": ft,
                     "condition": "", "damage": "seeded", "rpm": rpm, "rpm_std": None, **flat(e)})
    return rows


def summarise(rows):
    S = {}
    groups = defaultdict(list)
    for r in rows:
        groups[(r["dataset"], r["geometry"], r["fault_type"])].append(r)
        groups[(r["dataset"], r["geometry"], "all")].append(r)
    for (ds, g, ft), R in sorted(groups.items()):
        blk = {"n_records": len(R), "s_star": R[0]["s_star"]}
        for arm in ("unmasked", "masked"):
            V = [r for r in R if r[f"{arm}_valid"]]
            s = np.array([r[f"{arm}_s_hat"] for r in V])
            lock = [r for r in V if r[f"{arm}_in_lock"]]
            bear_all = {r["bearing_id"] for r in V}
            bear_lock = {r["bearing_id"] for r in lock}
            blk[arm] = {"valid": len(V), "valid_frac": len(V) / len(R),
                        "slip_pct_quantiles_5_25_50_75_95": (np.percentile(100 * s, [5, 25, 50, 75, 95]).round(3).tolist() if len(s) else None),
                        "in_lock_records": len(lock), "in_lock_frac_of_valid": (len(lock) / len(V) if V else None),
                        "in_lock_ci95": (list(binomtest(len(lock), len(V)).proportion_ci(0.95)) if V else None),
                        "bearings_with_any_in_lock": f"{len(bear_lock)}/{len(bear_all)}",
                        "at_grid_edge": sum(r[f"{arm}_at_grid_edge"] for r in V)}
        S[f"{ds}|{g}|{ft}"] = blk
    return S


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = cwru_rows()
    files = [str(p) for p in pu.files(bearings=PU_FAULT) if p.stem not in UNREADABLE]
    with Pool(4) as pool:
        rows += pool.map(pu_job, files, chunksize=4)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with io.open(OUT / "c90_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)
    S = summarise(rows)
    (OUT / "c90_summary.json").write_text(json.dumps(S, indent=2), encoding="utf-8")
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
