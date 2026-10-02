"""Build Supplementary S1 (pre-registered vs changed) from the PROTOCOL.md change-log rows. Regenerate; never hand-edit S1."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
rows = []
for line in (ROOT / "PROTOCOL.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*\*\*(C\d+[a-z]?)\*\*\s*\|(.*)\|(.*)\|\s*$", line)   # suffixed IDs (C104b) are post-hoc add-ons
    if not m:
        continue
    cid, change, why = m.group(1), m.group(2).strip(), m.group(3).strip()
    title = re.match(r"\*\*(.+?)\*\*", change)
    title = title.group(1) if title else change[:160]
    low = change.lower()
    # order matters: a row that says "post-hoc" is post-hoc even where it also discusses pre-registration, and
    # mislabelling one as pre-registered is exactly the error this table exists to prevent.
    kind = ("withdrawn" if "WITHDRAWN" in change
            else "post-hoc (descriptive)" if "post-hoc" in low
            else "pre-registered before run" if "pre-registered before" in low
            else "correction" if any(w in low for w in ("wrong", "error", "correct", "fix"))
            else "specification / reporting")
    rows.append(((int(re.match(r"C(\d+)", cid).group(1)), cid), cid, title.replace("|", "/"), kind, re.sub(r"\s+", " ", why)[:220].replace("|", "/")))
rows.sort()
out = ["# Supplementary S1 — protocol changes: pre-registered versus changed", "",
       "Generated from PROTOCOL.md by paper/make_s1.py. Every change was committed to version control with a timestamp before",
       "the runs it governs, unless the row says otherwise. Full text and justification: PROTOCOL.md.", "",
       "| ID | change | type | reason (abridged) |", "|---|---|---|---|"]
out += [f"| {c} | {t} | {k} | {w} |" for _, c, t, k, w in rows]


def bh_stages():
    """The multiplicity family at every committed stage, read from the git history of the C96 result plus the current file.

    Section 4 promises this table: members, unadjusted cluster p and BH-adjusted p at each stage of revision.
    """
    import subprocess
    rel = "results/c96/C96_RESULT.md"
    log = subprocess.run(["git", "log", "--reverse", "--format=%h %ad", "--date=short", "--", rel], cwd=ROOT,
                         capture_output=True, text=True, encoding="utf-8").stdout.split("\n")
    versions = [(h.split()[0], h.split()[1], subprocess.run(["git", "show", f"{h.split()[0]}:{rel}"], cwd=ROOT,
                 capture_output=True, text=True, encoding="utf-8").stdout) for h in log if h.strip()]
    cur = (ROOT / rel).read_text(encoding="utf-8")
    if not versions or versions[-1][2] != cur:
        versions.append(("this submission", "final", cur))

    def family(txt):
        body = txt.split("Benjamini", 1)[1].split("## Reading", 1)[0]
        fam = {}
        for ln in body.splitlines():
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) in (3, 4) and c[0] not in ("effect", "") and not c[0].startswith("---"):
                name, n = c[0][0].upper() + c[0][1:], ""
                m_ = re.match(r"(SHOT collapse), (\d+) splits", name)
                if m_:   # the member is the SHOT split test; its cluster count grew from 2 to 10 as runs completed
                    name, n = m_.group(1) + ", splits", f" (n = {m_.group(2)})"
                fam[name] = (c[1] + n, c[2])
        return fam

    fams = [(h, d, family(t)) for h, d, t in versions]
    members = []
    for _, _, f in fams:
        members += [m for m in f if m not in members]
    head = "| member | " + " | ".join(f"stage {i + 1} ({d}, `{h}`) p / p_BH" for i, (h, d, _) in enumerate(fams)) + " |"
    lines = ["", "## Multiplicity family at each stage of revision", "",
             "Benjamini--Hochberg adjustment of the exact cluster-level sign-flip p-values, over every primary cluster-level",
             "test in the paper at that stage. Generated from the version history of `results/c96/C96_RESULT.md`; a dash",
             "means the test was not yet a member. No member was ever removed. The manuscript quotes the final stage.", "",
             head, "|" + "---|" * (len(fams) + 1)]
    for m in members:
        lines.append(f"| {m} | " + " | ".join(f"{f[m][0]} / {f[m][1]}" if m in f else "--" for _, _, f in fams) + " |")
    return lines


out += bh_stages()
(ROOT / "paper" / "supplementary_S1_changes.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(rows), "rows")
