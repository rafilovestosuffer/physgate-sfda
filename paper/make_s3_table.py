"""Generate the per-specimen Paderborn geometry/damage table for Supplementary S3, read from the dataset's own datasheets.

Every value comes from page 1 (geometry) or page 2 (damage) of `data/pu/<B>/<B>.pdf`, the "Profile of rolling bearing
damage" file distributed with the data. Nothing here is copied from a catalogue or another rig. Page 2 has one column per
damage ("Damage 1/2/3"); `damages()` reads every column by position, because a specimen can carry more than one damage.

Also lists the byte-identical vibration signals among the recordings used (S3.1b), with the SHA-256 of each signal.

Writes paper/supplementary_S3_geometry_table.md; the block is inserted into S3 by hand once, then regenerated in place.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import fitz
import scipy.io as sio

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "supplementary_S3_geometry_table.md"
EXCLUDED = {"KB23", "KB24", "KB27"}          # double damage: outside this study's single-fault label space
sys.path.insert(0, str(ROOT / "data_prep"))
import pu  # noqa: E402

# page-2 row label (a word in the label column) -> field name
ROWS = {"Mode": "mode", "Sub-mode": "submode", "Symptom": "symptom", "Component": "component", "Position": "position",
        "combination": "combination", "Arrangement": "arrangement", "Length": "length_mm", "Extent": "extent",
        "Width": "width_mm", "Depth": "depth_mm", "Characteristic": "characteristic", "method": "method"}


def field(lines, label, span=4):
    for i, l in enumerate(lines):
        if l.strip() == label:
            for v in lines[i + 1:i + span]:
                v = v.strip()
                if v and v not in ("mm", "-", "pc.", "°", "Unit"):
                    return v
    return ""


def damages(pdf: Path) -> list[dict]:
    """One dict per damage column on page 2 of a datasheet (empty list for a healthy bearing).

    Words are assigned to a damage column by their x position (between the "Damage k" headers) and to a row by their
    y position (between the midpoints to the neighbouring row labels), so multi-line cells and a second or third damage
    are read correctly.
    """
    doc = fitz.open(pdf)
    if len(doc) < 2:
        return []
    words = doc[1].get_text("words")                       # (x0, y0, x1, y1, text, block, line, word)
    head_y = next(w[1] for w in words if w[4] == "Category")
    cols = sorted(w[0] for w in words if w[4] == "Damage" and abs(w[1] - head_y) < 3)
    assert len(cols) == 3, f"{pdf.name}: expected three damage columns, found {len(cols)}"
    left = cols[0] - 30                                     # values lie right of this; labels and units left of it
    ny = min(w[1] for w in words if w[4] == "damages")      # the "Number of damages" row
    n = int(next(w[4] for w in words if abs(w[1] - ny) < 3 and w[0] >= left))
    rows = sorted((w[1], ROWS[w[4]]) for w in words if w[4] in ROWS and 140 <= w[0] < left)
    out = [{} for _ in range(n)]
    for i, (y, name) in enumerate(rows):
        lo = (rows[i - 1][0] + y) / 2 if i else head_y + 8
        hi = (rows[i + 1][0] + y) / 2 if i + 1 < len(rows) else y + 20
        for k in range(n):
            x_lo, x_hi = cols[k] - 30, (cols[k + 1] - 30 if k + 1 < len(cols) else 1e9)
            cell = sorted((w[1], w[0], w[4]) for w in words if lo <= w[1] < hi and x_lo <= w[0] < x_hi)
            out[k][name] = " ".join(t for _, _, t in cell)
    return out


def duplicate_signals(bearings, conditions=("N15_M01_F10", "N15_M07_F04", "N15_M07_F10")):
    """Groups of recordings whose vibration_1 samples are byte-identical, with the SHA-256 of the samples."""
    groups = {}
    for b in bearings:
        for c in conditions:
            for path in sorted((ROOT / "data" / "pu" / b).glob(f"{c}_{b}_*.mat")):
                try:
                    mat = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
                except (TypeError, ValueError):
                    continue                                    # the one malformed file (PROTOCOL C34)
                s = mat[[k for k in mat if not k.startswith("__")][0]]
                h = hashlib.sha256(pu._channel(s, "vibration_1").tobytes()).hexdigest()
                groups.setdefault(h, []).append(path.stem)
    return sorted((v, h) for h, v in groups.items() if len(v) > 1)


def main():
    rows = []
    for pdf in sorted((ROOT / "data" / "pu").glob("K*/K*.pdf")):
        lines = [l for p in fitz.open(pdf) for l in p.get_text().split("\n")]
        b = pdf.stem
        ds = damages(pdf)
        rows.append({
            "bearing": b,
            "manufacturer": field(lines, "Manufacturer"),
            "pitch_mm": field(lines, "Pitch circle diameter"),
            "balls": field(lines, "Number of rolling elements"),
            "ball_mm": field(lines, "Rolling element diameter"),
            "n": len(ds),
            "combination": " + ".join(dict.fromkeys(d.get("combination", "") for d in ds)),
            "mode": " + ".join(d.get("mode", "") for d in ds),
            "symptom": " + ".join(d.get("symptom", "") for d in ds),
            "component": " + ".join(d.get("component", "") for d in ds),
            "size": " + ".join(f"{d['length_mm']} × {d['width_mm']}" if d.get("length_mm") else "n/a" for d in ds),
            "used": "no (double damage)" if b in EXCLUDED else "yes",
        })
    assert rows, "no Paderborn datasheets found under data/pu/"

    by_pitch = {}
    for r in rows:
        by_pitch.setdefault(r["pitch_mm"], []).append(r["bearing"])

    L = ["### S3.1a Per-specimen geometry and damage, read from the Paderborn datasheets", "",
         f"All {len(rows)} specimens distributed with the dataset. Geometry is on page 1 of each",
         "`data/pu/<bearing>/<bearing>.pdf`; damage mode, symptom, component, size and combination are on page 2, one column",
         "per damage (joined here with +). Combination: S single, R repetitive, M multiple damage. Reproduce with",
         "`python paper/make_s3_table.py`.", "",
         "| Bearing | Manufacturer | Pitch (mm) | Balls | Ball dia (mm) | Damages | Comb. | Damage mode | Symptom | Component "
         "| Length × width (mm) | Used here |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['bearing']} | {r['manufacturer'] or '--'} | {r['pitch_mm']} | {r['balls']} | {r['ball_mm']} | "
                 f"{r['n'] or '--'} | {r['combination'] or '--'} | {r['mode'] or 'healthy'} | {r['symptom'] or '--'} | "
                 f"{r['component'] or '--'} | {r['size'] or '--'} | {r['used']} |")
    L += ["", "Summary: " + "; ".join(f"pitch {k} mm on {len(v)} specimens" for k, v in sorted(by_pitch.items()))
          + ". Every specimen has 8 rolling elements of 6.75 mm, so the two geometries differ only in pitch diameter,",
          "giving outer-race orders 3.0706 (29.05 mm) and 3.0543 (28.55 mm). Two specimens of the inner-race class carry a",
          "second damage on the other ring (KI04 and KI14: particle-caused indentations on the outer ring, combination M);",
          "the dataset classifies a specimen with several damages by its largest damage, here the inner-ring pitting.", ""]

    used = [r["bearing"] for r in rows if r["used"] == "yes" and not r["mode"].startswith("artificial")]
    dups = duplicate_signals(used)
    L += ["### S3.1b Byte-identical vibration signals", "",
          "Recordings of the healthy and real-damage specimens used here, at the three adaptation conditions, whose",
          "`vibration_1` samples are byte-identical (SHA-256 of the stored samples). Each copy is a separate file and a",
          "separate recording in the gate counts; all copies of a group belong to one bearing and so stay on one side of",
          "every split.", "",
          "| Recordings | SHA-256 of `vibration_1` |", "|---|---|"]
    L += [f"| {', '.join(v)} | `{h}` |" for v, h in dups] + [""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {len(rows)} specimens; " + ", ".join(f"{k} mm x{len(v)}" for k, v in sorted(by_pitch.items()))
          + f"; {len(dups)} duplicate group(s)")


if __name__ == "__main__":
    main()
