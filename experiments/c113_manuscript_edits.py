"""C113: write the corrected-SHOT numbers into the manuscript once results/c113/c113_shot_splits.json exists.

Reads only retained result files (C113 evaluation and the C105 source-only re-run with its shot2 block). Every
sentence it inserts is built from those numbers; wording branches on the pre-registered rule outcome. Each anchor must
match exactly once; nothing is written if any anchor fails. Run after experiments/c113_shot_splits.py and
experiments/c105_source_only.py, before paper/make_tables.py and the PDF build.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "paper" / "tex" / "sections"
sys.path.insert(0, str(ROOT / "experiments"))
from rev6_load import boot_median_ci  # noqa: E402

c113 = json.loads((ROOT / "results/c113/c113_shot_splits.json").read_text(encoding="utf-8"))
c105 = json.loads((ROOT / "results/c105/c105_source_only.json").read_text(encoding="utf-8"))
if c113["missing"] or len(c113["splits"]) != 10 or "shot2_ten_splits" not in c105:
    sys.exit("C113 incomplete or C105 not re-run with the shot2 block")

rows = c113["rows"]
deltas = np.array([rows[s]["leaky"] - rows[s]["clean"] for s in c113["splits"]])
med = float(np.median(deltas))
lo, hi = boot_median_ci(deltas)
pos = int((deltas > 0).sum())
passed = c113["decision"] == "GENERALISES"
s2 = c105["shot2_ten_splits"]["summary"]
amp_rows = c105["shot2_ten_splits"]["rows"]
amp = np.array([r["amplification"] for r in amp_rows])
cg = np.array([r["clean_adapt_gain"] for r in amp_rows])
lg = np.array([r["leaky_adapt_gain"] for r in amp_rows])
sd = c105["sdalr_ten_splits"]["rows"]
sdalr_clean = np.array([r["adapted_clean"] for r in sd])
shot_clean = np.array([r["adapted_clean"] for r in amp_rows])
clean_diff = shot_clean - sdalr_clean          # SHOT minus SDALR on bearing-disjoint targets, per split

f = lambda x: f"{x:.1f}"
rule = ("meeting the pre-specified rule (median at least 10 points, sign-flip $p<0.05$)" if passed
        else "not meeting the pre-specified rule (median at least 10 points, sign-flip $p<0.05$)")
amp_word = "raises" if float(np.median(amp)) > 0 else "lowers"
cg_word = "raises" if float(np.median(cg)) > 0 else "lowers"
cmp_word = "higher" if float(np.median(clean_diff)) > 0 else "lower"

texts = {}


def rep(path, old, new):
    p = Path(path)
    s = texts.get(p) or p.read_text(encoding="utf-8")
    if new in s:
        texts[p] = s
        return
    if s.count(old) != 1:
        sys.exit(f"ANCHOR {s.count(old)}x in {p.name}: {old[:80]!r}")
    texts[p] = s.replace(old, new)


# 3 data: byte-identical Paderborn recordings (experiments/c113_dedup_check.py)
dd = json.loads((ROOT / "results/c113/c113_dedup_check.json").read_text(encoding="utf-8"))
dd_shift = abs(dd["full"]["median"] - dd["dedup"]["median"])
rep(S / "03_data.tex",
    "(N15\\_M01\\_F10), A2 (N15\\_M07\\_F04) and A3 (N15\\_M07\\_F10); the fourth condition (N09, \\SI{900}{rpm}, \\SI{15}{Hz}) enters\nonly the gate analyses.",
    "(N15\\_M01\\_F10), A2 (N15\\_M07\\_F04) and A3 (N15\\_M07\\_F10); the fourth condition (N09, \\SI{900}{rpm}, \\SI{15}{Hz}) enters\nonly the gate analyses. "
    "In the distributed files, five A2 recordings of bearing KA04 carry byte-identical vibration signals in two groups (recordings 5 and 19; 6, 15 and 20). "
    f"All copies belong to one bearing and so stay on one side of every split; scoring each identical window once changes the median SHOT loss by {dd_shift:.2f} points.")

# 4.3 adaptation variants
rep(S / "04_protocol.tex",
    "A planned SHOT comparison is not reported: a source-code audit found that its local implementation did not restore pseudo-label order after a shuffled loader pass, so its outputs do not measure SHOT, and no corrected experiment was run (Supplementary~S6).",
    "A first SHOT implementation returned pseudo-labels in the order of a shuffled loader pass rather than in dataset order, an indexing defect found by code audit; its outputs are retained for audit only (Supplementary~S6). Every SHOT result reported here comes from the corrected implementation, whose pseudo-label alignment is checked by a unit test, run on the ten splits from the same source checkpoints as SDALR.")

# 6.3 second method
rep(S / "06_results.tex",
    "Table~\\ref{tab:methods} places SDALR beside non-adaptive controls under the same bearing splits. No second SFDA method is reported (Section~\\ref{sec:protocol}); method-generality claims are restricted accordingly.",
    "Table~\\ref{tab:methods} places SDALR beside SHOT and non-adaptive controls under the same bearing splits.\n\n"
    f"\\textbf{{SHOT.}} Run from the same source checkpoints, SHOT loses a median {f(med)} points on bearing-disjoint targets "
    f"(conditional CI {f(lo)}--{f(hi)}; positive in {pos} of 10 splits), {rule}. Its source-only gap is the 35.1 points of the shared "
    f"source model; adaptation {amp_word} the gap by a median {f(abs(float(np.median(amp))))} points and {cg_word} clean accuracy by a median "
    f"{f(abs(float(np.median(cg))))} points (leaky accuracy changes by a median {f(float(np.median(lg)))}). On bearing-disjoint targets SHOT is "
    f"{cmp_word} than SDALR by a median {f(abs(float(np.median(clean_diff))))} points ({int((clean_diff > 0).sum())} of 10 splits higher). "
    "SHOT is SDALR's own base rather than an independent family, so the two do not establish method generality.")

# 2 positioning table caption
rep(S / "02_background.tex",
    "The present SFDA evidence is limited to SDALR.",
    "The present SFDA evidence is limited to SDALR and SHOT.")

# 7 discussion
rep(S / "07_discussion.tex",
    "This does not establish the behaviour of other SFDA algorithms. A source-only comparison is therefore necessary beside any adapted result.",
    f"SHOT, run from the same checkpoints, loses a median {f(med)} points on the same splits, so the loss is not specific to SDALR's "
    "reliability mechanism; other SFDA families remain untested. A source-only comparison is therefore necessary beside any adapted result.")

# 9 limitations
rep(S / "09_limitations.tex",
    "Only one SFDA method supplies valid adaptation evidence. The planned SHOT comparison is not reported because an indexing defect was found in its local implementation (Supplementary~S6), and no corrected run was performed. SHOT \\cite{liang2020shot}, NRC \\cite{yang2021nrc} and AaD \\cite{yang2022aad} therefore require valid evaluation before any method-general conclusion.",
    "Two SFDA methods supply adaptation evidence, and SHOT \\cite{liang2020shot} is SDALR's own base, so they are not independent families; NRC \\cite{yang2021nrc} and AaD \\cite{yang2022aad} require evaluation before any method-general conclusion. The first SHOT implementation had an indexing defect (Supplementary~S6); only the corrected run is reported.")

# 10 conclusions
rep(S / "10_conclusions.tex",
    "SDALR's high same-bearing accuracy does not carry over to unseen physical bearings under the tested protocol. On Paderborn, the median loss is 36.2 points across ten pre-specified splits;",
    f"SDALR's high same-bearing accuracy does not carry over to unseen physical bearings under the tested protocol. On Paderborn, the median loss is 36.2 points across ten pre-specified splits, and {f(med)} points for SHOT on the same splits;")
rep(S / "10_conclusions.tex",
    "The indexing defect found in our local SHOT implementation illustrates the need for those checks; the present SFDA conclusions are limited to SDALR.",
    "The indexing defect found and corrected in our own SHOT implementation illustrates the need for those checks; the SFDA conclusions are limited to SDALR and SHOT.")

# abstract
rep(S / "00_abstract.tex",
    "We re-evaluate source-free domain adaptation based on label reliability (SDALR) on Paderborn in a paired design:",
    "We re-evaluate source-free domain adaptation based on label reliability (SDALR) and SHOT on Paderborn in a paired design:")
rep(S / "00_abstract.tex",
    "The gap is already present before adaptation (35.1 points) and remains substantial afterwards.",
    f"The gap is already present before adaptation (35.1 points) and remains substantial afterwards; SHOT loses a median {f(med)} points on the same splits.")

# declarations: code availability
rep(S / "99_declarations.tex",
    "The local SHOT implementation is retained for audit only; its indexing defect is documented in Supplementary~S6 and its outputs are not used.",
    "SHOT runs from our implementation of its objective on the same backbone (runners/shot\\_patch.py, version 2); the first version, whose indexing defect is documented in Supplementary~S6, is retained for audit only and its outputs are not used.")

# highlights (main.tex, separate file generated from this block)
rep(ROOT / "paper/tex/main.tex",
    "\\item Unseen bearings reduce SDALR accuracy by a median 36 percentage points.",
    f"\\item Unseen bearings cost SDALR 36 and SHOT {med:.0f} points, median over ten splits.")

# cover letter (the DOCX is regenerated from this file)
import datetime as _dt
cl = ROOT / "paper/cover_letter.md"
t = cl.read_text(encoding="utf-8")
for old, new in (
    ("17 October 2026", _dt.date.today().strftime("%d %B %Y").lstrip("0")),
    ('"Bearing-disjoint evaluation of source-free fault diagnosis: an SDALR case study with physics-gated pseudo-labels"',
     '"Bearing-disjoint evaluation of source-free bearing fault diagnosis: the unseen-bearing loss, its source-model origin and the limits of physics-gated pseudo-labels"'),
    ("to a paired SDALR/source-only study", "to a paired study of two source-free methods, SDALR and SHOT, with a source-only arm"),
    ("Across ten Paderborn source-set draws, SDALR's median leaky-to-bearing-disjoint accuracy gap is 36.2 percentage points.",
     f"Across ten Paderborn source-set draws, SDALR's median leaky-to-bearing-disjoint accuracy gap is 36.2 percentage points and SHOT's is {med:.1f}."),
    ("The adaptation evidence concerns SDALR; the scope of that conclusion is stated in the methods and limitations.",
     "The adaptation evidence concerns SDALR and SHOT, which is SDALR's own base; the scope of that conclusion is stated in the methods and limitations."),
    ("six supplements and a reproducibility package", "seven supplements and a reproducibility package"),
):
    if new in t:
        continue
    if t.count(old) != 1:
        sys.exit(f"cover letter anchor: {old[:60]!r}")
    t = t.replace(old, new)
texts[cl] = t

# S6.1 and the audit record
s6 = ROOT / "paper/supplementary_S6_reporting_audit.md"
t6 = s6.read_text(encoding="utf-8")
old6 = "This is a static code finding, not a corrected performance estimate. Results in C85 and C100 and their source-only/SHOT interpretations cannot establish SHOT performance or agreement across two SFDA methods. They have been removed from the main performance table, title, abstract and conclusions. Original code and outputs remain in the experimental archive for audit. No corrected run is available. The manuscript now evaluates SDALR with non-adaptive controls; generalisation to other SFDA methods is untested."
new6 = ("This is a static code finding. Results in C85 and C100 cannot establish SHOT performance; their code and outputs remain in the experimental archive for audit only. "
        f"The defect was corrected on 22 October 2026 (shot_patch v2, PROTOCOL C113: pseudo-labels scattered into dataset order, loader pass checked, unit-tested) and SHOT was re-run on the ten splits from the same source checkpoints (kernels physgate-shot2-k10-g1 to g4). Corrected result: median split-level loss {f(med)} pp (conditional CI {f(lo)}--{f(hi)}), positive in {pos} of 10; nominal one-sided sign-flip p = {c113['p']:.4f}; pre-registered rule {'met' if passed else 'not met'}. The manuscript reports only the corrected run.")
if old6 not in t6 and new6 not in t6:
    sys.exit("S6.1 anchor")
texts[s6] = t6.replace(old6, new6)
rc = ROOT / "results/reporting_2026_10_09/reporting_corrections.json"
d = json.loads(rc.read_text(encoding="utf-8"))
d["shot_status"] = {"status": "CORRECTED (C113, 2026-10-22)", "withdrawn_run": "C100 (patch v1): obtain_label returned shuffled-loader order; audit only",
                    "corrected_run": {"kernels": "physgate-shot2-k10-g1..g4", "median_delta_pp": med, "ci_median": [lo, hi], "positive": pos, "p": c113["p"],
                                      "decision": c113["decision"]}}
texts[rc] = json.dumps(d, indent=2) + "\n"

for p, t in texts.items():
    p.write_text(t, encoding="utf-8")
print(f"C113 edits written: median {med:.1f} [{lo:.1f}, {hi:.1f}], {pos}/10, decision {c113['decision']}; files: {len(texts)}")
