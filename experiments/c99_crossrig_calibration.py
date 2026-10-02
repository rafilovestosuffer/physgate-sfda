"""C99: fix the envelope gate's operating point WITHOUT any target-rig data, then apply it to Paderborn.

Raised in review (Concern 2, both rounds): the gate's operating point z = 10 was pre-registered, but the evidence that
it is safe comes from Paderborn's own healthy recordings -- the target rig, and including bearings that appear in the
transfer targets. Even though z is a threshold on a WITHIN-RECORD robust z-score (no target statistics are pooled into
it), the choice among gate families was informed by target-rig healthy behaviour. That is target-rig supervision.

This script removes the dependency. The identical PCV rule (2 of 3 harmonics, slip window per C75) is swept over z on
healthy recordings from rigs the paper never adapts to -- UORED (20 healthy records, 6203_UORED, geometry verified from
Sehri et al. Table 2, speed measured in-file) and CWRU (healthy baselines, 6205_DE) -- and the operating point is taken
as the smallest z that accepts no healthy calibration record. That z is then applied to Paderborn unchanged.

If the off-rig operating point is at least as strict as the pre-registered z = 10, the gate results do not depend on
target-rig labels. CPU only, ~1 s per record (C19: 20 + 4 records, under a minute). Writes results/c99/.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, prewhiten, ses  # noqa: E402
from harmonic_coords import K_HARM, J_SIDE  # noqa: E402
from kinematics import kinematics, slip_window  # noqa: E402

OUT = ROOT / "results" / "c99"
PCV_H = (1, 2, 3)          # harmonics, as pre-registered (C53)
PCV_FRAC = 2.0 / 3.0       # 2-of-3 multiplicity rule
PU_Z = 10.0                # the pre-registered Paderborn operating point
DF_HZ = 64000.0 / 249_600  # C34: the SES resolution every Paderborn record is analysed at (0.2564 Hz)
BAND_HI_HZ = 15000.0       # C33
Z_GRID = np.arange(2.0, 40.1, 0.5)


def harmonic_max(signal, fs, rpm, bearing_model):
    """max within-record robust z at each of the first three BPFO and BPFI harmonic slip windows.

    The record is truncated to the sample count that reproduces Paderborn's SES resolution (C34, df = 0.2564 Hz) and
    the same 15 kHz band-search cap is applied, so a z on one rig means the same thing as a z on another."""
    k = kinematics(bearing_model)
    f_r = rpm / 60.0
    n = int(round(fs / DF_HZ))
    if len(signal) < n:
        raise ValueError(f"record shorter than {n} samples: cannot match the Paderborn SES resolution")
    y = prewhiten.prewhiten(np.asarray(signal[:n], dtype=np.float64), "none")
    band = band_select.select_band(y, fs, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r,
                                   f_hi=min(BAND_HI_HZ, fs / 2.56))
    f, S = ses.squared_envelope_spectrum(y, fs, band=(band.lo_hz, band.hi_hz))
    z = comb.normalise(f, S)
    out = {}
    for fam in ("BPFO", "BPFI"):
        peaks = []
        for h in PCV_H:
            lo, hi = slip_window(k, fam, harmonic=h)
            m = (f >= lo * f_r) & (f <= hi * f_r)
            peaks.append(float(z[m].max()) if m.any() else 0.0)
        out[fam] = peaks
    return out


def verdict(peaks, z_thr):
    """The pre-registered rule: a family fires iff >= 2 of its 3 harmonics exceed z_thr, and exactly one family wins."""
    score = {fam: sum(p > z_thr for p in ps) / len(PCV_H) for fam, ps in peaks.items()}
    best = max(score.values())
    win = [f for f, v in score.items() if v == best]
    return (win[0] if best >= PCV_FRAC and len(win) == 1 else None)


def calibration_peaks():
    """Healthy recordings from rigs the paper never adapts to."""
    rows = []
    import uored
    for r in uored.load():
        if r.fault_type == "normal":
            rows.append(("UORED", r.record_id, harmonic_max(r.signal, r.fs_hz, r.rpm, r.bearing_model)))
    try:
        import cwru
        for r in cwru.load():
            if r.fault_type == "normal":
                rows.append(("CWRU", r.record_id, harmonic_max(r.signal, r.fs_hz, r.rpm, r.bearing_model)))
    except Exception as exc:
        print(f"CWRU healthy records not loaded ({exc}); calibrating on UORED alone", flush=True)
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cal = calibration_peaks()
    print(f"calibration set: {len(cal)} healthy recordings from {sorted({c[0] for c in cal})}", flush=True)

    fa = [(z, sum(1 for _, _, p in cal if verdict(p, z) is not None)) for z in Z_GRID]
    z_star = next((float(z) for z, n in fa if n == 0), None)
    json.dump({"calibration": [{"rig": r, "record": i, "peaks": p} for r, i, p in cal],
               "false_accept_curve": [[float(z), n] for z, n in fa], "z_star": z_star},
              open(OUT / "c99_calibration.json", "w", encoding="utf-8"), indent=1)

    # Apply the off-rig operating point to Paderborn, using the retained per-record harmonic peaks where available.
    pu = list(csv.DictReader(open(ROOT / "results" / "h7" / "h7_records.csv", encoding="utf-8")))
    have_peaks = "pcv_peak_BPFO_1" in (pu[0] if pu else {})
    L = ["# C99 - operating point fixed off-rig, then applied to Paderborn", "",
         f"Calibration set: {len(cal)} healthy recordings from {', '.join(sorted({c[0] for c in cal}))} "
         "-- rigs that appear nowhere in the adaptation experiments.", "",
         "## False acceptance on the calibration set as the threshold is swept", "",
         "| z | healthy calibration records accepted as faulty |", "|---|---|"]
    L += [f"| {z:.1f} | {n}/{len(cal)} |" for z, n in fa if n or z <= (z_star or 0) + 2]
    L += ["", f"Smallest z with zero false acceptance off-rig: **z* = {z_star}**. "
              f"The pre-registered Paderborn operating point is z = {PU_Z:.0f}.", ""]
    if z_star is not None:
        # a larger z is a stricter threshold (fixed 2026-09-29: the first clause was inverted)
        L.append("The off-rig operating point is "
                 + ("stricter than" if z_star > PU_Z else "no stricter than")
                 + f" the pre-registered one, so a gate calibrated with no target-rig data would "
                 + ("fire at most as often" if z_star >= PU_Z else "fire at least as often")
                 + " as the gate reported in the paper.")
        # Paderborn side of the transfer, read from the envelope-rule operating curve (results/roc/roc_pu.json). The
        # sweep grid has no point at z*, so the nearest grid point at or above it is used and named as such.
        roc = json.load(open(ROOT / "results" / "roc" / "roc_pu.json", encoding="utf-8"))["pcv"]
        at = {int(r["z"]) if float(r["z"]).is_integer() else r["z"]: r for r in roc}
        ref = at[PU_Z] if PU_Z in at else at[int(PU_Z)]
        up = min((r for r in roc if r["z"] >= z_star), key=lambda r: r["z"], default=None)
        if up is not None:
            L += ["", "## Transfer to Paderborn (envelope-rule operating curve, `results/roc/roc_pu.json`)", "",
                  f"The sweep has no point at z* = {z_star}; the nearest point at or above it is z = {up['z']}.", "",
                  "| z | correct fault verdicts | healthy false acceptance |", "|---|---|---|",
                  f"| {ref['z']} (pre-registered) | {ref['correct']}/{ref['n_fault']} | {ref['healthy_FA']}/{ref['n_healthy']} |",
                  f"| {up['z']} (off-rig, nearest sweep point >= z*) | {up['correct']}/{up['n_fault']} | "
                  f"{up['healthy_FA']}/{up['n_healthy']} |", "",
                  f"The off-rig point keeps {100 * up['correct'] / ref['correct']:.0f} % of the pre-registered point's "
                  "correct fault verdicts. Adaptation was not re-run at the off-rig point."]
    if not have_peaks:
        L += ["", "Per-record Paderborn harmonic peaks are not retained in `h7_records.csv` (only the verdict at "
                  "z = 10), so the Paderborn side of the transfer is recomputed by `c99_pu_apply.py` if needed; the "
                  "calibration result above stands on its own."]
    (OUT / "C99_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
