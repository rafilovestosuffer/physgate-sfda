"""Generate the per-specimen Paderborn geometry/damage table for Supplementary S3, read from the dataset's own datasheets.

Every value comes from page 1 (geometry) or page 2 (damage) of `data/pu/<B>/<B>.pdf`, the "Profile of rolling bearing
damage" file distributed with the data. Nothing here is copied from a catalogue or another rig.

Writes paper/supplementary_S3_geometry_table.md; the block is inserted into S3 by hand once, then regenerated in place.
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "supplementary_S3_geometry_table.md"
EXCLUDED = {"KB23", "KB24", "KB27"}          # double damage: outside this study's single-fault label space


def field(lines, label, span=4):
    for i, l in enumerate(lines):
        if l.strip() == label:
            for v in lines[i + 1:i + span]:
                v = v.strip()
                if v and v not in ("mm", "-", "pc.", "°", "Unit"):
                    return v
    return ""


def main():
    rows = []
    for pdf in sorted((ROOT / "data" / "pu").glob("K*/K*.pdf")):
        lines = [l for p in fitz.open(pdf) for l in p.get_text().split("\n")]
        b = pdf.stem
        rows.append({
            "bearing": b,
            "manufacturer": field(lines, "Manufacturer"),
            "pitch_mm": field(lines, "Pitch circle diameter"),
            "balls": field(lines, "Number of rolling elements"),
            "ball_mm": field(lines, "Rolling element diameter"),
            "mode": field(lines, "Mode"),
            "symptom": field(lines, "Symptom"),
            "component": field(lines, "Component"),
            "method": re.sub(r"\s+", " ", field(lines, "Damage method")),
            "used": "no (double damage)" if b in EXCLUDED else "yes",
        })
    assert rows, "no Paderborn datasheets found under data/pu/"

    by_pitch = {}
    for r in rows:
        by_pitch.setdefault(r["pitch_mm"], []).append(r["bearing"])

    L = ["### S3.1a Per-specimen geometry and damage, read from the Paderborn datasheets", "",
         f"All {len(rows)} specimens distributed with the dataset. Geometry is on page 1 of each",
         "`data/pu/<bearing>/<bearing>.pdf`; damage mode and symptom are on page 2. Reproduce with",
         "`python paper/make_s3_table.py`.", "",
         "| Bearing | Manufacturer | Pitch (mm) | Balls | Ball dia (mm) | Damage mode | Symptom | Component | Used here |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['bearing']} | {r['manufacturer'] or '--'} | {r['pitch_mm']} | {r['balls']} | {r['ball_mm']} | "
                 f"{r['mode'] or 'healthy'} | {r['symptom'] or '--'} | {r['component'] or '--'} | {r['used']} |")
    L += ["", "Summary: " + "; ".join(f"pitch {k} mm on {len(v)} specimens" for k, v in sorted(by_pitch.items()))
          + ". Every specimen has 8 rolling elements of 6.75 mm, so the two geometries differ only in pitch diameter,",
          "giving outer-race orders 3.0706 (29.05 mm) and 3.0543 (28.55 mm).", ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {len(rows)} specimens; " + ", ".join(f"{k} mm x{len(v)}" for k, v in sorted(by_pitch.items())))


if __name__ == "__main__":
    main()
