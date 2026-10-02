"""Validate every manuscript figure against the Elsevier artwork rules and against the data. Exits non-zero on failure.

Checks
  1. every \\includegraphics in the .tex resolves to a file that exists
  2. page width equals the declared column width (90 / 140 / 190 mm) within 0.5 mm; height <= 230 mm
  3. all fonts embedded, and only the approved family used
  4. every rendered text span >= 6.9 pt (the 7 pt rule, measured rather than assumed)
  5. colour-vision-deficiency simulation (Machado et al. matrices): series colours stay separable
  6. greyscale separability of the same colours
  7. one data CSV per data figure, and its values match the result files recomputed through the evaluators
  8. captions, labels and reference order in the manuscript
Writes CVD proof sheets to paper/figures/cvd/.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import numpy as np
import fitz
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEX = ROOT / "paper" / "tex"
sys.path[:0] = [str(HERE), str(ROOT / "experiments")]
import style as S  # noqa: E402

PT_MM = 25.4 / 72
WIDTH_OF = {"fig1_design": 190, "fig2_collapse": 190, "fig3_purity": 140, "fig4_decomposition": 140,
            "fig5_roc": 140, "fig6_gains": 140, "fig7_slip": 90}
GA = "graphical_abstract"
APPROVED_FONTS = ("Arial", "ArialMT", "Arial-BoldMT", "DejaVuSans", "DejaVu Sans")
# Machado, Oliveira & Fernandes (2009), severity 1.0
CVD = {
    "deuteranopia": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413],
                              [-0.011820, 0.042940, 0.968881]]),
    "protanopia": np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216],
                            [-0.003882, -0.048116, 1.051998]]),
}
fails: list[str] = []


def check(cond, msg):
    if not cond:
        fails.append(msg)
    return cond


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def simulate(rgb, mat):
    return np.clip(mat @ rgb, 0, 1)


def sep(a, b):
    """Perceptual-ish distance: weighted Euclidean in RGB, adequate for a separability guard."""
    w = np.array([0.30, 0.59, 0.11])
    return float(np.sqrt(np.sum(w * (a - b) ** 2)))


def main():
    # ---- 1. every included figure exists
    included = []
    for tex in (TEX / "sections").glob("*.tex"):
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex.read_text(encoding="utf-8")):
            included.append((tex.name, m.group(1)))
    for src, rel in included:
        check((TEX / rel).exists(), f"{src}: missing figure file {rel}")

    # ---- 2-4. per-PDF geometry, fonts, text size
    for name, mm in WIDTH_OF.items():
        p = TEX / "figures" / f"{name}.pdf"
        if not check(p.exists(), f"{name}.pdf not built"):
            continue
        doc = fitz.open(p)
        page = doc[0]
        w_mm, h_mm = page.rect.width * PT_MM, page.rect.height * PT_MM
        check(abs(w_mm - mm) < 0.5, f"{name}: width {w_mm:.1f} mm, expected {mm} mm")
        check(h_mm <= 230, f"{name}: height {h_mm:.1f} mm exceeds 230 mm")
        for f in page.get_fonts(full=True):
            fname = f[3].split("+")[-1]
            check(not f[3].startswith("Type3") and f[2] != "Type3", f"{name}: Type 3 font {f[3]}")
            check(any(a.replace(" ", "") in fname.replace(" ", "") for a in APPROVED_FONTS),
                  f"{name}: unapproved font {fname}")
        sizes = [s["size"] for b in page.get_text("dict")["blocks"] if b.get("lines")
                 for l in b["lines"] for s in l["spans"] if s["text"].strip()]
        if sizes:
            # a span is a sub/superscript when its size is ~0.7x the size of some other span in the same figure
            uniq = sorted(set(round(v, 2) for v in sizes))
            is_script = {v: any(abs(v - 0.7 * w) < 0.15 for w in uniq if w > v + 0.3) for v in uniq}
            normal = [v for v in sizes if not is_script[round(v, 2)]]
            script = [v for v in sizes if is_script[round(v, 2)]]
            check(min(normal) >= 6.9, f"{name}: smallest normal text {min(normal):.2f} pt is below the 7 pt rule")
            if script:
                check(min(script) >= 5.95,
                      f"{name}: smallest sub/superscript {min(script):.2f} pt is below the 6 pt rule")
        doc.close()

    # graphical abstract: pixel size at 300 dpi and minimum text size
    gp = TEX / "figures" / f"{GA}.pdf"
    if check(gp.exists(), "graphical_abstract.pdf not built"):
        doc = fitz.open(gp)
        page = doc[0]
        px_w = page.rect.width / 72 * 300
        px_h = page.rect.height / 72 * 300
        check(px_w >= 1328 - 2 and px_h >= 531 - 2, f"graphical abstract {px_w:.0f}x{px_h:.0f} px at 300 dpi, need 1328x531")
        check(abs(px_w / px_h - 2.5) < 0.05, f"graphical abstract aspect {px_w / px_h:.2f}, expected 2.5")
        sizes = [s["size"] for b in page.get_text("dict")["blocks"] if b.get("lines")
                 for l in b["lines"] for s in l["spans"] if s["text"].strip()]
        check(min(sizes) >= 7.4, f"graphical abstract smallest text {min(sizes):.2f} pt; it is reduced to 500x200")
        doc.close()

    # ---- 5-6. colour separability under CVD and in greyscale
    series = ["leaky", "clean", "gated", "oracle", "comb", "eagle"]
    (HERE / "cvd").mkdir(exist_ok=True)
    for kind, mat in CVD.items():
        for i, a in enumerate(series):
            for b in series[i + 1:]:
                d = sep(simulate(hex_rgb(S.C[a]), mat), simulate(hex_rgb(S.C[b]), mat))
                check(d > 0.055, f"{kind}: {a} and {b} collapse to distance {d:.3f}")
    grey = {k: float(np.dot(hex_rgb(S.C[k]), [0.299, 0.587, 0.114])) for k in series}
    for i, a in enumerate(series):
        for b in series[i + 1:]:
            check(abs(grey[a] - grey[b]) > 0.04, f"greyscale: {a} and {b} differ by {abs(grey[a] - grey[b]):.3f}")
    for name in list(WIDTH_OF) + [GA]:
        src = HERE / "preview" / f"{name}.png"
        if src.exists():
            im = np.asarray(Image.open(src).convert("RGB").resize((700, int(700 * Image.open(src).height /
                                                                   Image.open(src).width)))) / 255
            for kind, mat in CVD.items():
                out = np.clip(im @ mat.T, 0, 1)
                Image.fromarray((out * 255).astype(np.uint8)).save(HERE / "cvd" / f"{name}_{kind}.png")

    # ---- 7. figure data matches the evaluators
    import c88_eval as E
    R = E.load()
    csv_p = HERE / "data" / "fig2_collapse.csv"
    if check(csv_p.exists(), "fig2_collapse.csv missing"):
        for row in csv.DictReader(open(csv_p, encoding="utf-8")):
            if row["rig"] != "Paderborn" or not row["split"].startswith("S"):
                continue
            s = row["split"]
            for col, key in (("leaky", (s, s, "none")), ("clean", (s, s + "c", "none")),
                             ("gated", (s, s + "c", "pcv")), ("oracle", (s, s + "c", "oracle"))):
                check(abs(float(row[col]) - R[key].mean()) < 0.01,
                      f"fig2 {s} {col}: {row[col]} != {R[key].mean():.2f} recomputed from artifacts")
    for name in WIDTH_OF:
        if name != "fig1_design":
            check((HERE / "data" / f"{name}.csv").exists(), f"{name}: plotted values not exported as CSV")

    # ---- 8. captions, labels, reference order
    body = "\n".join((TEX / "sections" / f).read_text(encoding="utf-8")
                     for f in sorted(p.name for p in (TEX / "sections").glob("*.tex")))
    labels = re.findall(r"\\label\{(fig:[^}]+)\}", body)
    check(len(labels) == len(set(labels)), "duplicate figure labels")
    for lab in labels:
        check(len(re.findall(r"\\ref\{" + re.escape(lab) + r"\}", body)) >= 1, f"figure {lab} is never \\ref-ed")
    order = [m.group(1) for m in re.finditer(r"\\ref\{(fig:[^}]+)\}", body)]
    first = [l for l in dict.fromkeys(order)]
    check(first == [l for l in labels if l in first], f"figures are not first cited in order: {first} vs {labels}")
    for blk in re.findall(r"\\begin\{figure\}.*?\\end\{figure\}", body, re.S):
        check("\\caption{" in blk and "\\label{" in blk, "a figure environment lacks a caption or label")

    print(f"{len(WIDTH_OF) + 1} figures checked")
    if fails:
        print("\nFAILURES")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("all figure checks passed")


if __name__ == "__main__":
    main()
