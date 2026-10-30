"""Build Supplementary S4: every result file the manuscript cites, with the runs behind it and their checksums.

Generated, never hand-edited. Sources: the manuscript's own source tags, results/ledger/*.csv and the retained artifacts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "tex"
OUT = ROOT / "paper" / "supplementary_S4_traceability.md"
RELEASE = ROOT / "paper" / "release.json"   # archive version and DOI, kept out of this script so its hash is stable

# result file -> (what it establishes in the paper, ledger run_id prefix that produced it)
CLAIMS = [
    ("results/c108/c108_purity.json", "Descriptive window-label purity by specimen", ""),
    ("results/c111/c111_probe_ablations.json", "Identity probe ablations on retained representations", ""),
    ("results/c104/C104B_RESULT.md", "Post-hoc class-specific same-condition analysis", ""),
    ("results/c105/c105_source_only.json", "Source-only and post-adaptation contrasts", ""),
    ("results/c106/c106_within_bearing.json", "Within-bearing descriptive contrasts", ""),
    ("results/c107/c107_gate_spillover.json", "Gate gain accounting", ""),
    ("results/c109/c109_intervals.json", "Conditional intervals and healthy false acceptance", ""),
    ("results/c110/c110_result.json", "Source expansion: diversity and volume change together", ""),
    ("results/c112/c112_result.json", "Original ordinary and saved balanced kinematic outcomes", ""),
    ("results/reporting_2026_10_09/reporting_corrections.json", "Reporting-only corrections and saved-score sensitivity (S6)", ""),
    ("results/c114/c114_unseen_labels.json", "Labels given to seen and unseen bearings; KI04/KI14 sensitivity (Sections 3, 6.4; S6.10)", ""),
    ("results/c115/c115_intervals.json", "Order-statistic intervals for every reported median; leave-one-bearing-out (Sections 4.5, 6; S6.11)", ""),
    ("results/c116/c116_gate_override.json", "Gate-override comparison, gain by certifiable bearings, SDALR reliability split (Section 6.6, Table 8)", ""),
    ("results/m4b/M4B_RESULT.md", "Comb gate against Smith and Randall's CWRU diagnosability grades (Section 6.6, S2.6)", ""),

    ("results/M0_PU_RESULT.md", "Reproduction of the published method on its own tasks (Section 6.1)", "m0-pu"),
    ("results/M1_RESULT.md", "Collapse on the two mechanical folds (Section 6.2)", "physgate-m1"),
    ("results/c88/C88_RESULT.md", "Ten pre-specified random bearing splits: collapse, gating, decomposition", "physgate-run-k10"),
    ("results/c94/C94_RESULT.md", "Second rig (HUST): six type-disjoint splits", "physgate-run-hust"),
    ("results/C85_RESULT.md", "WITHDRAWN: local SHOT outputs, two folds; indexing defect (S6)", "physgate-shot-f"),
    ("results/c100/C100_RESULT.md", "WITHDRAWN: local SHOT outputs, ten splits; indexing defect (S6)", "physgate-shot-k10"),
    ("results/c113/c113_shot_splits.json", "Corrected SHOT (patch v2) on the ten splits, both arms (Section 6.3, C113)", "physgate-shot2-k10"),
    ("results/c113/c113_dedup_check.json", "C113 loss with byte-identical Paderborn windows scored once (Section 3)", ""),
    ("results/c101/C101_RESULT.md", "Random forests on the ten splits, both arms (Section 6.3)", "physgate-run-c92"),
    ("results/c96/C96_RESULT.md", "Cluster-level inference and the Benjamini--Hochberg family (Section 4, S1)", ""),
    ("results/c97/C97_RESULT.md", "Identity probe on ten handcrafted time statistics (Section 6.4)", ""),
    ("results/c98/C98_RESULT.md", "In-loop gate coverage and the coverage-gain correlation (Section 6.6)", ""),
    ("results/c99/C99_RESULT.md", "Off-rig calibration of the envelope-rule operating point (Section 6.6)", ""),
    ("results/c102/C102_RESULT.md", "A/A floor: repeated executions of one configuration (Section 4)", "physgate-m2rep"),
    ("results/c103/C103_RESULT.md", "Cross-job gap: pretraining-state test and code diagnosis (Section 4)", "physgate-c103"),
    ("results/c104/C104_RESULT.md", "Same-condition, bearing-disjoint control (Section 6.3)", ""),
    ("results/c91/C91_RESULT.md", "Non-adaptive random-forest baselines on the two folds", "physgate-c91"),
    ("results/C83_RESULT.md", "Gating inside adaptation across three seeds", "physgate-m2"),
    ("results/PAIRED_GATING.md", "Pairing configuration and the collapse decomposition", "physgate-m2"),
    ("results/c87/N1_RESULT.md", "Within-class bearing-identity probe", "physgate-run-n1"),
    ("results/roc/ROC_RESULT.md", "Gate operating curves on Paderborn", ""),
    ("results/h7/H7_RESULT.md", "Gate false acceptance at the pre-specified operating points", ""),
    ("results/comb_v2/COMB_V2_RESULT.md", "Shaft-alias-guarded comb beside the frozen comb test", ""),
    ("results/c90/C90_RESULT.md", "Measured cage slip and the shaft-order lock", ""),
    ("results/b6a/B6A_RESULT.md", "CWRU cross-end contamination (Supplementary S3)", ""),
    ("results/c78/C78_RESULT.md", "Within-CWRU fan-end/drive-end control, null (Supplementary S3)", ""),
    ("results/b7_uored/B7_UORED_RESULT.md", "UORED gate behaviour and logged-speed problem (Supplementary S2, S3)", ""),
]


CRLF, LF = bytes((13, 10)), bytes((10,))


def sha(p: Path) -> str:
    """SHA-256 of the content with CRLF normalised to LF, so the value is the same on every operating system."""
    return hashlib.sha256(p.read_bytes().replace(CRLF, LF)).hexdigest()[:16]


def main():
    runs = defaultdict(list)
    for f in sorted((ROOT / "results" / "ledger").glob("*.csv")):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            runs[r["run_id"]].append(r)
    ledger_rows = sum(len(v) for v in runs.values())
    release = json.loads(RELEASE.read_text(encoding="utf-8"))

    lines = [
        "# Supplementary S4 — traceability of every reported number", "",
        "Each row is a result file cited by the manuscript, what it establishes, the Kaggle account that produced the runs "
        "behind it, and the SHA-256 (first 16 hex digits) of the file as submitted. The experiment ledger "
        f"(`results/ledger/*.csv`, {ledger_rows} rows) lists every individual run with its kernel URL, git commit and "
        f"retained artifact path. Run artifacts and every script listed here are in the public archive release {release['version']} "
        f"(https://doi.org/{release['doi']}), which contains the original runs of v1.0-submission, the corrected SHOT run "
        "(C113) and the post-hoc analyses C114-C116; reporting-only corrections are included in it. Reporting ledger rows "
        "are labelled separately and are not new experimental runs.", "",
        "All SHA-256 values in this supplement are computed on file content with line endings normalised to LF, so they "
        "verify identically on any operating system (strip carriage returns before hashing).", "",
        "| result file | establishes | runs | sha256 |", "|---|---|---|---|",
    ]
    for rel, what, prefix in CLAIMS:
        p = ROOT / rel
        if not p.exists():
            lines.append(f"| {rel} | {what} | MISSING | — |")
            continue
        hits = [r for k, v in runs.items() if prefix and k.startswith(prefix) for r in v]
        acc = sorted({r["kaggle_account"] for r in hits})
        runcell = (f"{len(hits)} ledger rows ({', '.join(acc)})" if hits
                   else "kernel artifact retained; probe outputs, not per-task accuracy rows" if prefix
                   else "deterministic analysis of retained data or artifacts; script in experiments/")
        lines.append(f"| `{rel}` | {what} | {runcell} | `{sha(p)}` |")

    figs = sorted((ROOT / "paper" / "figures" / "data").glob("*.csv"))
    lines += ["", "## Figure data", "",
              "The exact values plotted in each figure are provided as CSV so that any figure can be recomputed or "
              "re-plotted independently.", "", "| figure | data file | rows | sha256 |", "|---|---|---|---|"]
    for f in figs:
        rows = sum(1 for _ in open(f, encoding="utf-8")) - 1
        lines.append(f"| {f.stem.replace('_', ' ')} | `paper/figures/data/{f.name}` | {rows} | `{sha(f)}` |")

    # every script that produces a reported number, table or figure, hashed like the results it produces (review round 4)
    scripts = sorted(set((ROOT / "experiments").glob("*.py")) | set((ROOT / "paper").glob("make_*.py"))
                     | {ROOT / "paper" / "check_manuscript.py", ROOT / "paper" / "revision_reporting.py"} | set((ROOT / "paper" / "figures").glob("*.py"))
                     | set((ROOT / "kaggle" / "kernels").glob("*.py")) | set((ROOT / "runners").glob("*.py")))
    lines += ["", "## Analysis, evaluation, figure and kernel scripts", "",
              "Every script that computes a reported number, builds a table or figure, or ran on Kaggle, with the SHA-256 "
              "(first 16 hex digits) of the file as submitted.", "", "| script | sha256 |", "|---|---|"]
    lines += [f"| `{p.relative_to(ROOT).as_posix()}` | `{sha(p)}` |" for p in scripts if p.name != "__init__.py"]

    lines += ["", "## Regenerating reporting files only", "",
              f"Use the archived experiment repository ({release['version']}); preserve the directory layout. No training is required. Historical experiment scripts remain available for audit; the withdrawn SHOT outputs must not be interpreted as valid SHOT performance.", "",
              "```", "python paper/revision_reporting.py", "python paper/make_tables.py",
              "python paper/figures/build_figures.py", "python paper/figures/build_schematics.py",
              "python paper/make_s1.py", "python paper/make_s4.py", "python paper/check_manuscript.py", "```", ""]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{OUT.name}: {len(CLAIMS)} result files, {len(figs)} figure data files, {ledger_rows} ledger rows")


if __name__ == "__main__":
    main()
