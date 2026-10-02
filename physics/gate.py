"""Physics admissibility gate: a family-sum cyclostationarity test with an exact Gamma null.

Granularity is PER RECORD [C17]; verdicts are inherited by every child window of that record.

PRIMARY test [C24] -- cell-averaging CFAR, exact under an ESTIMATED noise floor:
    S_c   = native bins inside the union over k=1..K of slip_window(k * f_c)  [snap-to-native, C12]
    R_c   = reference bins within REF_HZ of any test bin, excluding test bins and +/- GUARD_HZ
    stat  = mean(SES[S_c]) / mean(SES[R_c])
    H0    : stat ~ F(2*N_c, 2*M_c)      (ratio of two independent scaled chi2 sums)
Gamma(N_c,1) is exact only when sigma2 is KNOWN. With sigma2 estimated from the same record the
Gamma threshold is anti-conservative (measured: 0.074 realised at nominal 0.05, ~4 SE high).
The F threshold absorbs the estimator's variance and is calibrated (0.049-0.055 at nominal 0.05).
REF_HZ and GUARD_HZ were fixed from null-only Monte-Carlo simulation, never from fault data [C23].

Interpolation is NOT used here. Interpolating correlates adjacent bins and rescales variance, which
destroys both the Exp(1) marginal and the independence the sum relies on. The representation tensor
may interpolate (no null is claimed for it); the gate may not.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import median_filter
from scipy.stats import gamma as gamma_dist

from scipy.stats import f as f_dist

LN2 = np.log(2.0)
REF_HZ = 25.0     # pre-registered from null-only simulation [C23]
GUARD_HZ = 2.0    # pre-registered from null-only simulation [C23]


def noise_floor(S: np.ndarray, f: np.ndarray, bw_hz: float = 50.0) -> np.ndarray:
    """Frequency-dependent scale sigma2(b) for NON-WHITE noise (Borghesani et al. 2013).

    Estimated by a running MEDIAN over a local bandwidth, divided by ln2. For an exponential
    variable median = mean * ln2, so median/ln2 is a consistent estimator of the mean that is
    robust to the very peaks we are trying to detect -- a running mean would let a strong fault
    line inflate its own noise floor and hide itself.
    """
    if S.size < 3:
        return np.full_like(S, S.mean() if S.size else 1.0)
    df = float(f[1] - f[0])
    size = max(3, int(round(bw_hz / df)) | 1)   # odd window
    med = median_filter(S, size=size, mode="nearest")
    return np.maximum(med / LN2, np.finfo(float).tiny)


def family_bins(f: np.ndarray, windows_hz: list[tuple[float, float]]) -> np.ndarray:
    """Indices of native bins falling inside any harmonic's slip window. Snap-to-native [C12]."""
    idx: list[int] = []
    for lo, hi in windows_hz:
        sel = np.nonzero((f >= lo) & (f <= hi))[0]
        idx.extend(sel.tolist())
    return np.unique(np.asarray(idx, dtype=int))


def family_statistic(S: np.ndarray, sigma2: np.ndarray, bins: np.ndarray) -> float:
    if bins.size == 0:
        return 0.0
    return float(np.sum(S[bins] / sigma2[bins]))


def family_threshold(n_bins: int, alpha: float) -> float:
    """Exact null quantile. T_c ~ Gamma(shape=n_bins, scale=1) when no CS2 component is present."""
    if n_bins <= 0:
        return np.inf
    return float(gamma_dist.ppf(1.0 - alpha, a=n_bins, scale=1.0))


def family_pvalue(T: float, n_bins: int) -> float:
    if n_bins <= 0:
        return 1.0
    return float(gamma_dist.sf(T, a=n_bins, scale=1.0))


def benjamini_hochberg(pvals: np.ndarray, q: float) -> np.ndarray:
    """BH-FDR across RECORDS [C14]. Returns a boolean acceptance mask."""
    p = np.asarray(pvals, dtype=float)
    m = p.size
    if m == 0:
        return np.zeros(0, dtype=bool)
    order = np.argsort(p)
    thresh = q * (np.arange(1, m + 1) / m)
    passed = p[order] <= thresh
    keep = np.zeros(m, dtype=bool)
    if passed.any():
        cut = np.nonzero(passed)[0].max()
        keep[order[: cut + 1]] = True
    return keep


def reference_bins(f: np.ndarray, test_bins: np.ndarray,
                   ref_hz: float = REF_HZ, guard_hz: float = GUARD_HZ) -> np.ndarray:
    """CFAR reference cells: within ref_hz of any test bin, minus test bins and a guard band."""
    n = f.size
    df = float(f[1] - f[0])
    r, g = int(round(ref_hz / df)), max(1, int(round(guard_hz / df)))
    mask = np.zeros(n, dtype=bool)
    for b in test_bins:
        mask[max(0, b - r): min(n, b + r + 1)] = True
    for b in test_bins:
        mask[max(0, b - g): min(n, b + g + 1)] = False
    return np.nonzero(mask)[0]


def cacfar_test(S: np.ndarray, f: np.ndarray, test_bins: np.ndarray, alpha: float,
                ref_hz: float = REF_HZ, guard_hz: float = GUARD_HZ) -> dict:
    """Family-level cell-averaging CFAR. Returns stat, p-value, threshold and the bin counts."""
    test_bins = np.asarray(test_bins, dtype=int)
    n = int(test_bins.size)
    ref = reference_bins(f, test_bins, ref_hz, guard_hz)
    m = int(ref.size)
    if n == 0 or m == 0:
        return {"stat": 0.0, "p": 1.0, "tau": np.inf, "reject_h0": False, "n": n, "m": m}
    stat = float(S[test_bins].mean() / max(S[ref].mean(), np.finfo(float).tiny))
    return {
        "stat": stat,
        "p": float(f_dist.sf(stat, 2 * n, 2 * m)),
        "tau": float(f_dist.ppf(1.0 - alpha, 2 * n, 2 * m)),
        "reject_h0": bool(stat > f_dist.ppf(1.0 - alpha, 2 * n, 2 * m)),
        "n": n, "m": m,
    }


def decide(S: np.ndarray, f: np.ndarray, gate_bins: dict, alpha: float,
           label_space: str = "L3") -> dict:
    """Per-RECORD admissibility verdict [C17].

    Each deciding family gets a CA-CFAR test at level alpha / n_families (union bound across families, C14:
    the families are not independent at coarse resolution, so no independence is assumed).
    Returns the physically supported class:
      * exactly the family with the largest normalised evidence among significant families, or
      * "normal" if no family is significant.
    A pseudo-label is ADMISSIBLE iff it equals this physical class. BH across records is applied by the
    caller on the returned min p-value.
    """
    fams = [fam for fam in gate_bins]
    a_fam = alpha / max(len(fams), 1)
    tests = {fam: cacfar_test(S, f, gate_bins[fam], a_fam) for fam in fams}
    sig = {fam: t for fam, t in tests.items() if t["reject_h0"]}
    cls_of = {"BPFO": "outer_race", "BPFI": "inner_race", "BPFB": "ball"}
    if sig:
        best = max(sig, key=lambda fam: sig[fam]["stat"])
        physical = cls_of[best]
    else:
        physical = "normal"
    return {
        "physical_class": physical,
        "tests": tests,
        "min_p": min(t["p"] for t in tests.values()) if tests else 1.0,
        "alpha_per_family": a_fam,
    }


def admissible(pseudo_label: str, verdict: dict) -> bool:
    return pseudo_label == verdict["physical_class"]
