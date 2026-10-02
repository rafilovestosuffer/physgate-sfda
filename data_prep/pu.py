"""Paderborn (Lessmeier et al. 2016) loader. Cite Lessmeier et al. 2016 in any use.

VERIFIED on the files (2026-09-13):
  * Each bearing directory holds 80 .mat files = 4 conditions x 20 repetitions.
  * vibration_1 is sampled on the 'HostService' raster: 256,823 samples ~= 4.01 s at 64 kHz.
  * SPEED IS MEASURED: a 'speed' channel on the 4 kHz 'Mech_4kHz' raster. We use its mean as the
    record's shaft speed (rpm_source = measured_in_file) and keep its spread in meta, so H4 (order
    tracking) is evaluated on PU with real speed rather than CWRU's nominal values.
  * Also present: force, torque, two phase currents, bearing temperature. Unused here.

Full PU is ~2.6 GB of float32 vibration, so load() filters by bearing and condition.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
import scipy.io as sio
import yaml

from records import Record

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "pu"
FS = 64000.0
NAME_RE = re.compile(r"^(N\d\d_M\d\d_F\d\d)_(K[A-Z]?\d\d\d?|K[AIB]\d\d)_(\d+)$")


def _groups() -> dict:
    ds = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    return ds["datasets"]["PU"]["bearings"]


def geometry_key(bid: str) -> str:
    """C35: PU kinematics are per bearing (two pitch diameters across manufacturers). Never "6203"."""
    ds = yaml.safe_load((ROOT / "configs" / "datasets.yaml").read_text(encoding="utf-8"))
    for key, ids in ds["datasets"]["PU"]["geometry"].items():
        if bid in ids:
            return key
    raise KeyError(f"PU bearing {bid} has no geometry entry -- refusing to guess")


def bearing_meta(bid: str) -> tuple[str, str]:
    """-> (fault_type, damage_origin)."""
    for group, ids in _groups().items():
        if bid in ids:
            if group == "healthy":
                return "normal", "none"
            if group == "combined":
                return "compound", "real"
            origin, kind = group.split("_")
            return ("outer_race" if kind == "outer" else "inner_race"), origin
    raise KeyError(f"unknown PU bearing {bid}")


def _channel(struct, name: str) -> np.ndarray:
    for it in np.atleast_1d(struct.Y):
        if it.Name == name:
            return np.asarray(it.Data, dtype=np.float64).ravel()
    raise KeyError(name)


def read_one(path: Path) -> Record:
    stem = path.stem
    m = NAME_RE.match(stem)
    if not m:
        raise ValueError(f"unexpected PU filename {path.name}")
    cond, bid, rep = m.group(1), m.group(2), int(m.group(3))
    mat = sio.loadmat(path, squeeze_me=True, struct_as_record=False)
    s = mat[[k for k in mat if not k.startswith("__")][0]]
    vib = _channel(s, "vibration_1").astype(np.float32)
    spd = _channel(s, "speed")
    fault, origin = bearing_meta(bid)
    return Record(
        dataset="PU", record_id=stem, bearing_id=bid, bearing_model=geometry_key(bid),
        fault_type=fault, condition=cond, rpm=float(np.mean(spd)), rpm_source="measured_in_file",
        fs_hz=FS, signal=vib,
        meta={"repetition": rep, "damage_origin": origin, "rpm_std": float(np.std(spd)),
              "nominal_rpm": int(cond[1:3]) * 100},
    )


def files(bearings: Iterable[str] | None = None, conditions: Iterable[str] | None = None) -> list[Path]:
    b = set(bearings) if bearings else None
    c = set(conditions) if conditions else None
    out = []
    for d in sorted(p for p in DATA.iterdir() if p.is_dir()):
        if b and d.name not in b:
            continue
        for f in sorted(d.glob("*.mat")):
            mm = NAME_RE.match(f.stem)
            if mm and (c is None or mm.group(1) in c):
                out.append(f)
    return out


def iter_records(bearings=None, conditions=None) -> Iterator[Record]:
    for f in files(bearings, conditions):
        yield read_one(f)


def load(bearings=None, conditions=None) -> list[Record]:
    return list(iter_records(bearings, conditions))
