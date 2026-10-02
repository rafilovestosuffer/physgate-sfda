"""Append ledger rows for every retained adaptation artifact that is not yet in the ledger (PROTOCOL C15, rule 8).

One row per (run, task). Runner shard = the Kaggle account that produced the artifact, read from the kernel URL prefix in the
artifact folder name, not guessed: artifacts pulled from the co-author account live under results/artifacts/physgate-run-* that
were pushed there; the mapping is given explicitly in ACCOUNT below. Idempotent: existing run_ids are never rewritten.
"""
from __future__ import annotations

import csv
import glob
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "results" / "ledger"
COLS = ["run_id", "runner_id", "kaggle_account", "git_sha", "config_hash", "task", "method", "rung", "seed", "split_type",
        "label_space", "track", "window_samples", "n_records", "acc", "macro_f1", "ece", "nll", "oracle_gap_closure",
        "expected_false_accepts", "wall_clock_s", "gpu_hours", "kernel_url", "artifact_path", "notes"]
COAUTHOR = {"physgate-m2seed-fa-s1", "physgate-m2seed-fb-s1", "physgate-shot-fa", "physgate-shot-fb",
            "physgate-run-n1-probe", "physgate-run-k10-g1", "physgate-run-k10-g2", "physgate-run-k10-g3",
            "physgate-run-c92-rf-g12", "physgate-run-c92-rf-g3", "physgate-run-hust-k6",
            "physgate-shot-k10-g1", "physgate-shot-k10-g3"}  # g2, g4 ran on the primary account (verified by kernels status, 2026-09-29)
SHA = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def rows_for(path: Path):
    d = json.load(open(path, encoding="utf-8"))
    if d.get("smoke") or not d.get("adapted"):
        return []
    run = path.parts[path.parts.index("artifacts") + 1]
    acct = "rhrhrhrhrh" if run in COAUTHOR else "rafiurrahman01"
    gate = d.get("gate") or "none"
    src, tgt = d.get("src_fold"), d.get("tgt_fold")
    leaky = src == tgt
    ds = d["dataset"]
    out = []
    for task, acc in d["adapted"].items():
        rid = f"{run}-{d['variant']}-{src}to{tgt}-{gate}-{task.replace('->', 'to')}-s{d['seed']}"
        out.append({"run_id": rid, "runner_id": acct, "kaggle_account": acct, "git_sha": SHA, "config_hash": "",
                    "task": f"{ds} {task} {src}->{tgt}", "method": f"SDALR {d['variant']} gate={gate}" if d["variant"] != "shot" else "SHOT",
                    "rung": "", "seed": d["seed"], "split_type": "leaky" if leaky else "bearing-wise", "label_space": "L3",
                    "track": "R", "window_samples": 2048, "n_records": "", "acc": acc, "macro_f1": "", "ece": "", "nll": "",
                    "oracle_gap_closure": "", "expected_false_accepts": "", "wall_clock_s": d.get("seconds", {}).get(task, ""),
                    "gpu_hours": "", "kernel_url": f"https://www.kaggle.com/code/{acct}/{run}",
                    "artifact_path": str(path.relative_to(ROOT)).replace("\\", "/"), "notes": ""})
    return out


def main():
    existing, shards = set(), {}
    for f in LEDGER.glob("*.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            existing.add(r["run_id"])
    new = []
    for p in glob.glob(str(ROOT / "results" / "artifacts" / "**" / "result_*.json"), recursive=True):
        new += [r for r in rows_for(Path(p)) if r["run_id"] not in existing]
    for r in new:
        shards.setdefault(r["runner_id"], []).append(r)
    for acct, rs in shards.items():
        f = LEDGER / f"{acct}.csv"
        newfile = not f.exists()
        with open(f, "a", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=COLS)
            if newfile:
                w.writeheader()
            w.writerows(rs)
        print(f"{f.name}: +{len(rs)} rows")
    print("total appended", len(new))


if __name__ == "__main__":
    main()
