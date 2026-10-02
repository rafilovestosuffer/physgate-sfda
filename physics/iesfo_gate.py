"""Target-informed band selection gate (PROTOCOL C79). Band search is inside the surrogate null.

For each family: over every admissible kurtogram-grid band, compute the C30 detrended robust residual at the kinematic
order AND at every surrogate order; T(o) = max over bands. p = rank of T(o_F) among surrogate T's. C30 itself is untouched.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d

import band_select
import comb
import ses
from harmonic_coords import K_HARM, J_SIDE
from kinematics import Kinematics


def _bands(x, fs, max_fault_hz, f_hi, max_level=6):
    nyq = fs / 2.0
    f_hi = nyq if f_hi is None else min(f_hi, nyq)
    out = []
    for lev in band_select._levels(max_level):
        nb = band_select._n_bands(lev)
        w = nyq / nb
        if w < 2.0 * max_fault_hz:
            continue
        for i in range(nb):
            lo, hi = i * w, (i + 1) * w
            if hi <= f_hi:
                out.append((max(lo, 1.0), hi))
    return out


def decide(x: np.ndarray, fs: float, k: Kinematics, f_r: float, alpha: float = 0.05, label_space: str = "L3",
           f_hi: float | None = None) -> dict:
    specs = comb.family_specs(k, label_space)
    bands = _bands(x, fs, (K_HARM * k.BPFI + J_SIDE) * f_r, f_hi)
    zs = []
    for lo, hi in bands:
        f, S = ses.squared_envelope_spectrum(x, fs, band=(lo, hi))
        zs.append((f, maximum_filter1d(comb.normalise(f, S), size=2 * comb.SMEAR + 1, mode="nearest")))
    tests = {}
    for spec in specs:
        surr = comb.surrogate_orders(spec, specs)
        T_c, T_s, best = -np.inf, np.full(surr.size, -np.inf), None
        for bi, (f, zmax) in enumerate(zs):
            df = float(f[1] - f[0])
            sc, dl = comb.comb_scores(zmax, df, np.array([spec.order]), spec, f_r)
            ss, _ = comb.comb_scores(zmax, df, surr, spec, f_r)
            A = np.vstack([np.ones_like(surr), surr]).T
            coef, *_ = np.linalg.lstsq(A, ss, rcond=None)
            res_s = ss - A @ coef
            med = float(np.median(res_s))
            mad = float(np.median(np.abs(res_s - med))) * 1.4826 + 1e-12
            r_c = (float(sc[0]) - (coef[0] + coef[1] * spec.order) - med) / mad
            r_s = (res_s - med) / mad
            T_s = np.maximum(T_s, r_s)
            if r_c > T_c:
                T_c, best = r_c, (bi, float(dl[0]))
        f, zmax = zs[best[0]]
        tests[spec.name] = {"T": T_c, "p": float((1 + np.sum(T_s >= T_c)) / (1 + T_s.size)),
                            "band": bands[best[0]], "best_delta": best[1],
                            "n_lines": comb.line_count(zmax, float(f[1] - f[0]), spec.order, best[1], spec, f_r)}
    a_fam = alpha / len(tests)
    adm = {n: t for n, t in tests.items() if t["p"] <= a_fam and t["n_lines"] >= comb.M_LINES}
    cls = {"BPFO": "outer_race", "BPFI": "inner_race", "BPFB": "ball"}
    return {"physical_class": cls[max(adm, key=lambda n: adm[n]["T"])] if adm else "normal", "tests": tests,
            "n_bands": len(bands)}
