"""Append ledger rows for the non-adaptive random-forest runs (C91 two folds, C92 ten splits), which the adaptation
appender does not see because they write one summary JSON per kernel rather than result_*.json per run (rule 8).

One row per (kernel, split or fold, feature set, task, arm). Account attribution reuses append_ledger.COAUTHOR, verified
against `kaggle kernels status` on both accounts (2026-09-29): c91 and c92-g4 primary, c92-g12 and c92-g3 co-author.
Idempotent: existing run_ids are never rewritten.
"""
from __future__ import annotations

import csv
import glob
import json
from pathlib import Path

import append_ledger as L

FEATURES = {"T": "10 time statistics", "F": "64 spectral bands", "E": "envelope spectrum", "TFE": "all three feature sets"}


def rows():
    out = []
    specs = [(p, "c91") for p in glob.glob(str(L.ROOT / "results/artifacts/physgate-c91-shallow-cpu/**/c91_result.json"),
                                          recursive=True)]
    specs += [(p, "c92") for p in glob.glob(str(L.ROOT / "results/artifacts/physgate-run-c92-rf-*/**/c92_result.json"),
                                           recursive=True)]
    for p, kind in specs:
        path = Path(p)
        run = path.parts[path.parts.index("artifacts") + 1]
        acct = "rhrhrhrhrh" if run in L.COAUTHOR else "rafiurrahman01"
        d = json.load(open(path, encoding="utf-8"))
        # c91: {feature: {rows: [{src_fold, task, leaky, clean}]}}; c92: {split: {feature: {rows: [{task, leaky, clean}]}}}
        blocks = ([(None, fs, v) for fs, v in d.items()] if kind == "c91"
                  else [(sid, fs, v) for sid, per in d.items() for fs, v in per.items()])
        for sid, fs, v in blocks:
            for r in v["rows"]:
                src = r.get("src_fold") or sid
                for arm in ("leaky", "clean"):
                    tgt = src if arm == "leaky" else (("B" if src == "A" else "A") if kind == "c91" else f"{src}c")
                    rid = f"{run}-rf{fs}-{src}to{tgt}-{r['task'].replace('->', 'to')}"
                    out.append({"run_id": rid, "runner_id": acct, "kaggle_account": acct, "git_sha": L.SHA,
                                "config_hash": "", "task": f"PU_M1 {r['task']} {src}->{tgt}",
                                "method": f"random forest ({FEATURES.get(fs, fs)}), no adaptation", "rung": "",
                                "seed": "", "split_type": "leaky" if arm == "leaky" else "bearing-wise",
                                "label_space": "L3", "track": "R", "window_samples": 2048, "n_records": "",
                                "acc": round(float(r[arm]), 4), "macro_f1": "", "ece": "", "nll": "",
                                "oracle_gap_closure": "", "expected_false_accepts": "", "wall_clock_s": "",
                                "gpu_hours": "0 (CPU kernel)", "kernel_url": f"https://www.kaggle.com/code/{acct}/{run}",
                                "artifact_path": str(path.relative_to(L.ROOT)).replace("\\", "/"),
                                "notes": f"{kind.upper()} random-forest baseline"})
    return out


def main():
    existing = set()
    for f in L.LEDGER.glob("*.csv"):
        existing |= {r["run_id"] for r in csv.DictReader(open(f, encoding="utf-8"))}
    new = [r for r in rows() if r["run_id"] not in existing]
    ids = [r["run_id"] for r in new]
    assert len(ids) == len(set(ids)), "duplicate run_ids generated"
    shards = {}
    for r in new:
        shards.setdefault(r["runner_id"], []).append(r)
    for acct, rs in shards.items():
        with open(L.LEDGER / f"{acct}.csv", "a", newline="", encoding="utf-8") as fh:
            csv.DictWriter(fh, fieldnames=L.COLS).writerows(rs)
        print(f"{acct}.csv: +{len(rs)} rows")
    print("total appended", len(new))


if __name__ == "__main__":
    main()
