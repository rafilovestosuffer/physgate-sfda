"""Kaggle CPU kernel: compile the manuscript to PDF (no LaTeX toolchain on the authoring machine).

Copies the staged LaTeX sources, ensures a TeX distribution with elsarticle, runs pdflatex/bibtex/pdflatex/pdflatex and
leaves main.pdf plus the full log in /kaggle/working/pdf/.
"""
import shutil, subprocess, sys
from pathlib import Path

OUT = Path("/kaggle/working/pdf"); OUT.mkdir(parents=True, exist_ok=True)
src = next(p for p in Path("/kaggle/input").rglob("main.tex")).parent
work = Path("/kaggle/working/build"); shutil.rmtree(work, ignore_errors=True)
shutil.copytree(src, work)
print("sources:", sorted(p.name for p in work.iterdir()), flush=True)


def run(cmd, **kw):
    print("$", " ".join(cmd), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    print(r.stdout[-3000:])
    if r.returncode and r.stderr:
        print("STDERR", r.stderr[-2000:])
    return r


have_tex = shutil.which("pdflatex") is not None
print("pdflatex present:", have_tex, flush=True)
if not have_tex:
    run(["apt-get", "update", "-qq"])
    run(["apt-get", "install", "-y", "-qq", "texlive-latex-recommended", "texlive-latex-extra",
         "texlive-fonts-recommended", "texlive-publishers", "texlive-science", "lmodern"])
elif not subprocess.run(["kpsewhich", "elsarticle.cls"], capture_output=True, text=True).stdout.strip():
    run(["apt-get", "update", "-qq"])
    run(["apt-get", "install", "-y", "-qq", "texlive-publishers", "texlive-latex-extra", "texlive-science"])

cls = subprocess.run(["kpsewhich", "elsarticle.cls"], capture_output=True, text=True).stdout.strip()
print("elsarticle.cls:", cls or "NOT FOUND", flush=True)

for i, cmd in enumerate([["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "main"],
                         ["bibtex", "main"],
                         ["pdflatex", "-interaction=nonstopmode", "main"],
                         ["pdflatex", "-interaction=nonstopmode", "main"]]):
    r = run(cmd, cwd=work)
    if i == 0 and r.returncode:
        print("first pass failed; see log", flush=True)
        break

pdf = work / "main.pdf"
if pdf.exists():
    shutil.copy(pdf, OUT / "manuscript.pdf")
    print("PDF OK", pdf.stat().st_size, "bytes", flush=True)
else:
    print("NO PDF PRODUCED", flush=True)
for ext in ("log", "blg", "bbl"):
    f = work / f"main.{ext}"
    if f.exists():
        shutil.copy(f, OUT / f"main.{ext}")
print("done", sorted(p.name for p in OUT.iterdir()), flush=True)
