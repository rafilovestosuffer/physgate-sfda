"""Second-generation comb gate (PROTOCOL C72). C30 (`comb.py`) stays frozen; this module only wraps it.

(a) shaft-alias guard: at the family's best delta, among positions carrying an unmistakable line (z > Z_LINE),
    if >= ALIAS_FRAC of them lie within ALIAS_BINS native bins of an integer multiple of f_r -> inadmissible.
(b) arbitration by aligned-line fraction n_lines / n_positions, ties broken by robust excess.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import maximum_filter1d

import comb
from kinematics import Kinematics

ALIAS_FRAC = 0.5
ALIAS_BINS = 1.5


def _line_positions(spec, delta, f_r, K=comb.K_HARM):
    hs = np.arange(1, K + 1)[:, None]
    js = np.arange(-spec.J, spec.J + 1)[None, :]
    scale = 1.0 + delta
    return ((hs * spec.order) * scale + js * spec.sb * (scale if spec.scale_sb else 1.0)).ravel() * f_r


def decide(f: np.ndarray, S: np.ndarray, k: Kinematics, f_r: float, alpha: float = 0.05,
           label_space: str = "L3") -> dict:
    tests = comb.test_families(f, S, k, f_r, label_space)
    df = float(f[1] - f[0])
    zmax = maximum_filter1d(comb.normalise(f, S), size=2 * comb.SMEAR + 1, mode="nearest")
    specs = {s.name: s for s in comb.family_specs(k, label_space)}
    a_fam = alpha / len(tests)
    info = {}
    for name, t in tests.items():
        pos = _line_positions(specs[name], t["best_delta"], f_r)
        idx = np.rint(pos / df).astype(int)
        ok = (idx > 0) & (idx < zmax.size)
        lit = pos[ok][zmax[idx[ok]] > comb.Z_LINE]
        if lit.size:
            dist_bins = np.abs(lit - np.rint(lit / f_r) * f_r) / df
            aliased = float(np.mean(dist_bins <= ALIAS_BINS))
        else:
            aliased = 0.0
        info[name] = {"n_positions": int(pos.size), "line_fraction": t["n_lines"] / pos.size,
                      "shaft_aliased_fraction": aliased}
    adm = {n: t for n, t in tests.items()
           if t["p"] <= a_fam and t["n_lines"] >= comb.M_LINES and info[n]["shaft_aliased_fraction"] < ALIAS_FRAC}
    cls = {"BPFO": "outer_race", "BPFI": "inner_race", "BPFB": "ball"}
    physical = (cls[max(adm, key=lambda n: (info[n]["line_fraction"], adm[n]["excess"]))] if adm else "normal")
    return {"physical_class": physical, "tests": tests, "v2": info, "alpha_per_family": a_fam}
