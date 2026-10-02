"""Shared read-only loader for the round-6 post-hoc analyses (C105-C109).

Reads retained artifacts only: per-arm result JSONs, the per-task adaptation logs (pre-update accuracy, i.e. the source
model's accuracy on the target before any adaptation step) and the per-window prediction dumps (pred_NN.npz). No training,
no GPU. Light enough to run locally (CLAUDE.md rule 4).
"""
from __future__ import annotations

import glob
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "results" / "artifacts"
TASKS = ["A1->A3", "A1->A2", "A3->A1", "A3->A2", "A2->A1", "A2->A3"]
FILE2TASK = {"01": "A1->A3", "02": "A1->A2", "10": "A3->A1", "12": "A3->A2", "20": "A2->A1", "21": "A2->A3"}
SPLITS = [f"S{i:02d}" for i in range(10)]
PRE = re.compile(r"批次:[·\s]*0/[·\s]*\d+;\s*总正确率:\s*([0-9.]+)%")
CLASS = {0: "normal", 1: "inner", 2: "outer"}


def pre_update(logdir: Path) -> dict:
    """Accuracy logged at batch 0 of each adaptation task, before any update: the source-only accuracy."""
    out = {}
    for f, t in FILE2TASK.items():
        p = logdir / f"adapt_{f}.log"
        if p.exists():
            m = PRE.search(p.read_text(encoding="utf-8", errors="replace"))
            if m:
                out[t] = float(m.group(1))
    return out


def preds(logdir: Path) -> dict:
    out = {}
    for f, t in FILE2TASK.items():
        p = logdir / f"pred_{f}.npz"
        if p.exists():
            d = np.load(p)
            out[t] = dict(pred=d["prob"].argmax(1), label=d["label"], rec=d["record_id"].astype(str))
    return out


def arm(result_json: str | Path) -> dict:
    result_json = Path(result_json)
    d = json.loads(result_json.read_text(encoding="utf-8"))
    logdir = result_json.parent / ("logs_" + result_json.stem[len("result_"):])
    return dict(adapted=d["adapted"], pre=pre_update(logdir), preds=preds(logdir), path=str(result_json.relative_to(ROOT)))


@lru_cache(maxsize=1)
def load() -> dict:
    """{'k10': {(src, tgt, gate): arm}, 'shot': {(src, tgt): arm}, 'fold': {(job, stem): arm}}"""
    D = {"k10": {}, "shot": {}, "fold": {}}
    for p in glob.glob(str(ART / "physgate-run-k10-*" / "k10" / "S*" / "result_PU_M1_*.json")):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        if d.get("smoke") or len(d["adapted"]) < 6:
            continue
        D["k10"][(d["src_fold"], d["tgt_fold"], d.get("gate") or "none")] = arm(p)
    for p in glob.glob(str(ART / "physgate-shot-k10-*" / "shot_k10" / "S*" / "result_PU_M1_*.json")):
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        D["shot"][(d["src_fold"], d["tgt_fold"])] = arm(p)
    for job in ("m1-fa", "m1-fb", "m2-fa", "m2-fb"):
        for p in glob.glob(str(ART / f"physgate-{job}" / "*" / "result_*.json")):
            D["fold"][(job, Path(p).stem)] = arm(p)
    return D


def bearing_of(record_id: str) -> str:
    return record_id.split("_")[3]


def mean6(a: dict, key: str) -> float:
    return float(np.mean([a[key][t] for t in TASKS]))


def sign_flip_p(x, alternative="two-sided") -> float:
    """Exact sign-flip permutation p for the mean of x (n <= 20)."""
    x = np.asarray(x, float)
    n = len(x)
    signs = ((np.arange(2 ** n)[:, None] >> np.arange(n)) & 1) * 2 - 1
    stats = (signs * x).mean(1)
    obs = x.mean()
    if alternative == "greater":
        return float((stats >= obs - 1e-12).mean())
    return float((np.abs(stats) >= abs(obs) - 1e-12).mean())


def boot_median_ci(x, n=20000, seed=0):
    """Percentile bootstrap interval of the median, resampling clusters (the entries of x)."""
    x = np.asarray(x, float)
    rng = np.random.default_rng(seed)
    meds = np.median(x[rng.integers(0, len(x), (n, len(x)))], axis=1)
    lo, hi = np.percentile(meds, [2.5, 97.5])
    return [float(lo), float(hi)]


def dump(obj, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=float), encoding="utf-8")
