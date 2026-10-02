"""Assemble the submission package into paper/submission/.

Contents: manuscript, highlights, supplementary S1-S3, figures, the frozen split definitions, the merged ledger, the decision
scripts, and a MANIFEST listing every result file cited by the manuscript with its size and SHA-256. Re-runnable; overwrites.
"""
from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "submission"
FILES = [
    ("paper/tex/main.tex", "manuscript/main.tex"),
    ("paper/tex/references.bib", "manuscript/references.bib"),
    ("paper/cover_letter.md", "cover_letter.md"),
    ("paper/supplementary_S4_traceability.md", "supplementary/S4_traceability.md"),
    ("paper/supplementary_S1_changes.md", "supplementary/S1_protocol_changes.md"),
    ("paper/supplementary_S2_gates.md", "supplementary/S2_gates.md"),
    ("paper/supplementary_S3_datasets.md", "supplementary/S3_datasets.md"),
    ("paper/references.bib", "references.bib"),
    ("paper/credit.md", "declarations/credit.md"),
    ("paper/data_availability.md", "declarations/data_availability.md"),
    ("paper/coi.md", "declarations/coi.md"),
    ("configs/splits.yaml", "reproducibility/splits.yaml"),
    ("configs/splits_k10.yaml", "reproducibility/splits_k10.yaml"),
    ("configs/bearings.yaml", "reproducibility/bearings.yaml"),
    ("PROTOCOL.md", "reproducibility/PROTOCOL.md"),
    ("DECISIONS.md", "reproducibility/DECISIONS.md"),
]
SCRIPTS = ["paper/make_tables.py", "paper/make_s4.py", "paper/check_manuscript.py",
           "paper/figures/style.py", "paper/figures/build_figures.py", "paper/figures/build_schematics.py",
           "paper/figures/validate_figures.py", "paper/figures/qa_layout.py", "experiments/c88_eval.py", "experiments/c87_eval.py", "experiments/final_decisions.py",
           "experiments/paired_gating.py", "experiments/c90_slip.py", "experiments/c90_synthetic.py",
           "experiments/append_ledger.py", "experiments/append_ledger_rf.py", "paper/make_s1.py", "paper/figures/fig_splits.py",
           "experiments/c96_clustered_stats.py", "experiments/c100_shot_splits.py", "experiments/c101_rf_splits.py",
           "experiments/c102_aa_floor.py", "kaggle/kernels/c103_pretrain_state.py"]


def sha(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()[:16]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    for rel, dest in FILES:
        src = ROOT / rel
        if not src.exists():
            print("MISSING", rel)
            continue
        (OUT / dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, OUT / dest)
    for rel in SCRIPTS:
        d = OUT / "reproducibility" / "scripts" / Path(rel).name
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, d)
    for sub in ("sections", "tables", "figures"):
        for f in (ROOT / "paper" / "tex" / sub).iterdir():
            if f.is_file():
                (OUT / "manuscript" / sub).mkdir(parents=True, exist_ok=True)
                shutil.copy(f, OUT / "manuscript" / sub / f.name)
    (OUT / "figures" / "data").mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "paper" / "figures" / "data").glob("*.csv"):
        shutil.copy(f, OUT / "figures" / "data" / f.name)
    for f in (ROOT / "paper" / "figures" / "preview").glob("*.png"):
        (OUT / "figures" / "preview").mkdir(parents=True, exist_ok=True)
        shutil.copy(f, OUT / "figures" / "preview" / f.name)
    led = OUT / "reproducibility" / "ledger"
    led.mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "results" / "ledger").glob("*.csv"):
        shutil.copy(f, led / f.name)
    # cited results
    # The LaTeX manuscript is the only manuscript. Cited results come from the S4 claim list, which is maintained with it
    # (the markdown draft that used to seed this list stopped at v0.2 and is not part of the submission).
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "paper"))
    import make_s4
    cited = sorted({rel for rel, _, _ in make_s4.CLAIMS})
    lines = ["# Manifest — result files cited by the manuscript", "",
             f"git {subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()}", "",
             "| cited path | bytes | sha256 (16) |", "|---|---|---|"]
    for c in cited:
        src = ROOT / c
        if src.is_dir():
            files = sorted(src.rglob("*.md")) + sorted(src.rglob("*.json"))
            for f in files[:6]:
                lines.append(f"| {f.relative_to(ROOT).as_posix()} | {f.stat().st_size} | {sha(f)} |")
        elif src.exists():
            dest = OUT / "results" / Path(c).name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src, dest)
            lines.append(f"| {c} | {src.stat().st_size} | {sha(src)} |")
        else:
            lines.append(f"| {c} | MISSING | — |")
    (OUT / "MANIFEST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    n = sum(1 for _ in OUT.rglob("*") if _.is_file())
    print(f"submission package: {n} files under {OUT.relative_to(ROOT)}")
    print("missing cited:", [l for l in lines if "MISSING" in l] or "none")


if __name__ == "__main__":
    main()
