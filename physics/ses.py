"""Squared envelope spectrum. ONE SEGMENT, NO WELCH AVERAGING [C18].

Welch is ruled out by arithmetic, not preference (PLAN.md 0.5): at 4 segments the PU BPFO k=1 slip
window holds 1.5 native bins. Variance reduction comes from the family SUM instead -- Gamma(N,1) has
CV = 1/sqrt(N), so N=66 gives ~12% against 100% for a single chi2_2 ordinate. The family sum IS the
averaging, and unlike Welch it preserves the resolution the windows depend on.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import hilbert, butter, sosfiltfilt


def bandpass(x: np.ndarray, fs: float, lo: float, hi: float, order: int = 4) -> np.ndarray:
    nyq = fs / 2.0
    lo_n, hi_n = max(lo / nyq, 1e-6), min(hi / nyq, 1 - 1e-6)
    if hi_n <= lo_n:
        raise ValueError(f"bad band [{lo}, {hi}] for fs={fs}")
    sos = butter(order, [lo_n, hi_n], btype="bandpass", output="sos")
    return sosfiltfilt(sos, x)


def squared_envelope(x: np.ndarray) -> np.ndarray:
    """|analytic(x)|^2, mean-removed. Mean removal kills the DC ordinate, which is not CS2."""
    env2 = np.abs(hilbert(x)) ** 2
    return env2 - env2.mean()


def squared_envelope_spectrum(x: np.ndarray, fs: float,
                              band: tuple[float, float] | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Return (freqs_hz, SES). One periodogram of the whole window -- no segmenting, no averaging.

    Frequency resolution is exactly 1/T where T = len(x)/fs. That resolution is what the slip
    windows are sized against, so it must not be traded away.
    """
    if band is not None:
        x = bandpass(x, fs, *band)
    e = squared_envelope(np.asarray(x, dtype=float))
    n = e.size
    S = np.abs(np.fft.rfft(e)) ** 2 / n
    f = np.fft.rfftfreq(n, d=1.0 / fs)
    return f, S
