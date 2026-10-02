"""Manuscript quality gates. Exits non-zero on any failure.

  1. headline numbers in the .tex match the result files they come from
  2. every \\cite key exists in references.bib, and every bib entry is cited
  3. every \\ref resolves to a \\label; no duplicate labels; every table/figure is referenced
  4. abstract <= 250 words; 5 highlights, each <= 85 characters
  5. forbidden claims: cross-machine framing, any BIST-W result, any Bio-SFDA accuracy comparison, leftover placeholders
  6. no unresolved VERIFY flag on a cited reference
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "paper" / "tex"
fails: list[str] = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def body_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted((TEX / "sections").glob("*.tex")))


def tables_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted((TEX / "tables").glob("*.tex")))


def main():
    body, tables = body_text(), tables_text()
    whole = body + tables + (TEX / "main.tex").read_text(encoding="utf-8")
    res = lambda rel: (ROOT / rel).read_text(encoding="utf-8")

    # 1. headline numbers against their sources
    facts = [
        ("94.1", "results/M1_RESULT.md", "leaky mean on the two folds"),
        ("56.8", "results/M1_RESULT.md", "clean mean on the two folds"),
        ("36.2", "results/c88/C88_RESULT.md", "median ten-split collapse"),
        ("33.5", "results/c94/C94_RESULT.md", "median HUST collapse"),
        ("65.1", "results/C85_RESULT.md", "SHOT clean mean"),
        ("87.2", "results/C85_RESULT.md", "SHOT leaky mean"),
        ("507 of 508", "results/c87/N1_RESULT.md", "identity probe"),
        ("82", "results/c88/C88_RESULT.md", "median recoverable share"),
        ("8.9", "results/c88/C88_RESULT.md", "random forest minus SDALR"),
        ("0.06", "results/c90/C90_RESULT.md", "median measured slip"),
        ("508 of 508", "results/c97/C97_RESULT.md", "handcrafted-feature identity probe"),
        ("0.95", "results/c98/C98_RESULT.md", "coverage-gain rank correlation"),
        ("22.7", "results/c101/C101_RESULT.md", "median ten-split RF (time statistics) collapse"),
        ("32.1", "results/c101/C101_RESULT.md", "median ten-split RF (combined features) collapse"),
        # (manuscript form, source, what, source form) where the two are written differently
        ("$z = 36$", "results/c99/C99_RESULT.md", "off-rig zero-false-acceptance operating point", "z* = 36.0**"),
        ("333 of 1839", "results/c99/C99_RESULT.md", "Paderborn transfer at the off-rig point", "| 333/1839 | 0/480 |"),
        ("21.7", "results/c100/C100_RESULT.md", "median ten-split SHOT collapse"),
        ("29.7", "results/c104/C104_RESULT.md", "median same-condition collapse (C104)"),
        ("28.5", "results/c104/C104B_RESULT.md", "inner-race same-condition recall drop (C104b)"),
        ("66 paired tasks", "results/c102/C102_RESULT.md", "A/A floor coverage"),
        ("35.1", "results/c105/c105_source_only.json", "median source-only collapse (C105)"),
        ("38.7", "results/c106/c106_within_bearing.json", "median within-bearing difference (C106)"),
        ("74.6", "results/c110/c110_result.json", "unseen-bearing accuracy at four specimens per class (C110)"),
        ("45.9", "results/c110/c110_result.json", "unseen-bearing accuracy at one specimen per class (C110)", "45.864"),
        ("8.4", "results/c112/c112_result.json", "median kinematic-forest collapse (C112)"),
        ("104", "results/c107/c107_gate_spillover.json", "share of gate gain on certified windows (C107)", "1.037"),
        ("25.0--56.3", "results/c109/c109_intervals.json", "CI of the median collapse (C109)", "25.0183"),
    ]
    # 1b. every BH-adjusted value quoted anywhere must be a member of the recomputed C96 family (rounded to 3 dp)
    import json as _json
    fam = _json.loads(res("results/c96/c96_family.json"))["family"]
    allowed = {f"{m['bh']:.3f}" for m in fam}
    for v in re.findall(r"p_\{\\mathrm\{BH\}\}\s*=\s*([0-9.]+)", whole):
        check(f"{float(v):.3f}" in allowed, f"p_BH = {v} is not a member of the C96 family {sorted(allowed)}")
    allowed_by = {f"{m['by']:.3f}" for m in fam if "by" in m}
    for v in re.findall(r"p_\{\\mathrm\{BY\}\}\s*=\s*([0-9.]+)", whole):
        check(f"{float(v):.3f}" in allowed_by, f"p_BY = {v} is not a member of the C96 family {sorted(allowed_by)}")
    for value, src, what, *src_form in facts:
        check(value in whole, f"{what}: {value} is not in the manuscript")
        hay = res(src).replace("507/508", "507 of 508").replace("508/508", "508 of 508")
        needle = src_form[0] if src_form else value
        check(needle in hay, f"{what}: {needle} is not in {src}")

    # 2. citations
    bib = (TEX / "references.bib").read_text(encoding="utf-8")
    keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    cited = {k.strip() for m in re.findall(r"\\cite\{([^}]+)\}", whole) for k in m.split(",")}
    for k in sorted(cited - keys):
        check(False, f"\\cite{{{k}}} has no entry in references.bib")
    for k in sorted(keys - cited):
        check(False, f"references.bib entry '{k}' is never cited")
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", bib, re.S):
        if "VERIFY" in m.group(2) and m.group(1) in cited:
            check(False, f"reference '{m.group(1)}' still carries a VERIFY flag")

    # 3. cross-references
    labels = re.findall(r"\\label\{([^}]+)\}", whole)
    check(len(labels) == len(set(labels)), "duplicate \\label in the manuscript")
    for r in {m for m in re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", whole)}:
        check(r in labels, f"\\ref{{{r}}} has no matching \\label")
    for lab in labels:
        if lab.startswith(("tab:", "fig:")):
            check(len(re.findall(r"\\ref\{" + re.escape(lab) + r"\}", whole)) >= 1, f"{lab} is never referenced")

    # 4. front-matter limits
    abstract = re.sub(r"%.*", "", (TEX / "sections" / "00_abstract.tex").read_text(encoding="utf-8"))
    abstract = re.sub(r"\\SI\{([^}]*)\}\{[^}]*\}", r"\1", abstract)
    n = len(re.sub(r"\\[a-zA-Z]+", " ", abstract).split())
    check(n <= 250, f"abstract is {n} words, limit 250")
    items = re.findall(r"\\item (.+)", (TEX / "main.tex").read_text(encoding="utf-8"))
    check(len(items) == 5, f"{len(items)} highlights, Elsevier allows 3-5")
    for it in items:
        check(len(it.strip()) <= 85, f"highlight over 85 characters ({len(it.strip())}): {it.strip()[:60]}...")

    # 5. claims we must not make
    for pattern, why in [
        (r"cross-machine (?:transfer|adaptation|result)s?\b(?!.{0,40}not claimed)", "cross-machine claim"),
        (r"BIST-W (?:recovers|improves|raises|gains)", "a BIST-W result (the experiment was cut before any outcome)"),
        (r"(?:outperform|better than|compared with).{0,40}Bio-SFDA", "an accuracy comparison against Bio-SFDA"),
        (r"\bTODO\b|\bXXX\b|(?:median|mean|by|of|is|reaches)\s+null\b|null\s*(?:\%|pp|points)",
         "an unfilled placeholder"),
        (r"Author One|Author Two|example\.edu", "a leftover author placeholder"),
    ]:
        for m in re.finditer(pattern, body, re.I):
            check(False, f"forbidden text ({why}): '{body[max(0, m.start() - 40):m.end() + 40].strip()}'")

    # 6. control sequences destroyed by an editing accident: a literal CR/TAB/FF where a backslash belongs.
    # "\r" in a Python string that reaches a file as a carriage return turns \ref into visible garbage and
    # compiles without an error, so it has to be caught here rather than in the LaTeX log.
    for path in sorted(TEX.rglob("*.tex")):
        raw = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
        for ch, name in (("\r", "CR"), ("\t", "TAB"), ("\f", "FF"), ("\v", "VT"), ("\b", "BS"), ("\a", "BEL")):
            if ch in raw:
                i = raw.index(ch)
                check(False, f"{path.name}: literal {name} where a control sequence belongs: "
                             f"{raw[max(0, i - 30):i + 30]!r}")

    print(f"checked {len(facts)} headline numbers, {len(cited)} citations, {len(labels)} labels")
    if fails:
        print("\nFAILURES")
        for f in fails:
            print(" -", f)
        sys.exit(1)
    print("manuscript checks passed")


if __name__ == "__main__":
    main()
