"""Bearing kinematics: fault characteristic frequencies from geometry + measured shaft speed.

Contract (PLAN.md 0.1, 2.3; change log C13):
  * BSF and BPFB are DISTINCT quantities and are never conflated.
        BSF  = (Pd/2Bd)(1 - r^2)    true ball/roller spin frequency
        BPFB = 2 * BSF             ball DEFECT line -- what you search in an envelope spectrum
    "BSF" is used for both in the literature (CWRU's table tabulates 2x spin under that label;
    Smith & Randall report true spin). We therefore assert against the CLOSED FORM, never a table.
  * Unverified geometry RAISES. Silent numbers are the failure mode this module exists to prevent.
  * Slip windows follow from ONE pre-registered constant s_max via the cage-slip model.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import yaml

_CFG = Path(__file__).resolve().parents[1] / "configs" / "bearings.yaml"
S_MAX_DEFAULT = 0.02  # pre-registered cage-slip fraction. Do not tune. PLAN.md 2.3.


class UnverifiedBearingError(RuntimeError):
    """Raised when geometry has not been confirmed against a primary source."""


@dataclass(frozen=True)
class Kinematics:
    """Fault orders (multiples of shaft speed). Multiply by f_r [Hz] for frequencies."""
    bearing: str
    n: int
    r: float          # (Bd/Pd) cos(alpha)
    BPFO: float
    BPFI: float
    FTF: float
    BSF: float        # true spin
    BPFB: float       # 2 * BSF -- the searched defect line

    def at_rpm(self, rpm: float) -> Dict[str, float]:
        f_r = rpm / 60.0
        return {k: getattr(self, k) * f_r for k in ("BPFO", "BPFI", "FTF", "BSF", "BPFB")} | {"f_r": f_r}

    def ordering_ok(self) -> bool:
        """BPFO < BPFB < BPFI. Holds iff 2/(n+2) < r < 2/(n-2). Required by harmonic_coords."""
        return self.BPFO < self.BPFB < self.BPFI


def _load_cfg() -> dict:
    with open(_CFG, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def kinematics(bearing: str, cfg: dict | None = None) -> Kinematics:
    cfg = cfg or _load_cfg()
    entry = cfg["bearings"].get(str(bearing))
    if entry is None:
        raise KeyError(f"bearing {bearing!r} not in configs/bearings.yaml")
    if not entry.get("verified", False):
        raise UnverifiedBearingError(
            f"{bearing}: geometry is UNVERIFIED and must not be used. "
            f"blocked_on: {entry.get('blocked_on', 'unspecified')}. "
            "Obtain n, Bd and Pd from a manufacturer catalogue and record the source URL "
            "in configs/bearings.yaml before this bearing can be used."
        )

    n = int(entry["n"])
    # Units are whatever the primary source uses (CWRU: inches; Paderborn profiles: mm). Only the
    # ratio enters the kinematics, so we never convert -- converting is where rounding errors creep in.
    if "Bd_in" in entry:
        Bd, Pd = float(entry["Bd_in"]), float(entry["Pd_in"])
    else:
        Bd, Pd = float(entry["Bd_mm"]), float(entry["Pd_mm"])
    alpha = math.radians(float(entry.get("alpha_deg", cfg["defaults"]["alpha_deg"])))
    r = (Bd / Pd) * math.cos(alpha)

    bsf = (Pd / (2.0 * Bd)) * (1.0 - r * r)
    return Kinematics(
        bearing=str(bearing), n=n, r=r,
        BPFO=(n / 2.0) * (1.0 - r),
        BPFI=(n / 2.0) * (1.0 + r),
        FTF=0.5 * (1.0 - r),
        BSF=bsf,
        BPFB=2.0 * bsf,
    )


def slip_window(k: Kinematics, line: str, s_max: float = S_MAX_DEFAULT,
                harmonic: int = 1) -> Tuple[float, float]:
    """Slip tolerance window for `harmonic * line`, in ORDER units. PLAN.md 2.3.

    Cage slip reduces the actual cage frequency, f_c = (1-s) * FTF. Hence, exactly:
        BPFO = n * f_c        -> dBPFO/BPFO = -s          (geometry independent)
        BPFI = n * (f_r-f_c)  -> dBPFI/BPFI = +s*BPFO/BPFI (geometry DEPENDENT -- never hard-code)
    Both are ONE-SIDED: outer-race lines fall below theoretical, inner-race lines come out above.

    BSF/BPFB/FTF under slip are UNVERIFIED; a symmetric +/- s_max window is used and declared.
    """
    if harmonic < 1:
        raise ValueError("harmonic must be >= 1")
    if line == "BPFO":
        c = k.BPFO * harmonic
        return ((1.0 - s_max) * c, c)
    if line == "BPFI":
        c = k.BPFI * harmonic
        return (c, (1.0 + s_max * k.BPFO / k.BPFI) * c)
    if line in ("BPFB", "BSF", "FTF"):  # UNVERIFIED under slip -- symmetric, declared
        c = getattr(k, line) * harmonic
        return ((1.0 - s_max) * c, (1.0 + s_max) * c)
    raise ValueError(f"unknown line {line!r}")


def _main() -> None:
    p = argparse.ArgumentParser(description="Bearing fault orders from verified geometry.")
    p.add_argument("--bearing", required=True)
    p.add_argument("--rpm", type=float, default=None)
    p.add_argument("--s-max", type=float, default=S_MAX_DEFAULT)
    a = p.parse_args()

    k = kinematics(a.bearing)
    print(f"{k.bearing}: n={k.n}  r={k.r:.6f}  (BPFO<BPFB<BPFI: {k.ordering_ok()})")
    print(f"{'line':6s} {'order':>10s} {'slip window (order)':>28s}" + ("" if a.rpm is None else f" {'Hz':>10s}"))
    for line in ("FTF", "BPFO", "BPFB", "BPFI"):
        lo, hi = slip_window(k, line, a.s_max)
        row = f"{line:6s} {getattr(k, line):10.4f} {f'[{lo:.4f}, {hi:.4f}]':>28s}"
        if a.rpm is not None:
            row += f" {getattr(k, line) * a.rpm / 60.0:10.3f}"
        print(row)
    print(f"{'BSF':6s} {k.BSF:10.4f}   (true spin; BPFB = 2*BSF is the searched defect line)")


if __name__ == "__main__":
    _main()
