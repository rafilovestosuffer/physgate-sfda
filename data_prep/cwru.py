"""CWRU drive-end loader (64 records: 60 fault @ 12 kHz + 4 normal @ 48 kHz).

NOTE: the four NORMAL baselines are 48 kHz. Filtering to 12 kHz silently drops the whole healthy
class, so fs_filter defaults to None and fs is carried per record.

Physical-bearing identity: CWRU seeded ONE bearing per (fault location, size, outer-race position) and
re-ran it at loads 0-3 hp. So all four loads of e.g. inner-race 0.007" share one bearing_id. The four
normal records are ONE physical healthy bearing -- CWRU's healthy class cannot be bearing-wise split
(PROTOCOL 3.2, a stated limitation).
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import scipy.io as sio

from records import Record

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "cwru"
OPS = ROOT / "notes" / "_pmmcp_records_ops.json"
LABELS = ROOT / "notes" / "_pmmcp_labels.json"


def _bearing_id(lab: dict) -> str:
    if lab["fault_type"] == "normal":
        return "cwru_normal"
    size = lab.get("fault_diameter_in")
    pos = lab.get("or_position") or "na"
    return f"cwru_{lab['fault_type']}_{size:.3f}_{pos}"


def load(channel: str = "DE", fs_filter: float | None = None) -> list[Record]:
    ops = json.load(io.open(OPS, encoding="utf-8"))
    labs = json.load(io.open(LABELS, encoding="utf-8"))
    out = []
    for o in ops:
        if fs_filter is not None and o["fs_hz"] != fs_filter:
            continue
        p = DATA / o["cache_filename"]
        if not p.exists():
            raise FileNotFoundError(f"{p} missing -- run data_prep/download_cwru.py")
        m = sio.loadmat(p)
        key = o["internal_mat_key"].replace("_DE_", f"_{channel}_")
        if key not in m:
            raise KeyError(f"{p.name}: key {key} not found; keys={[k for k in m if not k.startswith('__')]}")
        sig = np.asarray(m[key], dtype=np.float32).ravel()
        rpm_keys = [k for k in m if k.endswith("RPM")]
        if rpm_keys:
            rpm, src = float(np.asarray(m[rpm_keys[0]]).ravel()[0]), "measured_in_file"
        else:
            rpm, src = float(o["nominal_rpm"]), "nominal_table"
        lab = labs[o["opaque_id"]]
        out.append(Record(
            dataset="CWRU", record_id=str(o["file_id"]), bearing_id=_bearing_id(lab),
            bearing_model="6205" if channel == "DE" else "6203",
            fault_type=lab["fault_type"], condition=f"load{o['load_hp']}hp",
            rpm=rpm, rpm_source=src, fs_hz=float(o["fs_hz"]), signal=sig,
            meta={"load_hp": o["load_hp"], "fault_diameter_in": lab.get("fault_diameter_in"),
                  "or_position": lab.get("or_position"), "sr2015_grade": lab.get("sr2015_grade"),
                  "known_anomalies": lab.get("known_anomalies", []), "nominal_rpm": o["nominal_rpm"],
                  "opaque_id": o["opaque_id"], "channel": channel},
        ))
    return out
