"""KNEOS-HC transform tests: geometry independence of the SHAPE, harmonic-index alignment,
refusal at infeasible resolution, and gate verdicts on synthetic records."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import numpy as np
import pytest
from scipy.signal import butter, sosfiltfilt

import gate, ses, prewhiten
from harmonic_coords import harmonic_coordinates, FeasibilityError, CHANNELS, K_HARM, J_SIDE, M_SUB
from kinematics import kinematics


def fault_record(bearing, line, fs, rpm, T=3.0, seed=0, amp=1.0, jitter=0.01, band=(8000, 10000)):
    rng = np.random.default_rng(seed)
    n = int(fs * T)
    k = kinematics(bearing)
    f_r = rpm / 60.0
    x = 0.3 * rng.standard_normal(n)
    if line is not None:
        period = 1.0 / (getattr(k, line) * f_r)
        imp = np.zeros(n); t = 0.0
        while t < T:
            i = int(t * fs)
            if i < n:
                # inner-race impulses are amplitude-modulated by the load zone at f_r
                imp[i] = 1.0 + (0.8 * np.cos(2 * np.pi * f_r * t) if line == "BPFI" else 0.0)
            t += period * (1 + jitter * rng.standard_normal())
        sos = butter(4, [band[0] / (fs / 2), band[1] / (fs / 2)], btype="bandpass", output="sos")
        x += amp * 40 * sosfiltfilt(sos, imp)
    return x, f_r


def spectrum(x, fs, band=(8000, 10000)):
    return ses.squared_envelope_spectrum(prewhiten.cepstrum_prewhiten(x), fs, band=band)


@pytest.mark.parametrize("bearing,fs,rpm", [("6205", 12000.0, 1772.0), ("6203", 64000.0, 1500.0),
                                            ("6203", 64000.0, 900.0)])
def test_tensor_shape_is_geometry_independent(bearing, fs, rpm):
    band = (2000, 5000) if fs == 12000.0 else (8000, 10000)
    x, f_r = fault_record(bearing, None, fs, rpm, band=band)
    f, S = spectrum(x, fs, band)
    r = harmonic_coordinates(f, S, kinematics(bearing), f_r, "L3")
    assert r.tensor.shape == (len(CHANNELS), K_HARM, 2 * J_SIDE + 1, M_SUB) == (5, 5, 5, 9)
    assert np.isfinite(r.tensor).all()


def test_refuses_at_2048_samples():
    """Blocker 4 regression guard, at the transform itself."""
    x, f_r = fault_record("6203", "BPFO", 64000.0, 1500.0, T=2048 / 64000.0)
    f, S = spectrum(x, 64000.0)
    with pytest.raises(FeasibilityError, match="native bins"):
        harmonic_coordinates(f, S, kinematics("6203"), f_r, "L3")


def test_outer_fault_lands_on_outer_channel_harmonic_rows():
    fs = 64000.0
    x, f_r = fault_record("6203", "BPFO", fs, 1500.0, seed=1)
    f, S = spectrum(x, fs)
    r = harmonic_coordinates(f, S, kinematics("6203"), f_r, "L3")
    O, I = CHANNELS.index("O"), CHANNELS.index("I")
    centre = J_SIDE
    o_peak = r.tensor[O, :, centre, :].max(axis=1)      # per harmonic
    i_peak = r.tensor[I, :, centre, :].max(axis=1)
    assert (o_peak[:3] > i_peak[:3]).all(), f"outer evidence {o_peak} vs inner {i_peak}"


@pytest.mark.parametrize("line,expected", [("BPFO", "outer_race"), ("BPFI", "inner_race"), (None, "normal")])
def test_gate_verdicts_on_synthetic_6205(line, expected):
    """6205 has no shaft-harmonic lock, so the gate should get all three right."""
    fs, band = 12000.0, (2000, 5000)
    x, f_r = fault_record("6205", line, fs, 1772.0, seed=2, band=band)
    f, S = spectrum(x, fs, band)
    r = harmonic_coordinates(f, S, kinematics("6205"), f_r, "L3")
    v = gate.decide(S, f, r.gate_bins, alpha=0.01, label_space="L3")
    assert v["physical_class"] == expected, v
    assert gate.admissible(expected, v)


def test_pure_noise_is_rarely_admitted_as_a_fault():
    fs, band = 12000.0, (2000, 5000)
    fp = 0
    for seed in range(40):
        x, f_r = fault_record("6205", None, fs, 1772.0, seed=100 + seed, band=band)
        f, S = spectrum(x, fs, band)
        r = harmonic_coordinates(f, S, kinematics("6205"), f_r, "L3")
        fp += gate.decide(S, f, r.gate_bins, alpha=0.05)["physical_class"] != "normal"
    assert fp <= 6, f"{fp}/40 noise records called faulty at alpha=0.05"
