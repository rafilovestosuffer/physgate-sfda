"""HUST bearing loader (Thuan & Hong, BMC Res Notes 16(1):138, 2023; Mendeley doi:10.17632/cbv7jyx4p9 v3,
CC BY 4.0). Hanoi University of Science and Technology.

VERIFIED ON THE FILES (2026-09-13):
  * 99 .mat files named <FAULT><MODEL>0<LOAD> (e.g. B502): FAULT in {N, I, O, B, IB, IO, OB}; MODEL digit 4..8 ->
    bearing 6204..6208; LOAD digit 0/2/4 -> 0/200/400 W. Ball (B) has 12 files: no 6204 ball records.
  * `data`: vibration at 51,200 Hz. Mostly 512,000 samples (10 s). 12 files are shorter, down to
    121,082 samples (2.36 s), but ALL 12 are COMPOUND-fault records; every single-fault record is
    >= 3 s and fits the Track A window. Length is carried per record.
  * `fs` is NOT the sampling rate. It is the PER-FILE SHAFT FREQUENCY in Hz. Evidence: the maximum of
    the `rpm` trace equals fs*60 exactly (B602: 1444.2 = 24.07*60; B604: 1362.0 = 22.70*60), and the
    values fall with load as induction-motor slip predicts (0 W ~24.9 Hz, 200 W ~24.2 Hz, 400 W ~22.9 Hz).
    -> resolves open item 4 at per-file granularity.
  * `rpm` trace is partly corrupt (negative values; B602 median -2.3e7). NOT used.

Physical identity is ASSUMED to be one bearing per (fault, model), re-run across the three loads.
Geometry for 6204/6206/6207/6208 is unverified. HUST's 6205 is a KG Bearing (India) part, not the
SKF 6205-2RS JEM whose geometry we verified, so it is registered separately as unverified.
"""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import scipy.io as sio

from records import Record, COMPOUND

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "hust" / "raw"
FS = 51200.0
NAME = re.compile(r"^(IB|IO|OB|N|I|O|B)([4-8])0([024])$")  # e.g. B502: ball, 6205, 200 W
FAULT = {"N": "normal", "I": "inner_race", "O": "outer_race", "B": "ball",
         "IB": COMPOUND, "IO": COMPOUND, "OB": COMPOUND}


def load(include_compound: bool = False) -> list[Record]:
    files = sorted(DATA.glob("*.mat"))
    if len(files) != 99:
        raise FileNotFoundError(f"expected 99 HUST files in {DATA}, found {len(files)}")
    out = []
    for p in files:
        m = NAME.match(p.stem)
        if not m:
            raise ValueError(f"unexpected HUST filename {p.name}")
        code, model_digit, load_digit = m.groups()
        fault = FAULT[code]
        if fault == COMPOUND and not include_compound:
            continue
        mat = sio.loadmat(p)
        sig = np.asarray(mat["data"], dtype=np.float32).ravel()
        f_r = float(np.asarray(mat["fs"]).ravel()[0])
        model = f"62{int(model_digit):02d}_HUST"
        out.append(Record(
            dataset="HUST", record_id=p.stem, bearing_id=f"hust_{code}_{model_digit}",
            bearing_model=model, fault_type=fault, condition=f"{int(load_digit) * 100}W",
            rpm=f_r * 60.0, rpm_source="measured_in_file", fs_hz=FS, signal=sig,
            meta={"fault_code": code, "load_W": int(load_digit) * 100, "shaft_hz": f_r,
                  "bearing_identity_assumed": True, "compound": fault == COMPOUND},
        ))
    return out
