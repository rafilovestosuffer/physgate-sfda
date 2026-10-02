"""C19 numerical feasibility gate. Runs BEFORE any pipeline component is implemented.

Blockers 1 and 4 (PLAN.md 0.2, 0.3) were both invisible in prose and surfaced only on doing the
arithmetic. Guards that catch bad RESULTS do not catch bad SPECIFICATIONS. This module computes the
governing quantities for every (dataset, condition, bearing, track) and asserts they are workable.

Three constraints, all evaluated on the SNAPPED NATIVE BIN GRID (no interpolation -- C12):
  (a) pooled family bins   N_c >= N_MIN      -- the family-sum Gamma(N_c,1) null needs support
  (b) anchor/shaft-harmonic separation >= SEP_MIN bins, else POSITION-DEGENERATE
  (c) revolutions per window >= REVS_MIN
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml

from kinematics import Kinematics, kinematics, slip_window, S_MAX_DEFAULT

ROOT = Path(__file__).resolve().parents[1]

N_MIN = 20        # pooled native bins per fault family
SEP_MIN = 2.0     # bins between a fault anchor and the nearest shaft harmonic
REVS_MIN = 5.0    # shaft revolutions per window
K_HARM = 5        # harmonics per family (pre-registered)

# DECISION families carry a gate verdict and therefore need a supported Gamma(N_c,1) null.
# They map one-to-one onto the label space: BPFO->Outer, BPFI->Inner, BPFB->Ball.
DECISION_FAMILIES = ("BPFO", "BPFI", "BPFB")
# ...but only those present in the dataset's label space actually decide anything.
# L3 = {Normal, Inner, Outer} (mandatory wherever PU is involved -- PU has NO ball class)
# L4 = L3 + {Ball}            (CWRU / JNU / HUST only)
LABEL_SPACE_FAMILIES = {"L3": ("BPFO", "BPFI"), "L4": ("BPFO", "BPFI", "BPFB")}
# CONTEXT channels are representation-only. There is NO CAGE CLASS in L3 or L4, so FTF can never
# decide anything; N_MIN does not apply to it. Its bin count is reported for information only.
# (FTF is intrinsically bin-poor: window width scales with line frequency and FTF ~ BPFO/n.)
CONTEXT_CHANNELS = ("FTF",)
FAMILIES = DECISION_FAMILIES + CONTEXT_CHANNELS


@dataclass
class Verdict:
    dataset: str
    condition: str
    bearing: str
    track: str
    T_s: float
    fs_hz: float
    rpm: float
    df_hz: float
    revolutions: float
    family_bins: Dict[str, int] = field(default_factory=dict)
    separations: Dict[str, float] = field(default_factory=dict)
    degenerate: List[str] = field(default_factory=list)
    label_space: str = "L4"
    failures: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.failures


def _bins_in(lo_hz: float, hi_hz: float, df: float) -> int:
    """Native FFT bins whose centres fall inside [lo, hi]. Snap-to-native, never interpolated."""
    if hi_hz < lo_hz:
        return 0
    first = math.ceil(lo_hz / df - 1e-12)
    last = math.floor(hi_hz / df + 1e-12)
    return max(0, last - first + 1)


def assess(dataset: str, condition: str, bearing: str, track: str,
           fs_hz: float, rpm: float, T_s: float, label_space: str = "L4",
           s_max: float = S_MAX_DEFAULT, k_harm: int = K_HARM) -> Verdict:
    k: Kinematics = kinematics(bearing)
    f_r = rpm / 60.0
    df = 1.0 / T_s
    v = Verdict(dataset, condition, bearing, track, T_s, fs_hz, rpm, df, T_s * f_r)
    v.label_space = label_space
    deciding = LABEL_SPACE_FAMILIES[label_space]

    # (c) revolutions
    if v.revolutions < REVS_MIN:
        v.failures.append(f"only {v.revolutions:.2f} shaft revolutions per window (need >= {REVS_MIN})")

    for fam in FAMILIES:
        # (a) pooled bins across the harmonic family -- width scales with k, so bins accumulate
        total = 0
        for h in range(1, k_harm + 1):
            lo, hi = slip_window(k, fam, s_max, harmonic=h)
            total += _bins_in(lo * f_r, hi * f_r, df)
        v.family_bins[fam] = total
        if fam in deciding and total < N_MIN:
            v.failures.append(f"{fam}: only {total} pooled native bins across k=1..{k_harm} (need >= {N_MIN})")

        # (b) separation from the nearest shaft harmonic, at k=1 (the binding case)
        order = getattr(k, fam)
        nearest = max(1, round(order))
        sep_bins = abs(order - nearest) * f_r / df
        v.separations[fam] = sep_bins
        if fam in deciding and sep_bins < SEP_MIN:
            level = "SAME-BIN" if sep_bins < 1.0 else "MARGINAL"
            v.degenerate.append(f"{fam}~{nearest}xf_r {sep_bins:.2f}b {level}")
            if sep_bins < 1.0:
                # Sub-bin collapse: the fault anchor and the shaft harmonic are the SAME ordinate.
                # Not recoverable by any window length. Only cyclostationary order can separate them.
                v.failures.append(f"{fam}: SAME-BIN collapse with {nearest}x f_r ({sep_bins:.2f} bins)")

    if v.degenerate:
        # Not a hard failure: it routes to the DRS-dependent path (C11). But it MUST be recorded,
        # because a frequency-position rule cannot work here -- only a cyclostationarity-order test.
        v.failures_note = "POSITION-DEGENERATE -> requires discrete/random separation (step 1.5)"
    return v


def sweep(T_grid=(0.5, 1.0, 1.5, 2.0, 2.5, 4.0), **kw) -> List[Verdict]:
    return [assess(T_s=T, **kw) for T in T_grid]


def _cases() -> List[dict]:
    ds = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    out = []
    cw = ds["datasets"]["CWRU"]
    for load, rpm in cw["conditions"].items():
        out.append(dict(dataset="CWRU", condition=f"load{load}hp", bearing=cw["bearing"],
                        fs_hz=cw["fs_hz"], rpm=float(rpm), label_space="L4"))
    pu = ds["datasets"]["PU"]
    for name, c in pu["conditions"].items():
        for geom in pu["geometry"]:          # C35: every PU geometry is certified, not just the majority
            out.append(dict(dataset="PU", condition=name, bearing=geom,
                            fs_hz=pu["fs_hz"], rpm=float(c["rpm"]), label_space="L3"))
    return out


def run_all(track: str = "A", T_s: float | None = None) -> List[Verdict]:
    ds = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    res = []
    for c in _cases():
        if T_s is not None:
            T = T_s
        elif track == "A":
            T = float(ds["tracks"]["A"]["window_seconds"])
        else:
            T = float(ds["tracks"]["R"]["window_samples"]) / c["fs_hz"]
        res.append(assess(track=track, T_s=T, **c))
    return res


def emit_windows_yaml(path: Path | None = None) -> Path:
    path = path or (ROOT / "configs" / "windows.yaml")
    ds = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    T_A = float(ds["tracks"]["A"]["window_seconds"])
    res = run_all("A")
    lines = [
        "# GENERATED by physics/feasibility.py -- do not hand-edit.",
        "# Track A window lengths are DERIVED from the three C19 constraints, not chosen.",
        f"# Constraints: pooled family bins >= {N_MIN}, anchor/shaft separation >= {SEP_MIN} bins,",
        f"#              revolutions >= {REVS_MIN}, s_max = {S_MAX_DEFAULT}, K = {K_HARM}.",
        f"track_A_seconds: {T_A}", "certified:",
    ]
    for v in res:
        lines.append(f"  - {{dataset: {v.dataset}, condition: {v.condition}, bearing: '{v.bearing}', "
                     f"T_s: {v.T_s}, samples: {int(round(v.T_s * v.fs_hz))}, df_hz: {v.df_hz:.4f}, "
                     f"revolutions: {v.revolutions:.1f}, label_space: {v.label_space}, "
                     f"min_decision_bins: {min(v.family_bins[f] for f in LABEL_SPACE_FAMILIES[v.label_space])}, "
                     f"ftf_context_bins: {v.family_bins['FTF']}, "
                     f"ok: {str(v.ok).lower()}, degenerate: \"{'; '.join(v.degenerate) or 'none'}\"}}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _fmt(v: Verdict) -> str:
    bins = " ".join(f"{f}:{v.family_bins[f]:>3d}" for f in FAMILIES)
    return (f"  {v.dataset:5s} {v.condition:12s} {v.bearing:5s} T={v.T_s:5.3f}s "
            f"df={v.df_hz:7.3f}Hz rev={v.revolutions:6.1f} | {bins} | "
            f"{'OK  ' if v.ok else 'FAIL'} {('DEGEN[' + ', '.join(v.degenerate) + ']') if v.degenerate else ''}")


if __name__ == "__main__":
    for track in ("R", "A"):
        print(f"===== TRACK {track} =====")
        for v in run_all(track):
            print(_fmt(v))
            for f in v.failures:
                print(f"        ! {f}")
        print()
    p = emit_windows_yaml()
    print(f"wrote {p.relative_to(ROOT)}")
