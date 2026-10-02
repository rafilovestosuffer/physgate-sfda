"""Kinematics tests. The arbiter for bearing geometry.

TOLERANCE POLICY [C13, refined from measurement -- see docstring of test_race_lines_vs_cwru_table]:
  * PRIMARY assertions for BSF/BPFB are against the CLOSED-FORM FORMULA (exact to 1e-12).
    No external table is ever the arbiter for the ball line, because "BSF" denotes two different
    quantities across CWRU (2x spin) and Smith & Randall (true spin).
  * SECONDARY cross-check against CWRU's published table uses tolerances derived from the measured
    deviations, not guessed. CWRU tabulates to 4-5 dp so rounding alone permits ~5e-5.
"""
import math, sys, pathlib
from pathlib import Path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import pytest
from kinematics import (Kinematics, kinematics, slip_window, UnverifiedBearingError, S_MAX_DEFAULT)

# Measured worst deviations vs CWRU's published table (this repo, 2026-09-13):
#   race/cage lines  max 1.19e-4  (6203 BPFO)   -> atol 2e-4
#   ball line BPFB   max 2.77e-4  (6203 BPFB)   -> atol 5e-4
ATOL_RACE = 2e-4
ATOL_BALL = 5e-4

CWRU_PUBLISHED = {
    "6205": {"BPFO": 3.5848, "BPFI": 5.4152, "FTF": 0.39828, "BPFB": 4.7135},
    "6203": {"BPFO": 3.0530, "BPFI": 4.9469, "FTF": 0.38170, "BPFB": 3.9874},
}
FORMULA_EXACT = {  # closed form, independent of any table
    "6205": {"BSF": 2.356721, "BPFB": 4.713443},
    "6203": {"BSF": 1.993839, "BPFB": 3.987677},
}


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_race_lines_vs_cwru_table(bearing):
    k = kinematics(bearing)
    for line in ("BPFO", "BPFI", "FTF"):
        assert getattr(k, line) == pytest.approx(CWRU_PUBLISHED[bearing][line], abs=ATOL_RACE)


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_ball_line_against_formula_not_table(bearing):
    """C13: the ball line is asserted against the formula. The table is a loose cross-check only."""
    k = kinematics(bearing)
    assert k.BSF == pytest.approx(FORMULA_EXACT[bearing]["BSF"], abs=1e-6)
    assert k.BPFB == pytest.approx(FORMULA_EXACT[bearing]["BPFB"], abs=1e-6)
    assert k.BPFB == pytest.approx(CWRU_PUBLISHED[bearing]["BPFB"], abs=ATOL_BALL)


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_bpfb_is_exactly_twice_bsf(bearing):
    k = kinematics(bearing)
    assert k.BPFB == 2.0 * k.BSF          # exact, no tolerance
    assert k.BPFB != k.BSF                # never conflated


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_ftf_equals_bpfo_over_n(bearing):
    """Exact identity for every geometry. Guards against an inconsistent element count."""
    k = kinematics(bearing)
    assert k.FTF == pytest.approx(k.BPFO / k.n, abs=1e-12)


def test_6203_requires_eight_elements():
    """n=9 gives BPFO 3.4348 and fails to reproduce CWRU's table. The unit test is the arbiter."""
    k = kinematics("6203")
    assert k.n == 8
    r = k.r
    assert (9 / 2.0) * (1 - r) == pytest.approx(3.4348, abs=1e-3)   # what n=9 would wrongly give


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_line_ordering_bpfo_lt_bpfb_lt_bpfi(bearing):
    """Required by harmonic_coords. Holds iff 2/(n+2) < r < 2/(n-2); assert the closed form too."""
    k = kinematics(bearing)
    assert k.ordering_ok()
    assert 2.0 / (k.n + 2) < k.r < 2.0 / (k.n - 2)


@pytest.mark.parametrize("bearing", ["6205", "6203"])
def test_slip_window_signs_and_exact_bpfo_shift(bearing):
    """Outer-race lines fall BELOW theoretical, inner-race come out ABOVE. dBPFO/BPFO == -s_max."""
    k = kinematics(bearing)
    s = S_MAX_DEFAULT

    lo, hi = slip_window(k, "BPFO", s)
    assert hi == k.BPFO                                   # one-sided, anchored at theoretical
    assert lo < k.BPFO
    assert (lo - k.BPFO) / k.BPFO == pytest.approx(-s, abs=1e-15)   # machine precision

    lo_i, hi_i = slip_window(k, "BPFI", s)
    assert lo_i == k.BPFI
    assert hi_i > k.BPFI
    # geometry-dependent, never hard-coded: +s * BPFO/BPFI
    assert (hi_i - k.BPFI) / k.BPFI == pytest.approx(s * k.BPFO / k.BPFI, abs=1e-15)

    for line in ("BPFB", "FTF"):                          # UNVERIFIED under slip -> symmetric
        lo_s, hi_s = slip_window(k, line, s)
        c = getattr(k, line)
        assert (c - lo_s) == pytest.approx(hi_s - c, abs=1e-12)


def test_bpfi_shift_is_not_the_6205_constant():
    """Regression guard: +1.32% is the 6205 value only. 6203 must differ."""
    k5, k3 = kinematics("6205"), kinematics("6203")
    sh = lambda k: S_MAX_DEFAULT * k.BPFO / k.BPFI
    assert sh(k5) == pytest.approx(0.013239, abs=1e-5)
    assert sh(k3) == pytest.approx(0.012343, abs=1e-5)
    assert sh(k5) != sh(k3)


@pytest.mark.parametrize("bearing", ["N205", "NU205", "6204", "6206", "6207", "6208"])
def test_unverified_bearings_raise(bearing):
    """Silent numbers are the failure mode this module exists to prevent."""
    with pytest.raises(UnverifiedBearingError, match="UNVERIFIED"):
        kinematics(bearing)


def test_harmonic_windows_scale_with_k():
    """Window width scales with harmonic index -- this is why the family sum accumulates bins."""
    k = kinematics("6203")
    w1 = lambda h: (lambda t: t[1] - t[0])(slip_window(k, "BPFO", S_MAX_DEFAULT, harmonic=h))
    assert w1(2) == pytest.approx(2 * w1(1), rel=1e-12)
    assert w1(5) == pytest.approx(5 * w1(1), rel=1e-12)


# ---- C35: Paderborn geometry is per bearing, from the dataset's own profile PDFs ----
def test_pu_geometry_map_covers_every_bearing_exactly_once():
    import yaml
    ds = yaml.safe_load((Path(__file__).resolve().parents[1] / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    pu = ds["datasets"]["PU"]
    mapped = [b for ids in pu["geometry"].values() for b in ids]
    roster = [b for ids in pu["bearings"].values() for b in ids]
    assert len(mapped) == len(set(mapped)) == 32
    assert set(mapped) == set(roster)


def test_pu_orders_and_manufacturer_dependent_lock():
    a, b = kinematics("6203_PU_2905"), kinematics("6203_PU_2855")
    assert a.BPFO == pytest.approx(4 * (1 - 6.75 / 29.05), abs=1e-12)
    assert a.BPFO == pytest.approx(3.0706, abs=1e-4) and b.BPFO == pytest.approx(3.0543, abs=1e-4)
    lo_a, _ = slip_window(a, "BPFO", 0.02)
    lo_b, _ = slip_window(b, "BPFO", 0.02)
    assert lo_a > 3.0 > lo_b          # 3xf_r outside the IBU/MTK BPFO window, inside the FAG one
    assert abs(a.BPFB - 4.0) < 0.02 * a.BPFB and abs(b.BPFB - 4.0) < 0.02 * b.BPFB   # BPFB collides on both
