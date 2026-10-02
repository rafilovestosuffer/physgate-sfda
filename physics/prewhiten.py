"""Discrete/random separation (DRS) -- mandatory pipeline step 1.5 [C11].

Why it is mandatory: on the 6203 (Paderborn), BPFO sits 1.77 % from 3*f_r, BPFI 1.06 % from 5*f_r and
BPFB 0.31 % from 4*f_r. No slip window separates them by frequency position (PLAN 0.2). What does
separate them is CYCLOSTATIONARY ORDER: shaft harmonics are first-order cyclostationary (CS1,
deterministic, phase-locked), bearing faults are second-order (CS2, random because slip destroys phase
coherence). DRS removes the CS1 content before envelope analysis. It is Smith & Randall's (2015) own
pre-processing, and their Method 2, cepstrum pre-whitening, had the highest success rate of the three.

Default: cepstrum pre-whitening (CPW), Borghesani, Pennacchi, Randall, Sawalhi & Ricci, MSSP 36 (2013):
    x_w = Re{ F^-1[ X(f) / |X(f)| ] }
i.e. set the real cepstrum to zero except the phase: the magnitude spectrum is flattened, removing all
discrete (deterministic) peaks and the transfer-path colouring, while phase -- which carries impulse
timing -- is kept.

Alternative: linear-prediction (AR) residual. Discrete components are predictable; the residual is not.
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve_toeplitz


def cepstrum_prewhiten(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    X = np.fft.rfft(x - x.mean())
    y = np.fft.irfft(X / (np.abs(X) + eps), n=x.size)
    return y / (y.std() + eps)


def lpc_residual(x: np.ndarray, order: int = 64) -> np.ndarray:
    """Linear-prediction residual via Yule-Walker (Levinson through a Toeplitz solve)."""
    x = np.asarray(x, dtype=float)
    x = x - x.mean()
    n = x.size
    # Wiener-Khinchin: autocorrelation = inverse FFT of the power spectrum. O(n log n), not O(n^2).
    r = np.fft.irfft(np.abs(np.fft.rfft(x, n=2 * n)) ** 2, n=2 * n)[: order + 1] / n
    a = solve_toeplitz(r[:order], r[1: order + 1])
    pred = np.convolve(x, np.r_[0.0, a], mode="full")[:n]
    e = x - pred
    e[:order] = 0.0
    return e / (e[order:].std() + 1e-12)


def prewhiten(x: np.ndarray, method: str = "cepstrum", **kw) -> np.ndarray:
    if method == "cepstrum":
        return cepstrum_prewhiten(x, **kw)
    if method == "lpc":
        return lpc_residual(x, **kw)
    if method == "none":
        x = np.asarray(x, dtype=float)
        return (x - x.mean()) / (x.std() + 1e-12)
    raise ValueError(f"unknown pre-whitening method {method!r}")
