"""Pre-whitening tests. These test the PHYSICS the step exists for, on a synthetic 6203 lock:
a large deterministic shaft harmonic at 3*f_r sitting 1.77 % below a random-slip BPFO impulse train.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import numpy as np
import pytest
from scipy.signal import butter, sosfiltfilt

import prewhiten, ses
from kinematics import kinematics

FS = 64000.0
T = 3.0
FR = 25.0                       # PU 1500 rpm
N = int(FS * T)


def synthetic_6203_lock(seed=0, shaft_amp=3.0, fault_amp=1.0, slip_jitter=0.01):
    """Deterministic shaft harmonics (CS1) + slip-jittered BPFO impulses exciting a 9 kHz resonance (CS2)."""
    rng = np.random.default_rng(seed)
    t = np.arange(N) / FS
    k = kinematics("6203")
    bpfo = k.BPFO * FR                                             # 76.33 Hz
    shaft = sum(shaft_amp / h * np.sin(2 * np.pi * h * FR * t + h) for h in (1, 2, 3, 4, 5))
    period = 1.0 / bpfo
    times, tt = [], 0.0
    while tt < T:
        times.append(tt)
        tt += period * (1 + slip_jitter * rng.standard_normal())  # random slip -> CS2, not CS1
    imp = np.zeros(N)
    idx = (np.asarray(times) * FS).astype(int)
    imp[idx[idx < N]] = 1.0
    sos = butter(4, [8000 / (FS / 2), 10000 / (FS / 2)], btype="bandpass", output="sos")
    fault = fault_amp * 40 * sosfiltfilt(sos, imp)
    noise = 0.2 * rng.standard_normal(N)
    return shaft + fault + noise, bpfo


def test_cepstrum_prewhitening_flattens_magnitude():
    rng = np.random.default_rng(1)
    x = np.sin(2 * np.pi * 75 * np.arange(N) / FS) * 50 + rng.standard_normal(N)
    y = prewhiten.cepstrum_prewhiten(x)
    mag = np.abs(np.fft.rfft(y))[1:]
    assert mag.std() / mag.mean() < 1e-6, "CPW output must have a flat magnitude spectrum"


def test_prewhitening_suppresses_deterministic_harmonic():
    """A 50x sinusoid dominates the raw spectrum; after CPW its bin is no larger than any other."""
    rng = np.random.default_rng(2)
    t = np.arange(N) / FS
    x = 50 * np.sin(2 * np.pi * 75.0 * t) + rng.standard_normal(N)
    for method in ("cepstrum", "lpc"):
        y = prewhiten.prewhiten(x, method)
        P = np.abs(np.fft.rfft(y)) ** 2
        f = np.fft.rfftfreq(N, 1 / FS)
        b = np.argmin(np.abs(f - 75.0))
        ratio = P[b] / np.median(P[1:])
        assert ratio < 50, f"{method}: sinusoid still {ratio:.0f}x the median after pre-whitening"


def test_prewhitening_preserves_the_cs2_fault_line_on_the_6203_lock():
    """THE point of C11: after CPW the envelope spectrum must show BPFO, not the shaft harmonic 1.77 % away."""
    x, bpfo = synthetic_6203_lock()
    y = prewhiten.cepstrum_prewhiten(x)
    f, S = ses.squared_envelope_spectrum(y, FS, band=(8000.0, 10000.0))
    df = f[1] - f[0]
    b_fault = int(round(bpfo / df))
    b_shaft = int(round(3 * FR / df))
    assert abs(b_fault - b_shaft) >= 2, "test geometry must resolve the two lines (T=3 s -> 3.98 bins)"
    floor = np.median(S[(f > 20) & (f < 600)])
    fault_peak = S[b_fault - 1: b_fault + 2].max()
    assert fault_peak > 20 * floor, f"BPFO line not detected after CPW ({fault_peak/floor:.1f}x floor)"


@pytest.mark.parametrize("method", ["cepstrum", "lpc", "none"])
def test_prewhiten_output_is_finite_and_normalised(method):
    x, _ = synthetic_6203_lock(seed=3)
    y = prewhiten.prewhiten(x, method)
    assert np.isfinite(y).all()
    assert y.size == x.size
    assert abs(np.std(y[100:]) - 1.0) < 0.1


# ---------------------------------------------------------------------------- band selection
import band_select


def test_kurtogram_grid_matches_fast_kurtogram_structure():
    assert [band_select._n_bands(l) for l in (0.0, 1.0, 1.6, 2.0, 2.6, 3.0)] == [1, 2, 3, 4, 6, 8]


def test_kurtogram_scores_gaussian_noise_near_zero():
    rng = np.random.default_rng(4)
    bands = band_select.kurtogram(rng.standard_normal(N), FS, max_level=4)
    assert max(abs(b.kurtosis) for b in bands) < 0.2


def test_kurtogram_finds_the_fault_resonance_after_prewhitening():
    """Fault impulses excite 8-10 kHz; a strong shaft tone and noise elsewhere. Selected band must cover 9 kHz."""
    x, _ = synthetic_6203_lock(seed=5)
    b = band_select.select_band(prewhiten.cepstrum_prewhiten(x), FS, max_level=6, max_fault_hz=600.0)
    assert b.lo_hz <= 9000.0 <= b.hi_hz, f"selected {b}"
    assert b.kurtosis > 0.5


def test_band_width_floor_protects_fault_harmonics():
    x, _ = synthetic_6203_lock(seed=6)
    b = band_select.select_band(prewhiten.cepstrum_prewhiten(x), FS, max_fault_hz=1000.0)
    assert b.width_hz >= 2000.0
