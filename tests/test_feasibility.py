"""C19 feasibility tests. These run BEFORE any pipeline component and gate the whole project.

Regression guards for the two blockers that were invisible in prose (PLAN.md 0.2, 0.3).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "physics"))

import pytest
import yaml
from feasibility import (assess, run_all, _cases, LABEL_SPACE_FAMILIES, N_MIN,
                         SEP_MIN, REVS_MIN, emit_windows_yaml)

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_track_A_certifies_every_condition():
    """Every (dataset, condition, bearing) must pass at the derived Track A window."""
    for v in run_all("A"):
        assert v.ok, f"{v.dataset}/{v.condition} failed: {v.failures}"


def test_track_R_2048_is_rejected_for_track_A_use():
    """BLOCKER 4 REGRESSION GUARD.

    At 2048 samples the slip window holds <0.4 native bins and the fault channels collapse into
    the same bin as the shaft harmonics. This MUST fail. If it ever passes, the resolution
    analysis has been silently broken.
    """
    verdicts = run_all("R")
    assert all(not v.ok for v in verdicts), "2048-sample windows must NEVER certify for Track A"
    pu = [v for v in verdicts if v.dataset == "PU"]
    for v in pu:
        assert v.revolutions < 1.0, f"PU at 2048 should be <1 shaft revolution, got {v.revolutions}"
        assert any("SAME-BIN" in d for d in v.degenerate), "PU at 2048 must show SAME-BIN collapse"


def test_6203_shaft_harmonic_lock_is_documented():
    """BLOCKER 1 REGRESSION GUARD (PLAN 0.2).

    The 6203's BPFB sits 0.31% from 4x f_r. No window width separates them. Assert the lock is
    still detected, so nobody 'fixes' it by widening or narrowing s_max.
    """
    from kinematics import kinematics
    k = kinematics("6203")
    for line, nearest, tol_pct in (("BPFO", 3, 1.8), ("BPFB", 4, 0.4), ("BPFI", 5, 1.1)):
        dev = abs(getattr(k, line) - nearest) / nearest * 100
        assert dev < tol_pct, f"6203 {line} should sit within {tol_pct}% of {nearest}x f_r, got {dev:.2f}%"
    # and the 6205 must NOT have the lock -- the contrast is the experiment
    k5 = kinematics("6205")
    for line in ("BPFO", "BPFB", "BPFI"):
        o = getattr(k5, line)
        dev = abs(o - round(o)) / round(o) * 100
        assert dev > 5.0, f"6205 {line} unexpectedly close to a shaft harmonic ({dev:.2f}%)"


def test_ftf_is_context_not_decision():
    """There is no cage class in L3 or L4, so FTF must never gate. It is bin-poor by construction."""
    for space, fams in LABEL_SPACE_FAMILIES.items():
        assert "FTF" not in fams, f"FTF must not be a deciding family in {space}"
    assert "BPFB" not in LABEL_SPACE_FAMILIES["L3"], "PU has no ball class; BPFB cannot decide in L3"


def test_windows_yaml_is_generated_and_consistent():
    p = emit_windows_yaml()
    d = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert d["track_A_seconds"] == 3.0
    assert len(d["certified"]) == len(_cases())
    for row in d["certified"]:
        assert row["ok"] is True
        assert row["min_decision_bins"] >= N_MIN
        assert row["revolutions"] >= REVS_MIN


def test_shorter_window_would_collapse_pu_n09():
    """T_A was DERIVED, not chosen. Show the boundary: 1.0 s collapses PU N09 to sub-bin."""
    # binding geometry is the FAG 6203 (Pd 28.55 mm, smallest BPFO-3xf_r offset) -- C35
    n09 = [c for c in _cases() if c["condition"] == "N09_M07_F10" and c["bearing"] == "6203_PU_2855"][0]
    assert not assess(track="A", T_s=1.0, **n09).ok, "T=1.0s must fail on PU N09"
    assert assess(track="A", T_s=3.0, **n09).ok, "T=3.0s must pass on PU N09"
    # and at the rejected 2.0 s, N09 is merely MARGINAL rather than failing -- record why we moved up
    v2 = assess(track="A", T_s=2.0, **n09)
    assert v2.ok and v2.degenerate, "T=2.0s should pass but be marginal on PU N09"
