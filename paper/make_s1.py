"""Build Supplementary S1 (what was fixed in advance and what changed) from PROTOCOL.md. Regenerate; never hand-edit S1.

S1 summarises the protocol entries that bear on the reported results; PROTOCOL.md in the archive keeps the full text,
date and reason of every entry. Every entry cited here must exist in PROTOCOL.md and must carry the status S1 gives it
(fixed before its runs, or post hoc), otherwise the build fails.
"""
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

entries = {}
for line in (ROOT / "PROTOCOL.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*\*\*(C\d+[a-z]?)\*\*\s*\|(.*)$", line)
    if m:
        entries[m.group(1)] = m.group(2).lower()

FIXED = [   # decisions committed to the protocol before the runs they govern
    ("C30", "Comb-test gate with a record-specific surrogate-order null and a two-line multiplicity rule", "Section 5"),
    ("C32", "Paired design: one source model adapted to a seen-bearing and an unseen-bearing target at the same condition, with SDALR's released code, windows and seed", "Section 4.1"),
    ("C72", "Shaft-alias-guarded comb (comb_v2)", "Section 5"),
    ("C81", "Gates inside SDALR's adaptation loop, run in the same job and from the same source checkpoint as the ungated arm", "Sections 4.4, 6.6"),
    ("C83", "Three seeds on the two mechanical folds", "Sections 4.5, 6.6"),
    ("C88", "Ten random 3/3/3 source draws from the 17 bearings, and the decision rule for the gap", "Sections 4.2, 6.2"),
    ("C90", "Slip measured on the recordings", "Supplementary S5"),
    ("C91, C92", "Random forests on the folds and on the ten splits", "Section 6.3"),
    ("C94", "The same design on a second rig (HUST), with its decision rule", "Section 6.3, S6.12"),
    ("C104", "Same-condition, bearing-disjoint control without adaptation, with its decision rule", "Section 6.3"),
    ("C113", "Corrected SHOT implementation on the ten splits", "Section 6.3"),
    ("C110, C111, C112", "Exploratory follow-ups: source-diversity curve, identity-probe ablations, kinematic-feature forest", "Section 6.4"),
]
CHANGED = [
    ("C117", "The protocol asked for five seeds per configuration. SDALR's released seed (2024) was adopted before the first paired run, and split-level variance replaced seed-level variance", "Section 4.5"),
    ("C85, C100, C113", "The first SHOT implementation returned pseudo-labels in the order of a shuffled loader pass. Its outputs are withdrawn, and the corrected implementation was run on the ten splits", "Section 4.3, S6.1"),
    ("C87, C93", "A planned bearing-identity remedy was withdrawn before any run, and its replacement was not run to a decision; no remedy result is reported", "Section 9"),
    ("C70", "UORED shaft speed could not be resolved from the recordings, so no UORED arm is primary", "Supplementaries S2, S3"),
    ("C103, C103b", "The explanation of the accuracy difference between two jobs was revised from the retained logs and code", "Section 4.6"),
    ("C118-C121, C123", "Reporting corrections made before submission (wording, interval labels, citations, code-line evidence); no new run and no changed result", "Supplementary S6"),
]
POSTHOC = [  # analyses added after results were seen; all descriptive
    ("C56", "Physical bearing as the statistical unit for real-data intervals", "Supplementary S6"),
    ("C95", "Which bearings the gates can act on", "Section 6.6"),
    ("C96", "Cluster-level inference and the Benjamini-Hochberg family (S1.4)", "Section 4.5, S6"),
    ("C97", "Identity probe on handcrafted statistics", "Section 6.4"),
    ("C98", "In-loop gate coverage and its association with the gain", "Section 6.6"),
    ("C99", "Off-rig calibration of the gate operating point", "Section 6.6"),
    ("C102", "Repeated executions of one configuration (A/A floor)", "Section 4.6"),
    ("C104b", "Per-class breakdown of the same-condition control", "Section 6.3"),
    ("C105", "Source-only arm", "Section 6.2"),
    ("C106", "Within-bearing seen-versus-unseen contrast", "Section 6.2"),
    ("C107", "Gate gain by window group", "Section 6.6"),
    ("C108", "Block labelling on seen and unseen bearings", "Section 6.4"),
    ("C109, C115", "Order-statistic intervals for every reported median; leave-one-bearing-out check", "Sections 4.5, 6.2; S6.11"),
    ("C114", "Labels given to seen and unseen bearings; KI04/KI14 sensitivity", "Section 6.4, S6.10"),
    ("C116", "Gate override and gain by certifiable bearings", "Section 6.6"),
    ("C122", "Outer-race composition of the two targets", "Section 6.2, S6.11"),
]


def ids(cell):
    out = []
    for part in cell.split(", "):
        a = re.match(r"C(\d+)-C(\d+)$", part)
        out += [f"C{i}" for i in range(int(a.group(1)), int(a.group(2)) + 1)] if a else [part]
    return out


for table, must in ((FIXED, ("pre-registered",)), (CHANGED, ()), (POSTHOC, ("post-hoc",))):
    for cell, _, _ in table:
        for cid in ids(cell):
            assert cid in entries, f"{cid} is not in PROTOCOL.md"
            assert not must or any(w in entries[cid] for w in must), f"{cid}: protocol entry does not state {must}"

release = json.loads((ROOT / "paper" / "release.json").read_text(encoding="utf-8"))
row = lambda t: [f"| {a} | {b}. | {c} |" for a, b, c in t]
out = ["# Supplementary S1 — protocol: what was fixed in advance and what changed", "",
       "The study followed a dated, version-controlled protocol, PROTOCOL.md, archived with the code and results "
       f"(release {release['version']}, https://doi.org/{release['doi']}). An entry is called pre-specified when it was "
       "committed before the runs it governs; the study was not registered with an external registry (main text, "
       "Section 4.6). This supplement summarises the entries that bear on the reported results; PROTOCOL.md gives the "
       "full text, date and reason of every entry, including implementation details not listed here.", "",
       "## S1.1 Fixed before the corresponding runs", "", "| Entry | What was fixed | Reported in |", "|---|---|---|",
       *row(FIXED), "",
       "## S1.2 Departures, withdrawals and corrections", "", "| Entry | What changed | Reported in |", "|---|---|---|",
       *row(CHANGED), "",
       "## S1.3 Analyses added after results were seen", "",
       "These analyses are post hoc and descriptive; none has a decision rule.", "",
       "| Entry | Analysis | Reported in |", "|---|---|---|", *row(POSTHOC)]


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
    lines = ["", "## S1.4 Multiplicity family at each stage of revision", "",
             "Benjamini--Hochberg adjustment of the exact cluster-level sign-flip p-values, over every primary cluster-level",
             "test in the paper at that stage. Generated from the version history of `results/c96/C96_RESULT.md`; a dash",
             "means the test was not yet a member. The historical family is retained unchanged, including the withdrawn SHOT test (S6). Its inclusion preserves the audit trail, not valid SHOT evidence. All p-values are nominal and do not establish population-level error control.", "",
             head, "|" + "---|" * (len(fams) + 1)]
    for m in members:
        lines.append(f"| {m} | " + " | ".join(f"{f[m][0]} / {f[m][1]}" if m in f else "--" for _, _, f in fams) + " |")
    return lines


out += bh_stages()
(ROOT / "paper" / "supplementary_S1_changes.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(len(FIXED) + len(CHANGED) + len(POSTHOC), "rows")
