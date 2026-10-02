"""H7 (PROTOCOL C53) -- frequency-position rules vs the kinematic comb gate on Paderborn.

(i)  comb gate: reused from results/h6_c35 (cepstrum arm). Not re-run.
(ii) PCV-style rule  : PCTL Alg. 1 reimplemented on the MEASURED SES (none arm).
(iii) EAGLE-style rule: Bio-SFDA sec. 4.2 reimplemented on the raw-signal STFT (no envelope, no DRS).
All constants are fixed in C53. These are OUR reimplementations and are labelled as such everywhere.
"""
from __future__ import annotations

import csv
import io
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.signal import stft

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, prewhiten, pu, ses  # noqa: E402,E401
from h6_prewhitening import N_SAMPLES, UNREADABLE, PU_BAND_HI_HZ, SINGLE_FAULT, wilson  # noqa: E402
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics, slip_window  # noqa: E402

OUT = ROOT / "results" / "h7"
PCV_Z, PCV_FRAC, PCV_H = 10.0, 2.0 / 3.0, (1, 2, 3)
EAGLE_SEG_S, EAGLE_Z, EAGLE_NEIGH_HZ, EAGLE_WINS, EAGLE_EMAX_HZ = 1.0, 2.0, 25.0, 5.0, 15000.0
FAMS = {"BPFO": "outer_race", "BPFI": "inner_race"}


def process(path: str) -> dict:
    r = pu.read_one(Path(path))
    k = kinematics(r.bearing_model)
    f_r = r.rpm / 60.0
    x = r.signal[:N_SAMPLES].astype(np.float64)
    row = {"record_id": r.record_id, "bearing_id": r.bearing_id, "geometry": r.bearing_model,
           "fault_type": r.fault_type, "condition": r.condition}

    # ---- (ii) PCV-style: measured SES, identical band selection to H6 'none' arm
    y = prewhiten.prewhiten(x, "none")
    band = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r,
                                   f_hi=PU_BAND_HI_HZ)
    f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(band.lo_hz, band.hi_hz))
    z = comb.normalise(f, S)
    scores = {}
    for fam in FAMS:
        present = 0
        for h in PCV_H:
            lo, hi = slip_window(k, fam, harmonic=h)
            m = (f >= lo * f_r) & (f <= hi * f_r)
            present += int(m.any() and z[m].max() > PCV_Z)
        scores[fam] = present / len(PCV_H)
        row[f"pcv_S_{fam}"] = scores[fam]
    best = max(scores.values())
    winners = [fam for fam, v in scores.items() if v == best]
    row["pcv_class"] = FAMS[winners[0]] if best >= PCV_FRAC and len(winners) == 1 else "normal"

    # ---- (iii) EAGLE-style raw features (z-scoring across the population happens in main)
    nper = int(EAGLE_SEG_S * r.fs_hz)
    fs_, _, Z = stft(x, fs=r.fs_hz, window="hann", nperseg=nper, noverlap=nper // 2)
    mag = np.abs(Z).mean(axis=1)
    total = float(np.sum(mag[fs_ <= EAGLE_EMAX_HZ] ** 2))
    for fam in ("BPFO", "BPFI", "BSF"):
        lo, hi = slip_window(k, fam, harmonic=1)
        roi = (fs_ >= lo * f_r) & (fs_ <= hi * f_r)
        if not roi.any():                                   # ROI narrower than 1 Hz: nearest bin
            roi = np.abs(fs_ - getattr(k, fam) * f_r) == np.abs(fs_ - getattr(k, fam) * f_r).min()
        c = getattr(k, fam) * f_r
        neigh = (np.abs(fs_ - c) <= EAGLE_NEIGH_HZ) & ~roi
        row[f"eagle_snr_{fam}"] = float(mag[roi].max() / max(np.median(mag[neigh]), 1e-30))
        row[f"eagle_E_{fam}"] = float(np.sum(mag[roi] ** 2) / max(total, 1e-30))
    return row


def robust_z(v: np.ndarray) -> np.ndarray:
    med = np.median(v)
    mad = 1.4826 * np.median(np.abs(v - med))
    return np.clip((v - med) / max(mad, 1e-30), -EAGLE_WINS, EAGLE_WINS)


def precision_block(R, key):
    n = len(R)
    prev = sum(x["fault_type"] == "outer_race" for x in R) / n
    said = [x for x in R if x[key] == "outer_race"]
    tp = sum(x["fault_type"] == "outer_race" for x in said)
    p, lo, hi = wilson(tp, len(said))
    at_chance = True if not said else bool(lo <= prev <= hi)
    material = bool(said) and (p - prev >= 0.15 and lo > prev)
    H = [x for x in R if x["fault_type"] == "normal"]
    fa = sum(x[key] != "normal" for x in H)
    conf = {t: {q: sum(1 for x in R if x["fault_type"] == t and x[key] == q) for q in ("normal", "inner_race", "outer_race")}
            for t in ("normal", "inner_race", "outer_race")}
    return {"n": n, "outer_prevalence": prev, "says_outer": len(said), "outer_precision": p,
            "outer_precision_ci95": [lo, hi], "at_chance": at_chance, "materially_above": material,
            "healthy_false_acceptance": {"n": len(H), "false": fa, "ci95": list(wilson(fa, len(H)))},
            "confusion_true_to_rule": conf}


def main() -> int:
    comb_csv = ROOT / "results" / "h6_c35" / "h6_records.csv"
    if not comb_csv.exists():
        raise SystemExit("REFUSED: C53 reuses the H6 C35 cepstrum arm; run it first")
    comb_cls = {x["record_id"]: x["physical_class"] for x in csv.DictReader(io.open(comb_csv, encoding="utf-8"))
                if x["arm"] == "cepstrum"}
    files = [str(p) for p in pu.files(bearings=SINGLE_FAULT) if p.stem not in UNREADABLE]
    assert len(files) == 2319, len(files)
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    rows = []
    with Pool(4) as pool:
        for i, rr in enumerate(pool.imap_unordered(process, files, chunksize=4), 1):
            rows.append(rr)
            if i % 200 == 0:
                print(f"{i}/{len(files)} {time.time() - t0:.0f}s", flush=True)
    rows.sort(key=lambda x: x["record_id"])
    for fam in ("BPFO", "BPFI", "BSF"):
        zs = robust_z(np.array([x[f"eagle_snr_{fam}"] for x in rows]))
        ze = robust_z(np.array([x[f"eagle_E_{fam}"] for x in rows]))
        for x, a, b in zip(rows, zs, ze):
            x[f"eagle_zsnr_{fam}"], x[f"eagle_zE_{fam}"] = float(a), float(b)
            x[f"eagle_bit_{fam}"] = int(a > EAGLE_Z or b > EAGLE_Z)
    for x in rows:
        act = [fam for fam in FAMS if x[f"eagle_bit_{fam}"]]
        x["eagle_class"] = FAMS[max(act, key=lambda fam: x[f"eagle_zsnr_{fam}"])] if act else "normal"
        x["comb_class"] = comb_cls[x["record_id"]]
    with io.open(OUT / "h7_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    res = {}
    for key in ("comb_class", "pcv_class", "eagle_class"):
        res[key] = {"all": precision_block(rows, key)}
        for g in sorted({x["geometry"] for x in rows}):
            res[key][g] = precision_block([x for x in rows if x["geometry"] == g], key)
    supported = (res["pcv_class"]["all"]["at_chance"] and res["eagle_class"]["all"]["at_chance"]
                 and res["comb_class"]["all"]["materially_above"])
    summary = {"decision_rule": "PROTOCOL C53", "H7_supported": bool(supported), "results": res,
               "seconds": round(time.time() - t0)}
    (OUT / "h7_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({k: {kk: {m: v[kk][m] for m in ("outer_precision", "outer_precision_ci95", "says_outer", "at_chance", "materially_above")} for kk in v} for k, v in res.items()}, indent=1))
    print("H7_supported", supported)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
