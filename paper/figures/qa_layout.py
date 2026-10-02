"""Layout quality assurance: find text that collides with other text, with data marks, or with the axes frame.

Works on the rendered PDF, so it sees exactly what a reader sees. For every text span it compares the span's box with
  (a) every other text span,
  (b) every vector drawing that is a data mark (a stroked path or a dark fill), ignoring page-sized backgrounds and very
      light fills such as shaded bands, which text is allowed to sit on,
  (c) the page edges (clipping).
Run: python paper/figures/qa_layout.py [name ...]
"""
from __future__ import annotations

import sys
from pathlib import Path

import fitz

HERE = Path(__file__).resolve().parent
TEX = HERE.parents[1] / "paper" / "tex" / "figures"
PAD = 0.4          # pt of slack: touching is not overlapping
MIN_AREA = 0.8     # pt^2 of intersection before we call it a collision


def area(r):
    return max(0.0, r.width) * max(0.0, r.height)


def luminance(c):
    if c is None:
        return 1.0
    r, g, b = (c + (0, 0, 0))[:3] if isinstance(c, tuple) else (0, 0, 0)
    return 0.299 * r + 0.587 * g + 0.114 * b


def inspect(pdf: Path):
    doc = fitz.open(pdf)
    page = doc[0]
    spans = [(s["text"].strip(), fitz.Rect(s["bbox"]))
             for b in page.get_text("dict")["blocks"] if b.get("lines")
             for l in b["lines"] for s in l["spans"] if s["text"].strip()]
    page_area = area(page.rect)
    marks = []
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"])
        # dashes and hairlines come through as degenerate rectangles; give them their real visual thickness
        if r.width < 0.8:
            r = fitz.Rect(r.x0 - 0.5, r.y0, r.x1 + 0.5, r.y1)
        if r.height < 0.8:
            r = fitz.Rect(r.x0, r.y0 - 0.5, r.x1, r.y1 + 0.5)
        if area(r) > 0.45 * page_area:               # background or panel fill
            continue
        if not page.rect.intersects(r) or r.y0 < -0.5 or r.x0 < -0.5:
            continue                                  # hatch/pattern tile, not drawn content
        stroked = d.get("color") is not None and d.get("width", 0) and d.get("width") > 0.2
        dark_fill = d.get("fill") is not None and luminance(d.get("fill")) < 0.80
        if stroked or dark_fill:
            marks.append((r, "stroke" if stroked else "fill"))

    issues = []
    for i, (t1, r1) in enumerate(spans):
        a = fitz.Rect(r1.x0 + PAD, r1.y0 + PAD, r1.x1 - PAD, r1.y1 - PAD)
        for t2, r2 in spans[i + 1:]:
            b = fitz.Rect(r2.x0 + PAD, r2.y0 + PAD, r2.x1 - PAD, r2.y1 - PAD)
            if area(a & b) > MIN_AREA:
                issues.append(f"text/text  {t1!r} over {t2!r}")
        for r2, kind in marks:
            if area(a & r2) > MIN_AREA and not r2.contains(a):     # a box drawn *around* the label is fine
                thin = min(r2.width, r2.height) < 3.0              # a rule, a line or a dashed guide
                frac = area(a & r2) / max(area(a), 1e-6)
                if (thin and area(a & r2) > 1.5) or frac > 0.12:
                    issues.append(f"text/{kind:6s} {t1!r} over a mark at {tuple(round(v, 1) for v in r2)}")
        if not page.rect.contains(fitz.Rect(r1.x0 - 0.5, r1.y0 - 0.5, r1.x1 + 0.5, r1.y1 + 0.5)):
            issues.append(f"clipped    {t1!r} runs past the page edge")
    doc.close()
    # collapse duplicates (a label crossing several segments of one line)
    seen, out = set(), []
    for msg in issues:
        key = msg.split(" over ")[0]
        if key not in seen:
            seen.add(key)
            out.append(msg)
    return out


def main():
    names = sys.argv[1:] or sorted(p.stem for p in TEX.glob("*.pdf"))
    total = 0
    for n in names:
        found = inspect(TEX / f"{n}.pdf")
        total += len(found)
        print(f"\n{n}: {len(found) or 'clean'}")
        for f in found:
            print("   ", f)
    print(f"\n{total} layout issues")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
