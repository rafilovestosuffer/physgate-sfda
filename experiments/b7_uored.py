"""B7-UORED (descriptive) and H8 (decision), PROTOCOL C55 with the C68 speed amendment.

Full 10 s records, 6203_UORED kinematics, kurtogram band <= 15 kHz (max_level 6), SES, frozen comb gate, L4, alpha 0.05.
Arms: prewhiten {none, cepstrum} x speed {spectral_1x (primary), logged (secondary)}.
"""
from __future__ import annotations

import csv
import io
import json
import math
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep")]
import band_select, comb, prewhiten, ses, uored  # noqa: E402,E401
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics  # noqa: E402

ALPHA, BAND_HI = 0.05, 15000.0
OUT = ROOT / "results" / "b7_uored"


def wilson(k, n, z=1.96):
    if n == 0:
        return [float("nan")] * 3
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [p, c - h, c + h]


def spectral_rpm(x: np.ndarray, fs: float) -> float:
    """C68: 1x line of the raw amplitude spectrum within 28.5-31.0 Hz, parabolic refinement."""
    x = x.astype(np.float64) - x.mean()
    X = np.abs(np.fft.rfft(x * np.hanning(x.size)))
    f = np.fft.rfftfreq(x.size, 1 / fs)
    idx = np.nonzero((f >= 28.5) & (f <= 31.0))[0]
    i = idx[np.argmax(X[idx])]
    a, b, c = np.log(X[i - 1] + 1e-30), np.log(X[i] + 1e-30), np.log(X[i + 1] + 1e-30)
    off = 0.5 * (a - c) / (a - 2 * b + c) if (a - 2 * b + c) != 0 else 0.0
    return 60.0 * (f[i] + off * (f[1] - f[0]))


def process(rec_id: str) -> list[dict]:
    r = {x.record_id: x for x in uored.load()}[rec_id]
    k = kinematics(r.bearing_model)
    x = r.signal.astype(np.float64)
    speeds = {"spectral_1x": spectral_rpm(x, r.fs_hz), "logged": r.rpm}
    rows = []
    for arm in ("none", "cepstrum"):
        y = prewhiten.prewhiten(x, arm)
        for src, rpm in speeds.items():
            f_r = rpm / 60.0
            b = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r, f_hi=BAND_HI)
            f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(b.lo_hz, b.hi_hz))
            v = comb.decide(f, S, k, f_r, ALPHA, "L4")
            rows.append({"record_id": r.record_id, "bearing_id": r.bearing_id, "fault_type": r.fault_type,
                         "health_state": r.meta["health_state"], "manufacturer": r.meta["manufacturer"],
                         "load_N": r.meta["load_N"], "arm": arm, "speed_source": src, "rpm": round(rpm, 2),
                         "rpm_logged": r.rpm, "rpm_spectral": round(speeds["spectral_1x"], 2),
                         "band_lo_hz": round(b.lo_hz, 1), "band_hi_hz": round(b.hi_hz, 1),
                         "physical_class": v["physical_class"],
                         **{f"lines_{fam}": v["tests"][fam]["n_lines"] for fam in ("BPFO", "BPFI", "BPFB")},
                         **{f"p_{fam}": v["tests"][fam]["p"] for fam in ("BPFO", "BPFI", "BPFB")}})
    return rows


def summarise(R):
    out = {}
    classes = ("normal", "inner_race", "outer_race", "ball")
    conf = {t: dict(Counter(x["physical_class"] for x in R if x["fault_type"] == t)) for t in classes + ("cage",)}
    for c in ("outer_race", "inner_race", "ball"):
        said = [x for x in R if x["physical_class"] == c]
        tp = sum(x["fault_type"] == c for x in said)
        truth = [x for x in R if x["fault_type"] == c]
        out[c] = {"says": len(said), "precision_wilson": wilson(tp, len(said)), "recall": tp / len(truth),
                  "recall_by_state": {s: sum(x["physical_class"] == c for x in truth if x["health_state"] == s) / 5
                                      for s in ("developing", "faulty")}}
    H = [x for x in R if x["fault_type"] == "normal"]
    fa = sum(x["physical_class"] != "normal" for x in H)
    out["healthy_false_acceptance"] = {"n": len(H), "false": fa, "wilson": wilson(fa, len(H))}
    out["inner_to_outer"] = conf["inner_race"].get("outer_race", 0)
    out["outer_to_inner"] = conf["outer_race"].get("inner_race", 0)
    cage = [x for x in R if x["fault_type"] == "cage"]
    oib = [x for x in R if x["fault_type"] in ("inner_race", "outer_race", "ball")]
    rc = sum(x["physical_class"] == "normal" for x in cage)
    rf = sum(x["physical_class"] == "normal" for x in oib)
    p = fisher_exact([[rc, len(cage) - rc], [rf, len(oib) - rf]], alternative="greater")[1]
    out["H8"] = {"R_c": rc / len(cage), "R_f": rf / len(oib), "fisher_one_sided_p": p,
                 "supported": bool(rc / len(cage) - rf / len(oib) >= 0.15 and p < 0.05)}
    out["confusion_true_to_gate"] = conf
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sorted(r.record_id for r in uored.load())      # also builds the npz cache in this process
    with Pool(4) as pool:
        rows = [x for rr in pool.map(process, ids) for x in rr]
    with io.open(OUT / "b7_records.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    summary = {"rule": "PROTOCOL C55 + C68", "arms": {}}
    for arm in ("none", "cepstrum"):
        for src in ("spectral_1x", "logged"):
            summary["arms"][f"{arm}|{src}"] = summarise([x for x in rows if x["arm"] == arm and x["speed_source"] == src])
    summary["H8_supported_primary"] = summary["arms"]["cepstrum|spectral_1x"]["H8"]["supported"]
    (OUT / "b7_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    for k, v in summary["arms"].items():
        print(k, {c: (v[c]["says"], [round(z, 3) for z in v[c]["precision_wilson"]], round(v[c]["recall"], 2)) for c in ("outer_race", "inner_race", "ball")},
              "FA", v["healthy_false_acceptance"]["false"], "I->O", v["inner_to_outer"], "H8", v["H8"])
    print("H8_supported_primary", summary["H8_supported_primary"])


if __name__ == "__main__":
    main()
