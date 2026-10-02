"""Bearing-wise split construction with a HARD leakage assertion. PROTOCOL section 3.

The assertion is not advisory. `assert_no_leak` raises LeakageError, and `build` calls it on every
task it produces unless the task is explicitly declared `leaky: true` (the Track R reproductions,
which exist precisely to measure the leak and are labelled as such in every table).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, Iterable, List, Set

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "configs" / "splits.yaml"


class LeakageError(RuntimeError):
    """A physical bearing appears on both sides of a task."""


def assert_no_leak(source_ids: Iterable[str], target_ids: Iterable[str], task: str = "") -> None:
    s, t = set(source_ids), set(target_ids)
    both = sorted(s & t)
    if both:
        raise LeakageError(f"{task}: {len(both)} physical bearing(s) on BOTH sides: {both}")


def mechanical_folds(ids: Iterable[str]) -> Dict[str, List[str]]:
    """Sort and split: first ceil(n/2) -> A. The rule in configs/splits.yaml, as code."""
    s = sorted(ids)
    k = math.ceil(len(s) / 2)
    return {"A": s[:k], "B": s[k:]}


def load_cfg() -> dict:
    return yaml.safe_load(CFG.read_text(encoding="utf-8"))


def verify_folds_follow_rule(cfg: dict | None = None) -> None:
    """The YAML must equal what the mechanical rule produces. Hand edits are caught here."""
    cfg = cfg or load_cfg()
    for group, spec in cfg["pu"].items():
        if "excluded" in spec:
            continue
        expected = mechanical_folds(spec["A"] + spec["B"])
        if expected != {"A": spec["A"], "B": spec["B"]}:
            raise ValueError(f"pu.{group} folds {spec} do not follow the mechanical rule {expected}")


def _expand(cfg: dict, groups: Dict[str, object]) -> Set[str]:
    out: Set[str] = set()
    for group, folds in groups.items():
        spec = cfg["pu"][group]
        for f in ([folds] if isinstance(folds, str) else list(folds)):
            out.update(spec[f])
    return out


def pu_task_bearings(task: str, reverse: bool = False, cfg: dict | None = None) -> Dict[str, Set[str]]:
    cfg = cfg or load_cfg()
    t = cfg["tasks"][task]
    if "population" in t:
        sf, tf = (t["target_fold"], t["source_fold"]) if reverse else (t["source_fold"], t["target_fold"])
        src = _expand(cfg, {g: sf for g in t["population"]})
        tgt = _expand(cfg, {g: tf for g in t["population"]})
    else:
        src, tgt = _expand(cfg, t["source"]), _expand(cfg, t["target"])
        if reverse:
            raise ValueError(f"{task} has fixed source/target roles; reversal is undefined")
    if not t.get("leaky", False):
        assert_no_leak(src, tgt, task)
    return {"source": src, "target": tgt}
