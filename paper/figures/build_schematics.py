"""Fig. 1 (delegated to fig1_design.py) and the graphical abstract.

Run: python paper/figures/build_schematics.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import style as S  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402


def box(ax, x, y, w, h, text, face, edge=None, fontsize=7, weight="normal", tcol="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012",
                                linewidth=0.8, facecolor=face, edgecolor=edge or face, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color=tcol,
            zorder=3, fontweight=weight, linespacing=1.35)


def arrow(ax, p0, p1, color="#555555", style="-|>", lw=0.9, rad=0.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=7, lw=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", zorder=4))


def fig1_design():
    """Fig. 1 is built by fig1_design.py (design schematic with recomputed signal and gate insets)."""
    import fig1_design as F
    F.build()


def graphical_abstract():
    """1328 x 531 px at 300 dpi (Elsevier minimum), i.e. 4.427 x 1.770 in; must stay legible at 500 x 200."""
    S.apply()
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(4.427, 1.770), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.5, 0.97, "Does source-free bearing diagnosis survive unseen bearings?", ha="center", va="top",
            fontsize=10, fontweight="bold", color="#111111")
    import json
    import numpy as np
    root = HERE.parents[1]
    t = json.load(open(root / "results" / "c109" / "c109_intervals.json", encoding="utf-8"))
    c105 = json.load(open(root / "results" / "c105" / "c105_source_only.json", encoding="utf-8"))["sdalr_ten_splits"]["rows"]
    lk = np.median([r["adapted_leaky"] for r in c105])
    cl = np.median([r["adapted_clean"] for r in c105])
    sys.path.insert(0, str(root / "experiments"))
    import c88_eval as E
    R = E.load()
    gt = np.median([R[(s, s + "c", "pcv")].mean() for s in E.SPLITS])
    orc = np.median([R[(s, s + "c", "oracle")].mean() for s in E.SPLITS])
    drop = t["effects"]["sdalr_collapse_ten_splits"]["median"]
    bars = [(0.11, lk, S.C["leaky"], "same bearings"),
            (0.37, cl, S.C["clean"], "unseen bearings"),
            (0.63, gt, S.C["gated"], "+ physics gate"),
            (0.89, orc, S.C["oracle"], "oracle filter")]
    base, top = 0.28, 0.80
    for x, v, col, lab in bars:
        h = (v / 100) * (top - base)
        ax.add_patch(plt.Rectangle((x - 0.075, base), 0.15, h, color=col, zorder=2))
        ax.text(x, base + h + 0.018, f"{v:.0f}%", ha="center", fontsize=9.5, fontweight="bold", color=col)
        ax.text(x, base - 0.10, lab, ha="center", va="center", fontsize=8, color="#222222")
    ax.annotate("", xy=(0.285, 0.50), xytext=(0.195, 0.50),
                arrowprops=dict(arrowstyle="-|>", color="#B03A2E", lw=1.6))
    ax.text(0.24, 0.565, f"-{drop:.0f} pts", ha="center", fontsize=8.5, color="#B03A2E", fontweight="bold")
    ax.plot([0.02, 0.98], [base, base], color="#555555", lw=0.9)
    ax.text(0.5, 0.075, "SDALR on Paderborn, medians of ten pre-specified bearing-disjoint splits",
            ha="center", va="center", fontsize=7.5, color="#444444")
    S.save(fig, "graphical_abstract")


if __name__ == "__main__":
    fig1_design()
    graphical_abstract()
