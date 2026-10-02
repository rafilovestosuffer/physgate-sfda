"""Single source of figure style for the manuscript (Elsevier artwork rules, verified 2026-09-20).

Widths are the Elsevier column widths in mm; figures are authored at printed size and never scaled in LaTeX, so a 7 pt
label in the file is 7 pt on the page. Colours are Okabe--Ito (colour-vision-deficiency safe) and every series is also
separated by position, shape or fill so that nothing depends on hue alone. save() writes the vector PDF that LaTeX uses,
a 600-dpi PNG preview, and the exact plotted values as CSV for the supplementary material.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PDF_DIR = ROOT / "paper" / "tex" / "figures"
PNG_DIR = ROOT / "paper" / "figures" / "preview"
CSV_DIR = ROOT / "paper" / "figures" / "data"

MM = 1 / 25.4
WIDTHS = {"single": 90 * MM, "onehalf": 140 * MM, "double": 190 * MM}   # inches
MAX_HEIGHT = 230 * MM

# Okabe--Ito, assigned once per experimental arm and never reused for anything else.
C = {
    "leaky": "#0F2B3D",        # near-black slate
    "clean": "#D55E00",        # vermillion
    "gated": "#E69F00",        # orange
    "oracle": "#009E73",       # bluish green
    "shallow": "#000000",      # black marker
    "comb": "#0072B2",         # blue
    "eagle": "#CC79A7",        # reddish purple
    "normal": "#56B4E9",       # sky blue
    "inner": "#009E73",
    "outer": "#E69F00",
    "grey": "#8A8A8A",
    "faint": "#D9D9D9",
}
LABEL = {"leaky": "leaky target", "clean": "bearing-disjoint target", "gated": "+ envelope gate",
         "oracle": "+ oracle filter", "shallow": "random forest (no adaptation)"}


def apply():
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 7.5,
        "axes.labelsize": 7.5,
        "axes.titlesize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.titlesize": 8,
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.6,
        "ytick.major.width": 0.6,
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "lines.linewidth": 1.0,
        "lines.markersize": 3.5,
        "legend.frameon": False,
        "legend.handlelength": 1.4,
        "legend.columnspacing": 1.0,
        "legend.handletextpad": 0.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "pdf.fonttype": 42,          # embed TrueType, no Type 3
        "ps.fonttype": 42,
        "savefig.bbox": "standard",  # keep the authored page size exactly
        "savefig.pad_inches": 0.0,
    })


def figure(width: str, height_mm: float):
    """A figure authored at its final printed size."""
    apply()
    h = height_mm * MM
    assert h <= MAX_HEIGHT, f"{height_mm} mm exceeds the page height budget"
    return plt.subplots(figsize=(WIDTHS[width], h), constrained_layout=True)


def grid(width: str, height_mm: float, nrows=1, ncols=1, **kw):
    apply()
    h = height_mm * MM
    assert h <= MAX_HEIGHT, f"{height_mm} mm exceeds the page height budget"
    return plt.subplots(nrows, ncols, figsize=(WIDTHS[width], h), constrained_layout=True, **kw)


def panel_tag(ax, tag: str, dx: float = -0.06, dy: float = 1.04):
    ax.text(dx, dy, tag, transform=ax.transAxes, fontsize=8, fontweight="bold", va="bottom", ha="left")


def save(fig, name: str, rows=None, header=None):
    """Write the vector PDF used by LaTeX, a 600-dpi preview, and the plotted values as CSV."""
    for d in (PDF_DIR, PNG_DIR, CSV_DIR):
        d.mkdir(parents=True, exist_ok=True)
    fig.savefig(PDF_DIR / f"{name}.pdf")
    fig.savefig(PNG_DIR / f"{name}.png", dpi=600)
    plt.close(fig)
    if rows is not None:
        with open(CSV_DIR / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            if header:
                w.writerow(header)
            w.writerows(rows)
    print(f"  {name}: pdf + png + {'csv' if rows is not None else 'no csv'}")
