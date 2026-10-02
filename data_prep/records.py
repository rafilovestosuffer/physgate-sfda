"""Common record interface for all four datasets.

The single most important field is `bearing_id`: the identity of the PHYSICAL bearing a signal was
recorded from. Splits are keyed on it (PROTOCOL section 3). A record from the same physical bearing
under a different load or speed has the SAME bearing_id -- that is precisely the leak Hendriks,
Dumond & Knox (MSSP 169:108732, 2022) identified in condition-wise CWRU splits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np

# Label spaces [FROZEN]
L3 = ("normal", "inner_race", "outer_race")
L4 = ("normal", "inner_race", "outer_race", "ball")
COMPOUND = "compound"  # out-of-label-space; excluded from main tables


@dataclass
class Record:
    dataset: str            # CWRU | PU | JNU | HUST
    record_id: str          # unique within dataset
    bearing_id: str         # PHYSICAL bearing identity -- the split key
    bearing_model: str      # kinematics key in configs/bearings.yaml (e.g. "6205", "6203")
    fault_type: str         # normal | inner_race | outer_race | ball | compound
    condition: str          # operating condition label
    rpm: float              # PER-FILE shaft speed where available; never a silent nominal
    rpm_source: str         # "measured_in_file" | "nominal_table" -- carried so H4's confound is auditable
    fs_hz: float
    signal: np.ndarray      # 1-D float32 vibration
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def seconds(self) -> float:
        return self.signal.size / self.fs_hz

    def label(self, space: str = "L3") -> int | None:
        classes = L3 if space == "L3" else L4
        return classes.index(self.fault_type) if self.fault_type in classes else None


def summarize(records: list[Record]) -> str:
    from collections import Counter
    by = Counter((r.fault_type) for r in records)
    bearings = Counter()
    for r in records:
        bearings[r.fault_type, r.bearing_id] += 1
    nb = Counter(ft for ft, _ in bearings)
    secs = sum(r.seconds for r in records)
    lines = [f"{len(records)} records, {secs/60:.1f} min of signal"]
    for ft in sorted(by):
        lines.append(f"  {ft:11s} records={by[ft]:4d}  physical_bearings={nb[ft]:3d}")
    return "\n".join(lines)
