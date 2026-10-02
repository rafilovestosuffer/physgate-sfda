"""UORED-VAFCLS loader (Sehri, Dumond & Bouchard, Data in Brief 49:109327, 2023; Mendeley y2px5tg92h v5, CC BY 4.0).

VERIFIED on the files (2026-09-13):
  * 60 CSVs `{H,I,O,B,C}_{bearing}_{state}.csv`, header Accelerometer,Acoustic,Speed,Load,Temperature Difference,
    420,000 rows = 10 s at 42 kHz. Vibration = column 0 only (C42).
  * Speed is logged ONCE per file (row 0; zeros elsewhere): 1709-1819 rpm, not the nominal 1750 -> per-file.
  * Bearing numbering by fault type: H 1-20 (state 0 of every bearing), I 1-5, O 6-10, B 11-15, C 16-20.
    Bearings 1-5 are NSK 6203ZZ, 6-20 FAFNIR 203KD (article Sec. 3) -> the inner-race class is entirely NSK.
    Geometry is identical (C54), but manufacturer is confounded with the inner class; recorded in meta.
  * State 0 of bearing b and states 1-2 of bearing b are the SAME physical bearing (bearing_id = b).
    Vieira et al. footnote 2: across labels this is not leakage; splitting by severity within a label IS (C36b).
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

from records import Record

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "uored" / "raw"
CACHE = ROOT / "data" / "uored" / "npy"
FS = 42000.0
NAME_RE = re.compile(r"^([HIOBC])_(\d+)_([012])$")
FAULT = {"H": "normal", "I": "inner_race", "O": "outer_race", "B": "ball", "C": "cage"}
STATE = {0: "healthy", 1: "developing", 2: "faulty"}
BEARING_RANGE = {"I": range(1, 6), "O": range(6, 11), "B": range(11, 16), "C": range(16, 21), "H": range(1, 21)}


def _read(path: Path) -> tuple[np.ndarray, float, float]:
    CACHE.mkdir(parents=True, exist_ok=True)
    c = CACHE / (path.stem + ".npz")
    if c.exists():
        z = np.load(c)
        return z["x"], float(z["rpm"]), float(z["load"])
    d = np.loadtxt(path, delimiter=",", skiprows=1, encoding="utf-8-sig")
    if d.shape != (420000, 5):
        raise ValueError(f"{path.name}: shape {d.shape}")
    rpm = d[:, 2][d[:, 2] > 0]
    if rpm.size != 1:
        raise ValueError(f"{path.name}: expected one speed reading, got {rpm.size}")
    load = float(d[0, 3])
    x = d[:, 0].astype(np.float32)
    np.savez(c, x=x, rpm=rpm[0], load=load)
    return x, float(rpm[0]), load


def load() -> list[Record]:
    files = sorted(RAW.glob("*.csv"))
    if len(files) != 60:
        raise FileNotFoundError(f"expected 60 UORED CSVs in {RAW}, found {len(files)}")
    out = []
    for p in files:
        m = NAME_RE.match(p.stem)
        if not m:
            raise ValueError(f"unexpected UORED file {p.name}")
        letter, b, st = m.group(1), int(m.group(2)), int(m.group(3))
        if b not in BEARING_RANGE[letter] or (letter == "H") != (st == 0):
            raise ValueError(f"{p.name}: inconsistent with the documented numbering")
        x, rpm, load_n = _read(p)
        # label: state 0 is healthy for every bearing; the letter of a state-0 file is H
        fault = FAULT[letter]
        out.append(Record(dataset="UORED", record_id=p.stem, bearing_id=f"uored_{b}", bearing_model="6203_UORED",
                          fault_type=fault, condition="1750rpm_nominal", rpm=rpm, rpm_source="measured_in_file",
                          fs_hz=FS, signal=x,
                          meta={"health_state": STATE[st], "manufacturer": "NSK" if b <= 5 else "FAFNIR",
                                "load_N": load_n}))
    return out


def assert_bearing_split(train_ids, test_ids) -> None:
    """C36b: UORED splits are keyed on bearing_id; any overlap is a hard failure."""
    both = set(train_ids) & set(test_ids)
    if both:
        raise AssertionError(f"UORED bearing-level leakage: {sorted(both)}")
