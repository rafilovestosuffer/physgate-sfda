"""KNEOS-HC: kinematics-normalised envelope spectrum in HARMONIC COORDINATES.

One call produces BOTH objects the paper's coupling claim rests on, from the SAME anchors and windows:
  * `tensor`    -- fixed shape (5, K, 2J+1, M) for the network: every bearing, machine, speed and
                   sampling rate maps harmonic k of family c to index k. Interpolated onto M sub-bins
                   (legitimate: no statistical null is claimed for the network input).
  * `gate_bins` -- per deciding family, the NATIVE SES bins inside the union of its slip windows.
                   Snapped, never interpolated [C12], so the CA-CFAR null in gate.py holds exactly.
State this in the paper precisely: shared anchors and windows, different discretisation. Not identical.

Why not a single warped axis: BPFO < BPFB < BPFI for both verified bearings, so the addendum's anchors
(BPFO->1, BPFI->2, BPFB->3) are non-monotone and no monotone interpolant exists; one axis also has no
coordinate for sidebands (PLAN 2.4).

Refuses to run where C19 fails: at 2048 samples the slip windows hold < 0.4 native bins and the fault
channels land in the same bin as the shaft harmonics (PLAN 0.3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np

from kinematics import Kinematics, slip_window, S_MAX_DEFAULT

K_HARM, J_SIDE, M_SUB = 5, 2, 9
N_MIN = 20
CHANNELS = ("O", "I", "B", "C", "S")
DECIDING = {"L3": ("BPFO", "BPFI"), "L4": ("BPFO", "BPFI", "BPFB")}
FAMILY_OF_CLASS = {"outer_race": "BPFO", "inner_race": "BPFI", "ball": "BPFB"}


class FeasibilityError(RuntimeError):
    """Raised when the spectral resolution cannot support the family test (C19)."""


@dataclass
class HCResult:
    tensor: np.ndarray                         # (5, K, 2J+1, M)
    gate_bins: Dict[str, np.ndarray]           # deciding family -> native bin indices
    gate_bins_fundamental: Dict[str, np.ndarray] = field(default_factory=dict)   # A6 depth ablation
    df_hz: float = 0.0
    f_r: float = 0.0


def _channel_spec(k: Kinematics) -> Dict[str, Tuple[str, float, float]]:
    """channel -> (line used for slip window, anchor order, sideband spacing in orders)."""
    return {
        "O": ("BPFO", k.BPFO, 1.0),   # stationary outer race: sidebands physically absent; kept as contrast
        "I": ("BPFI", k.BPFI, 1.0),   # inner race rotates through the load zone -> +/- j*f_r
        "B": ("BPFB", k.BPFB, k.FTF),  # ball carried by the cage -> +/- j*FTF
        "C": ("FTF", k.FTF, k.FTF),    # context channel only; never decides (C22)
        "S": ("FTF", 1.0, 1.0),        # shaft harmonics (CS1 residual); symmetric +/- s_max windows
    }


def _window_hz(k: Kinematics, line: str, anchor_order: float, h: int, shift_order: float,
               f_r: float, s_max: float) -> Tuple[float, float]:
    if line in ("BPFO", "BPFI", "BPFB"):
        lo, hi = slip_window(k, line, s_max, harmonic=h)
    else:  # FTF-type or shaft: symmetric +/- s_max around h * anchor
        c = h * anchor_order
        lo, hi = (1 - s_max) * c, (1 + s_max) * c
    return (lo + shift_order) * f_r, (hi + shift_order) * f_r


def _check_ordering(k: Kinematics) -> None:
    if not k.ordering_ok():
        raise FeasibilityError(f"{k.bearing}: BPFO<BPFB<BPFI violated -- harmonic coordinates assume it")
    if abs(k.FTF - k.BPFO / k.n) > 1e-12:
        raise FeasibilityError(f"{k.bearing}: FTF != BPFO/n; inconsistent geometry")


def harmonic_coordinates(f: np.ndarray, S: np.ndarray, k: Kinematics, f_r: float, label_space: str = "L3",
                         s_max: float = S_MAX_DEFAULT, K: int = K_HARM, J: int = J_SIDE, M: int = M_SUB,
                         gate_sidebands: bool = True, floor: np.ndarray | None = None) -> HCResult:
    _check_ordering(k)
    df = float(f[1] - f[0])
    spec = _channel_spec(k)
    # normalised, log-compressed spectrum for the REPRESENTATION only
    if floor is None:
        from gate import noise_floor
        floor = noise_floor(S, f)
    z = np.log1p(S / floor)

    tensor = np.zeros((len(CHANNELS), K, 2 * J + 1, M), dtype=np.float32)
    for ci, ch in enumerate(CHANNELS):
        line, anchor, spacing = spec[ch]
        for h in range(1, K + 1):
            for jj, j in enumerate(range(-J, J + 1)):
                lo, hi = _window_hz(k, line, anchor, h, j * spacing, f_r, s_max)
                grid = np.linspace(lo, hi, M)
                tensor[ci, h - 1, jj] = np.interp(grid, f, z, left=0.0, right=0.0)
        med = np.median(tensor[ci])
        if med > 0:
            tensor[ci] /= med  # per-channel median scaling

    # GATE: native bins, snapped, per deciding family
    gate_bins, fundamental = {}, {}
    for fam in DECIDING[label_space]:
        ch = {"BPFO": "O", "BPFI": "I", "BPFB": "B"}[fam]
        line, anchor, spacing = spec[ch]
        use_side = gate_sidebands and fam in ("BPFI", "BPFB")
        idx: List[int] = []
        for h in range(1, K + 1):
            for j in (range(-J, J + 1) if use_side else [0]):
                lo, hi = _window_hz(k, line, anchor, h, j * spacing, f_r, s_max)
                idx.extend(np.nonzero((f >= lo) & (f <= hi))[0].tolist())
        gate_bins[fam] = np.unique(np.asarray(idx, dtype=int))
        lo, hi = _window_hz(k, line, anchor, 1, 0.0, f_r, s_max)
        fundamental[fam] = np.nonzero((f >= lo) & (f <= hi))[0]
        if gate_bins[fam].size < N_MIN:
            raise FeasibilityError(
                f"{fam}: {gate_bins[fam].size} native bins < {N_MIN} at df={df:.3f} Hz, f_r={f_r:.2f} Hz. "
                "Window too short for the family test (C19). At 2048 samples this is expected to fail."
            )
    return HCResult(tensor=tensor, gate_bins=gate_bins, gate_bins_fundamental=fundamental, df_hz=df, f_r=f_r)


def order_spectrum(f: np.ndarray, S: np.ndarray, f_r: float, max_order: float = 16.0,
                   n_points: int = 1024, floor: np.ndarray | None = None) -> np.ndarray:
    """Rung L3 representation: SES on a fixed SHAFT-ORDER axis (speed-normalised, geometry NOT normalised)."""
    if floor is None:
        from gate import noise_floor
        floor = noise_floor(S, f)
    orders = np.linspace(0.0, max_order, n_points)
    return np.interp(orders * f_r, f, np.log1p(S / floor), left=0.0, right=0.0).astype(np.float32)
