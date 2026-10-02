"""Session-1 acceptance test 3: the gate's central statistical claim, verified EMPIRICALLY.

Under H0 (Gaussian background, no CS2 component) the realised false-alarm rate of the family test
must match nominal alpha within Monte-Carlo error, for BOTH white and coloured backgrounds.
This is a regression guard. The full calibration table (1500 trials, several N and alpha) is a paper
figure produced separately; this test uses fewer trials to stay under the CPU time budget and a
3-sigma binomial tolerance so it cannot flake.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import numpy as np
import pytest
from scipy.signal import lfilter
import ses, gate

FS, T = 12000.0, 3.0
N = int(FS * T)


def _family(m_idx, n, rng, clusters=5):
    per = max(1, n // clusters)
    starts = rng.choice(m_idx[: -per - 1], size=clusters, replace=False)
    return np.unique(np.concatenate([np.arange(s, s + per) for s in starts]))[:n]


def _realised_far(colored: bool, alpha: float, n_bins: int, trials: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    hits = 0
    for _ in range(trials):
        x = rng.standard_normal(N)
        if colored:
            x = lfilter([1.0], [1.0, -0.7, 0.25], x)     # strongly non-white AR(2) background
        f, S = ses.squared_envelope_spectrum(x, FS, band=(2000.0, 5000.0))
        m = np.nonzero((f >= 10) & (f <= 600))[0]
        hits += gate.cacfar_test(S, f, _family(m, n_bins, rng), alpha)["reject_h0"]
    return hits / trials


@pytest.mark.parametrize("colored", [False, True], ids=["white", "coloured"])
def test_cacfar_false_alarm_rate_matches_alpha(colored):
    alpha, trials = 0.05, 400
    far = _realised_far(colored, alpha, n_bins=45, trials=trials, seed=20260913 + int(colored))
    se = (alpha * (1 - alpha) / trials) ** 0.5
    assert abs(far - alpha) <= 3 * se, f"realised FAR {far:.3f} vs nominal {alpha} (3SE={3*se:.3f})"


def test_normalised_ses_ordinates_are_exponential():
    """The marginal the whole null rests on: SES/floor ~ Exp(1) in the fault-frequency region."""
    from scipy import stats
    rng = np.random.default_rng(1)
    f, S = ses.squared_envelope_spectrum(rng.standard_normal(N), FS, band=(2000.0, 5000.0))
    z = (S / gate.noise_floor(S, f))[(f >= 10) & (f <= 600)]
    assert abs(z.mean() - 1.0) < 0.08
    assert stats.kstest(z, "expon").pvalue > 0.01


def test_adjacent_ses_bins_are_uncorrelated():
    """Independence the family sum relies on. Interpolation would break this [C12]."""
    rng = np.random.default_rng(2)
    f, S = ses.squared_envelope_spectrum(rng.standard_normal(N), FS, band=(2000.0, 5000.0))
    z = S[(f >= 10) & (f <= 600)]
    for lag in (1, 2, 3):
        assert abs(np.corrcoef(z[:-lag], z[lag:])[0, 1]) < 0.08


def test_gate_detects_a_real_cs2_line():
    """Power sanity check: an amplitude-modulated resonance at a 'fault' rate must be detected."""
    rng = np.random.default_rng(3)
    t = np.arange(N) / FS
    f_fault = 105.87                                   # CWRU BPFO @ 1772 rpm
    carrier = rng.standard_normal(N)
    x = carrier * (1.0 + 0.6 * np.cos(2 * np.pi * f_fault * t)) + 0.5 * rng.standard_normal(N)
    f, S = ses.squared_envelope_spectrum(x, FS, band=(2000.0, 5000.0))
    windows = [((1 - 0.02) * k * f_fault, k * f_fault) for k in range(1, 6)]
    bins = gate.family_bins(f, windows)
    assert gate.cacfar_test(S, f, bins, alpha=0.01)["reject_h0"]


def test_bh_step_up_thresholds():
    """BH thresholds for m=5, q=0.05 are k*q/m = 0.01, 0.02, 0.03, 0.04, 0.05."""
    at_boundary = gate.benjamini_hochberg(np.array([0.001, 0.002, 0.030, 0.2, 0.9]), q=0.05)
    assert at_boundary.tolist() == [True, True, True, False, False]      # 0.030 <= 0.03 accepted
    just_over = gate.benjamini_hochberg(np.array([0.001, 0.002, 0.031, 0.2, 0.9]), q=0.05)
    assert just_over.tolist() == [True, True, False, False, False]       # 0.031 > 0.03 rejected
    # step-up property: a later p meeting its own threshold rescues earlier larger ones
    rescued = gate.benjamini_hochberg(np.array([0.011, 0.012, 0.013, 0.014, 0.05]), q=0.05)
    assert rescued.all()
