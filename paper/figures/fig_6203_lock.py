"""Figure 1 -- the 6203 shaft-harmonic lock (PLAN 0.2), on real data.

Panels (squared envelope spectrum, log scale):
  (a) PU KA04 (6203, real outer-race damage), N15_M01_F10, NO pre-whitening
  (b) same record, cepstrum pre-whitened
  (c) CWRU 130 (6205, outer race), cepstrum pre-whitened -- the lock-free contrast
Overlays: theoretical fault lines (solid) with slip windows (shaded), shaft harmonics k*f_r (dotted).
Descriptive figure; no hypothesis is tested here.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep")]
import band_select, cwru, prewhiten, pu, ses  # noqa: E402,E401
from kinematics import kinematics, slip_window  # noqa: E402

LINE_COL = {"BPFO": "#c0392b", "BPFI": "#2471a3", "BPFB": "#7d3c98"}


def panel(ax, f, S, k, f_r, title, fmax=420.0, lines=("BPFO", "BPFI", "BPFB")):
    m = (f > 2) & (f < fmax)
    floor = np.median(S[m])
    ax.semilogy(f[m], S[m] / floor, color="0.25", lw=0.6)
    top = (S[m] / floor).max() * 1.5
    for h in range(1, int(fmax / f_r) + 1):
        ax.axvline(h * f_r, color="0.55", ls=":", lw=0.8, zorder=0)
    for L in lines:
        for h in range(1, 6):
            c = getattr(k, L) * h * f_r
            if c > fmax:
                break
            lo, hi = slip_window(k, L, 0.02, harmonic=h)
            ax.axvspan(lo * f_r, hi * f_r, color=LINE_COL[L], alpha=0.12, lw=0)
            ax.axvline(c, color=LINE_COL[L], lw=0.9, alpha=0.9)
    ax.set_xlim(0, fmax)
    ax.set_ylim(0.3, top)
    ax.set_title(title, fontsize=9, loc="left")
    ax.set_ylabel("SES / median")


def main():
    k5 = kinematics("6205")
    r = pu.read_one(pu.files(bearings=["KA04"], conditions=["N15_M01_F10"])[0])
    x = r.signal[: int(4.0 * r.fs_hz)]
    fr_pu = r.rpm / 60.0
    k3 = kinematics(r.bearing_model)   # C35: KA04 is FAG, Pd 28.55 mm

    fig, axes = plt.subplots(3, 1, figsize=(7.2, 7.8), constrained_layout=True)
    for ax, arm, lab in ((axes[0], "none", "(a) Paderborn KA04, 6203, raw"),
                         (axes[1], "cepstrum", "(b) Paderborn KA04, 6203, cepstrum pre-whitened")):
        y = prewhiten.prewhiten(x, arm)
        b = band_select.select_band(y, r.fs_hz, max_fault_hz=(5 * k3.BPFI + 2) * fr_pu, f_hi=15000.0)  # C33
        f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(b.lo_hz, b.hi_hz))
        panel(ax, f, S, k3, fr_pu, f"{lab}  |  f_r = {fr_pu:.2f} Hz, band {b.lo_hz/1e3:.0f}-{b.hi_hz/1e3:.0f} kHz",
              lines=("BPFO", "BPFI"))

    c = {rec.record_id: rec for rec in cwru.load()}["130"]
    xc = c.signal[: int(5.0 * c.fs_hz)]
    fr_c = c.rpm / 60.0
    yc = prewhiten.cepstrum_prewhiten(xc)
    bc = band_select.select_band(yc, c.fs_hz, max_fault_hz=(5 * k5.BPFI + 2) * fr_c)
    fc, Sc = ses.squared_envelope_spectrum(yc, c.fs_hz, band=(bc.lo_hz, bc.hi_hz))
    panel(axes[2], fc, Sc, k5, fr_c, f"(c) CWRU 130, 6205, cepstrum pre-whitened  |  f_r = {fr_c:.2f} Hz",
          lines=("BPFO", "BPFI"))
    axes[2].set_xlabel("envelope frequency (Hz)")

    handles = [plt.Line2D([], [], color=LINE_COL["BPFO"], label="BPFO + slip window"),
               plt.Line2D([], [], color=LINE_COL["BPFI"], label="BPFI + slip window"),
               plt.Line2D([], [], color="0.55", ls=":", label="shaft harmonics k·f_r")]
    axes[0].legend(handles=handles, fontsize=7, loc="upper right", framealpha=0.9)
    out = ROOT / "paper" / "figures"
    for ext in ("png", "pdf"):
        fig.savefig(out / f"fig1_6203_lock.{ext}", dpi=200)
    print("saved", out / "fig1_6203_lock.png")


if __name__ == "__main__":
    main()
