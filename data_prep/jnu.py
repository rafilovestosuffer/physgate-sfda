"""JNU (Jiangnan University) loader. 12 CSV files, 50 kHz, single vibration column.

VERIFIED ON THE ACTUAL FILES (2026-09-13), correcting the literature:
  * fault recordings are 500,500 samples = 10.01 s; the normal recording is 1,501,500 = 30.03 s.
    Secondary sources state "20 s segments". They are wrong for this distribution.
  * EXACTLY ONE recording per (class, speed). There is therefore ONE physical bearing per fault class.

STRUCTURAL CONSEQUENCE -- a leakage-safe JNU split does not exist:
  every speed-transfer task (600->800 etc.) places the same physical bearing on both sides, and any
  within-speed split cuts windows out of one continuous recording. JNU can support Track R
  reproduction only; it cannot enter a bearing-wise table. This is reported as a finding.

CONFOUND (Li et al., Sensors 2013): normal/outer/roller were recorded on an N205, inner on an NU205.
A classifier can separate "inner" from the rest by bearing model alone.

Bearing identity is ASSUMED to be one bearing per class re-run across speeds; the dataset does not
document otherwise, and the assumption is the conservative one for leakage accounting.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from records import Record

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "jnu"
FS = 50000.0
PREFIX = {"n": "normal", "ib": "inner_race", "ob": "outer_race", "tb": "ball"}  # tb = roller
MODEL = {"normal": "N205", "outer_race": "N205", "ball": "N205", "inner_race": "NU205"}


def _parse(stem: str) -> tuple[str, int]:
    for p in ("ib", "ob", "tb", "n"):
        if stem.startswith(p):
            rest = stem[len(p):]
            return PREFIX[p], int(rest.split("_")[0])
    raise ValueError(stem)


def load() -> list[Record]:
    out = []
    files = sorted(DATA.glob("*.csv"))
    if len(files) != 12:
        raise FileNotFoundError(f"expected 12 JNU csv files in {DATA}, found {len(files)}")
    for p in files:
        fault, rpm = _parse(p.stem)
        sig = np.loadtxt(p, delimiter=",", dtype=np.float32).ravel()
        out.append(Record(
            dataset="JNU", record_id=p.stem, bearing_id=f"jnu_{fault}",
            bearing_model=MODEL[fault], fault_type=fault, condition=f"{rpm}rpm",
            rpm=float(rpm), rpm_source="nominal_table", fs_hz=FS, signal=sig,
            meta={"bearing_identity_assumed": True, "file": p.name,
                  "bearing_model_confound": MODEL[fault]},
        ))
    return out
