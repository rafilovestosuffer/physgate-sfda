"""Kinematically constrained harmonic-comb scan with a record-specific SURROGATE-ORDER null [C30].

Replaces the family-sum CA-CFAR test after it failed on real CWRU data (results/m4/M4_INVALID.md).

The constraint the old tests lacked
-----------------------------------
A speed-measurement error or cage slip shifts EVERY harmonic of a family by the SAME fraction delta:
    line(h, j) = (h * o_c + j * sb) * f_r * (1 + delta),   h = 1..K,  j = -J..J
Real fault lines therefore move together; stray lines (mains, shaft harmonics, other families) do not.

Statistic, for a fault order o (in shaft orders):
    zmax   = running max of the normalised SES over +/- SMEAR bins        (lines smear under slip)
    C(o)   = max over delta in a FIXED grid of G steps across [-s_max, +s_max] of
             sum_{h,j} min( log(1 + zmax[nearest bin of line(h, j)]), log(1 + Z_CAP) )
The saturation makes C count aligned lines: one strong stray line cannot outscore a family.
Sideband spacing is moved by delta only where slip physically moves it (FTF for the ball), not for the
shaft-rate sidebands of the inner race.
A fixed number of delta steps gives every order the same number of "looks", so scores at different
orders are comparable.

Null, record-specific
---------------------
The same C() is evaluated at N_S deterministic SURROGATE orders spread over [(1-R) o_c, (1+R) o_c], with
every surrogate removed whose harmonics could coincide with ANY deciding family's harmonics
(|h*o' - h'*o_F| <= (s_max + ALIAS_GUARD) * h'*o_F for h, h' <= K). The p-value is
    p_c = (1 + #{surrogates with C >= C(o_c)}) / (1 + N_valid).
The null thereby absorbs that record's own mains lines, shaft-harmonic residue and spectral colour: a
family is significant only if its kinematic comb beats combs placed at arbitrary non-kinematic orders.
Calibrated on null-only simulation before any real-data use (tests/test_comb.py).

Constants fixed a priori from resolution arithmetic, NOT tuned on the records that exposed the defect.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import maximum_filter1d, median_filter

from kinematics import Kinematics, S_MAX_DEFAULT

K_HARM, J_SIDE = 5, 2
G_DELTA = 41            # delta grid steps across [-s_max, +s_max]
SMEAR = 1               # +/- bins (slip smears a line over ~3 bins at df <= 0.33 Hz)
N_SURR = 499            # min attainable p = 0.002
SURR_RANGE = 0.50       # +/- 50 %: smallest range leaving >= 1.05 orders of non-aliasing room for every
                        # family on both verified bearings in L3 AND L4 (at 0.30, L4 BPFO keeps only 0.51)
ALIAS_GUARD = 0.005     # extra exclusion margin (fraction) around aliasing harmonics
FLOOR_BW_HZ = 25.0      # running-median floor bandwidth (robust to lines)
Z_CAP = 20.0            # per-term saturation. Under H0 a 3-bin max exceeds z=20 w.p. ~3*exp(-20) = 6e-9, so any
                        # value above it already means "a line is here". Capping makes the score COUNT aligned
                        # lines instead of letting one strong stray line dominate (failure seen in tests).
M_LINES = 2             # FROZEN multiplicity rule (Randall & Antoni diagnostic practice): a family is admissible
Z_LINE = Z_CAP          # only if >= 2 of its harmonic/sideband positions carry an unmistakable line (z > 20)
                        # at the best delta. A single line is not a fault signature. Known cost, pre-registered:
                        # a fault visible at its fundamental only is missed.
LN2 = np.log(2.0)


@dataclass(frozen=True)
class FamilySpec:
    name: str           # BPFO | BPFI | BPFB
    order: float        # o_c
    J: int              # sideband order used
    sb: float           # sideband spacing in shaft orders
    scale_sb: bool      # does slip/offset delta move the sideband spacing?


def family_specs(k: Kinematics, label_space: str = "L3", J: int = J_SIDE) -> list[FamilySpec]:
    specs = [FamilySpec("BPFO", k.BPFO, 0, 0.0, False),          # stationary outer race: no modulation
             # inner race modulated at f_r: cage slip moves the carrier, NOT the shaft-rate sideband spacing
             FamilySpec("BPFI", k.BPFI, J, 1.0, False)]
    if label_space == "L4":
        # ball carried by the cage: sideband spacing is FTF, which slip DOES move
        specs.append(FamilySpec("BPFB", k.BPFB, J, k.FTF, True))
    return specs


def normalise(f: np.ndarray, S: np.ndarray, bw_hz: float = FLOOR_BW_HZ) -> np.ndarray:
    df = float(f[1] - f[0])
    size = max(3, int(round(bw_hz / df)) | 1)
    floor = median_filter(S, size=size, mode="nearest") / LN2
    return S / np.maximum(floor, np.finfo(float).tiny)


def comb_scores(zmax: np.ndarray, df: float, orders: np.ndarray, spec: FamilySpec, f_r: float,
                K: int = K_HARM, s_max: float = S_MAX_DEFAULT, G: int = G_DELTA) -> tuple[np.ndarray, np.ndarray]:
    """Vectorised C(o) for many orders sharing spec.J and spec.sb. Returns (score, best_delta)."""
    deltas = np.linspace(-s_max, s_max, G)
    hs = np.arange(1, K + 1)
    js = np.arange(-spec.J, spec.J + 1)
    carrier = (hs[None, :, None] * orders[:, None, None] + 0.0 * js[None, None, :]).reshape(len(orders), -1)
    side = np.broadcast_to(js[None, None, :] * spec.sb, (len(orders), K, js.size)).reshape(len(orders), -1)
    scale = 1.0 + deltas[None, :, None]
    pos = (carrier[:, None, :] * scale + side[:, None, :] * (scale if spec.scale_sb else 1.0)) * f_r  # (O, G, L)
    idx = np.rint(pos / df).astype(np.int64)
    valid = (idx > 0) & (idx < zmax.size)
    terms = np.minimum(np.log1p(zmax), np.log1p(Z_CAP))                     # saturating per-term evidence
    vals = np.where(valid, terms[np.clip(idx, 0, zmax.size - 1)], 0.0)
    per_delta = vals.sum(axis=2)                                            # (O, G)
    best = per_delta.argmax(axis=1)
    return per_delta.max(axis=1), deltas[best]


def line_count(zmax: np.ndarray, df: float, order: float, delta: float, spec: FamilySpec, f_r: float,
               K: int = K_HARM) -> int:
    """Number of comb positions carrying an unmistakable line (z > Z_LINE) at a given delta."""
    hs = np.arange(1, K + 1)
    js = np.arange(-spec.J, spec.J + 1)
    scale = 1.0 + delta
    pos = (hs[:, None] * order * scale + js[None, :] * spec.sb * (scale if spec.scale_sb else 1.0)) * f_r
    idx = np.rint(pos.ravel() / df).astype(np.int64)
    idx = idx[(idx > 0) & (idx < zmax.size)]
    return int(np.sum(zmax[idx] > Z_LINE))


def surrogate_orders(spec: FamilySpec, all_specs: list[FamilySpec], K: int = K_HARM,
                     s_max: float = S_MAX_DEFAULT, n: int = N_SURR, rng_range: float = SURR_RANGE,
                     guard: float = ALIAS_GUARD) -> np.ndarray:
    lo, hi = (1 - rng_range) * spec.order, (1 + rng_range) * spec.order
    grid = np.linspace(lo, hi, 50 * n)           # fine grid, then drop aliasing orders
    keep = np.ones(grid.size, dtype=bool)
    tol = s_max + guard
    for F in all_specs:
        for h in range(1, K + 1):
            for h2 in range(1, K + 1):
                target = h2 * F.order
                keep &= np.abs(h * grid - target) > tol * target
    cand = grid[keep]
    if cand.size < n:
        raise ValueError(f"only {cand.size} non-aliasing surrogate orders for {spec.name}; need {n}")
    return cand[np.linspace(0, cand.size - 1, n).round().astype(int)]


def test_families(f: np.ndarray, S: np.ndarray, k: Kinematics, f_r: float, label_space: str = "L3",
                  K: int = K_HARM, J: int = J_SIDE, s_max: float = S_MAX_DEFAULT) -> dict:
    df = float(f[1] - f[0])
    z = normalise(f, S)
    zmax = maximum_filter1d(z, size=2 * SMEAR + 1, mode="nearest")
    specs = family_specs(k, label_space, J)
    out = {}
    for spec in specs:
        sc, dl = comb_scores(zmax, df, np.array([spec.order]), spec, f_r, K, s_max)
        surr = surrogate_orders(spec, specs, K, s_max)
        ss, _ = comb_scores(zmax, df, surr, spec, f_r, K, s_max)
        score = float(sc[0])
        # DETREND. The +/-s_max delta scan covers more distinct bins at higher orders, so surrogate scores drift
        # upward with order (measured Spearman ~ +0.1 under H0), and alias exclusion leaves the surrogate set
        # asymmetric about o_c. Ranking raw scores was anti-conservative for BPFO and conservative for BPFI.
        # Rank residuals from a least-squares linear trend in order instead.
        A = np.vstack([np.ones_like(surr), surr]).T
        coef, *_ = np.linalg.lstsq(A, ss, rcond=None)
        res_s = ss - A @ coef
        res_c = score - (coef[0] + coef[1] * spec.order)
        med = float(np.median(res_s))
        mad = float(np.median(np.abs(res_s - med))) * 1.4826 + 1e-12
        out[spec.name] = {
            "score": score, "best_delta": float(dl[0]),
            "p": float((1 + np.sum(res_s >= res_c)) / (1 + res_s.size)),
            "excess": (res_c - med) / mad,            # robust standardised excess, comparable across families
            "trend_slope": float(coef[1]), "n_surrogates": int(ss.size),
            "n_lines": line_count(zmax, df, spec.order, float(dl[0]), spec, f_r, K),
        }
    return out


def decide(f: np.ndarray, S: np.ndarray, k: Kinematics, f_r: float, alpha: float = 0.05,
           label_space: str = "L3") -> dict:
    """Per-RECORD verdict [C17]. A family is admissible iff (surrogate p <= alpha / n_families, the union bound)
    AND (>= M_LINES aligned unmistakable lines). Physical class = admissible family with the largest
    standardised excess, else 'normal'. The multiplicity rule makes the realised false-acceptance rate
    BOUNDED ABOVE by the surrogate test's, not equal to it: report the realised rate empirically."""
    tests = test_families(f, S, k, f_r, label_space)
    a_fam = alpha / len(tests)
    sig = {n: t for n, t in tests.items() if t["p"] <= a_fam and t["n_lines"] >= M_LINES}
    cls = {"BPFO": "outer_race", "BPFI": "inner_race", "BPFB": "ball"}
    physical = cls[max(sig, key=lambda n: sig[n]["excess"])] if sig else "normal"
    return {"physical_class": physical, "tests": tests, "alpha_per_family": a_fam,
            "min_p": min(t["p"] for t in tests.values())}
