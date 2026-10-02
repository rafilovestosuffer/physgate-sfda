"""C30 comb-scan detector: null calibration, power under speed/slip offset, and specificity.

These tests encode the two failure modes found on real CWRU data (results/m4/M4_INVALID.md):
  * sensitivity: a line displaced BELOW theoretical (speed error) must still be detected;
  * specificity: a strong stray line inside another family's window must not steal the verdict.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import numpy as np
import pytest
from scipy.signal import butter, sosfiltfilt, lfilter

import comb, prewhiten, ses
from kinematics import kinematics

FS, T, RPM = 12000.0, 5.0, 1772.0
N = int(FS * T)
F_R = RPM / 60.0
BAND = (2000.0, 4000.0)
K6205 = kinematics("6205")


def _resonate(imp, band=(2500.0, 3500.0)):
    sos = butter(4, [band[0] / (FS / 2), band[1] / (FS / 2)], btype="bandpass", output="sos")
    return sosfiltfilt(sos, imp)


def impulse_train(rate_hz, rng, jitter=0.01, am_hz=None, am_depth=0.8, amp=1.0):
    imp = np.zeros(N)
    t = 0.0
    while t < T:
        i = int(t * FS)
        if i < N:
            imp[i] = 1.0 + (am_depth * np.cos(2 * np.pi * am_hz * t) if am_hz else 0.0)
        t += (1.0 / rate_hz) * (1 + jitter * rng.standard_normal())
    return amp * 40 * _resonate(imp)


def record(kind=None, delta=0.0, seed=0, colored=False, stray_hz=None, stray_depth=0.3):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(N) * 0.4
    if colored:
        x = lfilter([1.0], [1.0, -0.7, 0.25], x)
    if kind == "inner":
        x += impulse_train(K6205.BPFI * F_R * (1 + delta), rng, am_hz=F_R)
    elif kind == "outer":
        x += impulse_train(K6205.BPFO * F_R * (1 + delta), rng)
    if stray_hz is not None:
        # An ISOLATED envelope line. Squared-envelope of c*(1 + m cos) has a 2nd harmonic of relative size
        # m/4, so a shallow depth (m = 0.3 -> 7.5 %) yields essentially ONE line. A deep modulation would create
        # a two-harmonic family, which is physically indistinguishable from a weak real fault.
        carrier = _resonate(rng.standard_normal(N))
        x += 6.0 * carrier * (1 + stray_depth * np.cos(2 * np.pi * stray_hz * np.arange(N) / FS))
    y = prewhiten.cepstrum_prewhiten(x)
    return ses.squared_envelope_spectrum(y, FS, band=BAND)


def verdict(**kw):
    f, S = record(**kw)
    return comb.decide(f, S, K6205, F_R, alpha=0.05, label_space="L3")


def test_surrogate_pvalues_are_approximately_calibrated():
    """Report-grade check on the surrogate rank test ALONE (before the multiplicity rule).
    Tolerance is loose on purpose: the surrogates are correlated, so the null is coarse. The GATE's realised
    false-acceptance rate is measured on real healthy records, not asserted here."""
    ps = []
    for s in range(120):
        f, S = record(kind=None, seed=9000 + s)
        t = comb.test_families(f, S, K6205, F_R, "L3")
        ps += [t["BPFO"]["p"], t["BPFI"]["p"]]
    ps = np.array(ps)
    assert (ps <= 0.025).mean() <= 0.06
    assert 0.35 <= (ps <= 0.5).mean() <= 0.65


@pytest.mark.parametrize("colored", [False, True], ids=["white", "coloured"])
def test_null_false_alarm_rate_is_not_anticonservative(colored):
    trials, alpha = 120, 0.05
    fa = sum(verdict(kind=None, seed=1000 + s, colored=colored)["physical_class"] != "normal" for s in range(trials))
    far = fa / trials
    se = (alpha * (1 - alpha) / trials) ** 0.5
    assert far <= alpha + 3 * se, f"realised FAR {far:.3f} > {alpha} + 3SE"


def test_surrogates_never_alias_a_family():
    specs = comb.family_specs(K6205, "L4")
    for spec in specs:
        surr = comb.surrogate_orders(spec, specs)
        assert surr.size == comb.N_SURR
        for F in specs:
            for h in range(1, 6):
                for h2 in range(1, 6):
                    assert np.all(np.abs(h * surr - h2 * F.order) > comb.S_MAX_DEFAULT * h2 * F.order)


@pytest.mark.parametrize("delta", [-0.003, 0.0, 0.015], ids=["below_-0.3pct", "exact", "above_+1.5pct"])
def test_inner_race_detected_despite_offset(delta):
    """Record 209's line sat 0.24 % BELOW theoretical and escaped the one-sided window."""
    v = verdict(kind="inner", delta=delta, seed=7)
    assert v["physical_class"] == "inner_race", v["tests"]


def test_outer_race_detected():
    v = verdict(kind="outer", delta=-0.005, seed=8)
    assert v["physical_class"] == "outer_race", v["tests"]


def test_stray_line_inside_bpfo_window_does_not_steal_inner_verdict():
    """The per-window-max failure: a strong isolated line in another family's window. The comb needs the
    family's harmonics to align under one delta, which a single stray line cannot supply."""
    stray = K6205.BPFO * F_R * 1.01
    v = verdict(kind="inner", delta=0.0, seed=9, stray_hz=stray)
    assert v["physical_class"] == "inner_race", v["tests"]


def test_isolated_single_line_is_rarely_called_a_fault():
    stray = K6205.BPFO * F_R * 1.01
    called = sum(verdict(kind=None, seed=200 + s, stray_hz=stray)["physical_class"] != "normal" for s in range(20))
    assert called <= 4, f"{called}/20 records with one isolated line were called faulty"


def test_inner_fault_does_not_leak_into_outer_family():
    """Records 210/212 failure mode: a real inner-race family must not make BPFO significant."""
    leaks = 0
    for s in range(10):
        f, S = record(kind="inner", seed=300 + s)
        t = comb.test_families(f, S, K6205, F_R, "L3")
        leaks += t["BPFO"]["p"] <= 0.025
    assert leaks <= 2, f"BPFO significant in {leaks}/10 inner-fault records"
