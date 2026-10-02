"""C36 (audit item "C33"): calibrate the FROZEN comb gate (C30) on null-only synthetic records with
discrete/random separation IN THE LOOP, over the pre-registered grid.

Grid: arm {none, cepstrum} x background {white, AR(2)} x alpha {0.10, 0.05, 0.01}
      x bearing {6205, 6203_PU_2905, 6203_PU_2855}. No fault, no line, no real data.
Reported: per-family surrogate p-value realised rate P(p <= alpha) and the GATE's realised
false-acceptance rate (physical_class != normal), each with a Monte-Carlo SE.
Pass rule, fixed before running: gate FAR <= alpha + 2 SE in every cell (the gate may be conservative;
it must not be anti-conservative). Written to results/calibration/null_drs_<date>.json.
"""
from __future__ import annotations

import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics")]
import comb, comb_v2, prewhiten, ses  # noqa: E402,E401
import os
GATE = comb_v2 if os.environ.get("GATE") == "v2" else comb
from kinematics import kinematics  # noqa: E402

FS, T = 12000.0, 3.0
N = int(FS * T)
BAND = (2000.0, 4000.0)
F_R = {"6205": 1772 / 60.0, "6203_PU_2905": 25.0, "6203_PU_2855": 25.0}
TRIALS = 300
ALPHAS = (0.10, 0.05, 0.01)


def one(args):
    bearing, arm, colored, seed = args
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(N)
    if colored:
        x = lfilter([1.0], [1.0, -0.7, 0.25], x)
    y = prewhiten.prewhiten(x, arm)
    f, S = ses.squared_envelope_spectrum(y, FS, band=BAND)
    k = kinematics(bearing)
    t = comb.test_families(f, S, k, F_R[bearing], "L3")
    ps = [t["BPFO"]["p"], t["BPFI"]["p"]]
    gate = {a: GATE.decide(f, S, k, F_R[bearing], alpha=a, label_space="L3")["physical_class"] != "normal"
            for a in ALPHAS}
    return bearing, arm, colored, ps, gate


def main():
    jobs = [(b, arm, col, 50_000 + i) for b in F_R for arm in (("cepstrum",) if os.environ.get("GATE") == "v2" else ("none", "cepstrum")) for col in (False, True)
            for i in range(TRIALS)]
    t0 = time.time()
    with Pool(4) as pool:
        res = pool.map(one, jobs, chunksize=8)
    cells = {}
    for b, arm, col, ps, gate in res:
        c = cells.setdefault((b, arm, "AR2" if col else "white"), {"p": [], "g": {a: 0 for a in ALPHAS}, "n": 0})
        c["p"] += ps
        c["n"] += 1
        for a in ALPHAS:
            c["g"][a] += gate[a]
    out, ok = [], True
    for (b, arm, bg), c in cells.items():
        p = np.asarray(c["p"])
        row = {"bearing": b, "arm": arm, "background": bg, "trials": c["n"]}
        for a in ALPHAS:
            far = c["g"][a] / c["n"]
            se = (a * (1 - a) / c["n"]) ** 0.5
            passed = far <= a + 2 * se
            ok &= passed
            row[f"a{a}"] = {"p_rate": round(float((p <= a).mean()), 4), "gate_far": round(far, 4),
                            "se": round(se, 4), "pass": bool(passed)}
        out.append(row)
        print(row, flush=True)
    dst = ROOT / "results" / "calibration" / f"null_drs{'_v2' if os.environ.get('GATE') == 'v2' else ''}_{time.strftime('%Y-%m-%d')}.json"
    dst.write_text(json.dumps({"rule": "gate FAR <= alpha + 2SE in every cell", "all_pass": bool(ok),
                               "seconds": round(time.time() - t0), "cells": out}, indent=2))
    print("ALL_PASS", ok, "->", dst)


if __name__ == "__main__":
    main()
