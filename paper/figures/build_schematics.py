"""Fig. 1 (paired design schematic) and the graphical abstract. Both are drawn, not data-plotted.

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
    fig, ax = S.figure("double", 68)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")

    box(ax, 0.01, 0.62, 0.20, 0.20, "source bearings\n3 healthy, 3 inner, 3 outer\n(fold B: 2 outer)\nat the source condition", S.C["leaky"])
    box(ax, 0.28, 0.62, 0.17, 0.20, "source model\n(trained once)", S.C["grey"])
    arrow(ax, (0.215, 0.72), (0.275, 0.72))

    # two adaptation arms
    box(ax, 0.56, 0.78, 0.23, 0.17, "adapt to the SAME bearings\nat the target condition", S.C["leaky"])
    box(ax, 0.56, 0.50, 0.23, 0.17, "adapt to the OTHER bearings\nat the target condition", S.C["clean"])
    arrow(ax, (0.455, 0.75), (0.555, 0.865), rad=0.18)
    arrow(ax, (0.455, 0.69), (0.555, 0.585), rad=-0.18)
    box(ax, 0.83, 0.78, 0.16, 0.17, "leaky\naccuracy", S.C["leaky"])
    box(ax, 0.83, 0.50, 0.16, 0.17, "bearing-disjoint\naccuracy", S.C["clean"], fontsize=7.0)
    arrow(ax, (0.795, 0.865), (0.825, 0.865))
    arrow(ax, (0.795, 0.585), (0.825, 0.585))
    ax.annotate("", xy=(0.91, 0.775), xytext=(0.91, 0.675),
                arrowprops=dict(arrowstyle="<->", color="#444444", lw=0.9))
    ax.text(0.935, 0.725, "leaky minus" + chr(10) + "bearing-disjoint", fontsize=7.0, va="center", color="#222222")

    # gated / oracle arms from the same checkpoint
    box(ax, 0.28, 0.20, 0.17, 0.13, "same source\ncheckpoint", S.C["grey"], fontsize=7.0)
    arrow(ax, (0.365, 0.615), (0.365, 0.335))
    box(ax, 0.56, 0.26, 0.23, 0.13, "+ physics gate on pseudo-labels", S.C["gated"], fontsize=7.0)
    box(ax, 0.56, 0.06, 0.23, 0.13, "+ oracle filter (reference)", S.C["oracle"], fontsize=7.0)
    arrow(ax, (0.455, 0.29), (0.555, 0.325), rad=0.1)
    arrow(ax, (0.455, 0.25), (0.555, 0.125), rad=-0.12)
    box(ax, 0.83, 0.06, 0.16, 0.33, "same tasks,\nsame job,\npaired\ndifferences", "#FFFFFF", edge="#999999",
        fontsize=7.0, tcol="#222222")
    arrow(ax, (0.795, 0.325), (0.825, 0.30))
    arrow(ax, (0.795, 0.125), (0.825, 0.16))

    note = ("Held fixed: condition pair, windows," + chr(10) + "class balance, optimiser, seed." + chr(10) +
            "The two targets differ in bearing" + chr(10) + "overlap and in which bearings they hold.")
    ax.text(0.01, 0.30, note, fontsize=7.0, va="top", color="#333333", linespacing=1.6)
    S.save(fig, "fig1_design")


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
    ax.text(0.5, 0.075, "SDALR on Paderborn, medians of ten pre-registered bearing-disjoint splits",
            ha="center", va="center", fontsize=7.5, color="#444444")
    S.save(fig, "graphical_abstract")


if __name__ == "__main__":
    fig1_design()
    graphical_abstract()
