"""Generate every LaTeX table in paper/tex/tables/ from retained artifacts. Never hand-edit the output.

Re-running this script must reproduce the submitted tables exactly (verification: git diff --exit-code paper/tex/tables).
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "tex" / "tables"
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as E  # noqa: E402
import c94_eval as H  # noqa: E402
import paired_gating as P  # noqa: E402

TASKS = E.TASKS
OTHER = {"A": "B", "B": "A"}
BS = "\\\\"


def wrap(body, caption, label, spec, header, small=False):
    """One caption of at most three sentences, below the table, and no separate note.

    small=True for wide tables: \\small plus tighter column separation keeps them inside the text width. Both are set
    inside a group closed before the caption, so every caption has the same size."""
    out = ["\\begin{table}[htbp]", "\\centering", "\\begingroup"]
    if small:
        out += ["\\small", "\\setlength{\\tabcolsep}{4pt}"]
    out += ["\\begin{tabular}{" + spec + "}", "\\toprule", header, "\\midrule", body.rstrip(), "\\bottomrule",
            "\\end{tabular}\\par", "\\endgroup", "\\caption{" + caption + "}", "\\label{tab:" + label + "}",
            "\\end{table}"]
    return "\n".join(out) + "\n"


def t1_datasets():
    rows = [
        "Paderborn (PU) \\cite{lessmeier2016} & 6 healthy, 5 outer, 6 inner (real) & 64 & 4 & 4 (3 adapt.) & adaptation, gating, slip",
        "HUST bearing \\cite{thuan2023hust} & 5 types $\\times$ \\{healthy, inner, outer\\} & 51.2 & 10 & 3 loads & second-rig replication",
        "CWRU \\cite{cwrubdc,smith2015} & 6205 drive end, 6203 fan end & 12 / 48 & 5--10 & 4 loads & slip, contamination",
        "UORED-VAFCLS \\cite{sehri2023uored} & 20 bearings, natural faults & 42 & 10 & 1 speed & gate assessment",
        "JNU \\cite{li2013jnu} & as published & 50 & 20 & 3 speeds & reproduction only",
    ]
    return wrap("\n".join(r + " " + BS for r in rows),
                "Datasets and their roles. Each row gives one dataset, the bearings and recordings used from it and its role in this study. "
                "Paderborn has four operating conditions, of which the three at 1500~rpm are used for adaptation. CWRU "
                "fault recordings are sampled at 12~kHz and the four normal baselines used for off-rig calibration at "
                "48~kHz.",
                "datasets", "l>{\\raggedright\\arraybackslash}p{3.85cm}lrrl",
                "Dataset & Bearings used & $f_s$ (kHz) & Record (s) & Conditions & Role " + BS, small=True)


def t2_splits():
    k10 = yaml.safe_load((ROOT / "configs" / "splits_k10.yaml").read_text(encoding="utf-8"))["splits"]
    m1 = yaml.safe_load((ROOT / "configs" / "splits.yaml").read_text(encoding="utf-8"))["pu"]
    rows = [("fold A", [m1[g]["A"] for g in ("healthy", "real_outer", "real_inner")]),
            ("fold B", [m1[g]["B"] for g in ("healthy", "real_outer", "real_inner")])]
    body = [f"{n} & " + " & ".join(", ".join(c) for c in cols) + " " + BS for n, cols in rows] + ["\\midrule"]
    for sid, d in k10.items():
        s = d["source"]
        body.append(f"{sid} & " + " & ".join(", ".join(s[c]) for c in ("normal", "outer_race", "inner_race")) + " " + BS)
    return wrap("\n".join(body), "Paderborn bearing splits. Each row lists the source bearings of one Paderborn split. The clean target of a split "
                "is the rest of the real-damage pool of 6 healthy, 5 outer-race and 6 inner-race bearings, and the leaky "
                "target is the source bearings at the target condition. Fold~B has two outer-race source bearings because "
                "the pool holds five.",
                "splits", "llll",
                "Split & Healthy & Outer race & Inner race " + BS, small=True)


def pu_rows():
    R = E.load()
    rows = []
    for s in E.SPLITS:
        k = [(s, s, "none"), (s, s + "c", "none"), (s, s + "c", "pcv"), (s, s + "c", "oracle")]
        if all(x in R for x in k):
            rows.append((s, *[R[x].mean() for x in k], None))
    rows += [(n.replace("M1 fold ", "fold "), *v) for n, *v in E.m1_rows()]
    return rows


def t3_collapse():
    rows = pu_rows()
    c105 = json.load(open(ROOT / "results" / "c105" / "c105_source_only.json", encoding="utf-8"))
    pre = {r["split"]: r["pre_delta"] for r in c105["sdalr_ten_splits"]["rows"] + c105["sdalr_folds_fold_job"]}
    body = []
    for name, lk, cl, pc, orc, ref in rows:
        if name == "fold A":
            body.append("\\midrule")
        if ref is not None:                 # a fold: one row per job, so no number is read across the two jobs
            body.append(f"{name}, fold job & {lk:.1f} & {cl:.1f} & {lk - cl:.1f} & {pre[name]:.1f} & -- & -- & -- & -- "
                        + BS)
            body.append(f"{name}, gating job & -- & {ref:.1f} & -- & -- & {pc:.1f} & {pc - ref:+.1f} & {orc:.1f} & -- "
                        + BS)
            continue
        body.append(f"{name} & {lk:.1f} & {cl:.1f} & {lk - cl:.1f} & {pre[name]:.1f} & {pc:.1f} & {pc - cl:+.1f} & "
                    f"{orc:.1f} & {100 * (orc - cl) / (lk - cl):.0f} " + BS)
    return wrap("\n".join(body),
                "SDALR accuracy on seen-bearing and unseen-bearing targets. Each row gives the accuracy (\\%) of SDALR on the "
                "leaky and bearing-disjoint (clean) targets of one "
                "Paderborn split, as the mean over its six condition pairs. Source-only $\\Delta$ is the same gap for the "
                "source model before adaptation, Gated and Oracle are the clean target with the envelope threshold gate and "
                "with the oracle pseudo-label filter, Gain is Gated minus Clean, and Recov.\\ is the share of "
                "$\\Delta_{\\mathrm{leak}}$ that the oracle recovers. Each fold has one row per job, because its two jobs "
                "trained different source checkpoints (Section~\\ref{sec:protocol}).", "collapse", "lrrrrrrrr",
                "Split & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ & Source-only $\\Delta$ & Gated & Gain & Oracle & "
                "Recov.\\ (\\%) " + BS, small=True)


def t4_methods():
    def vec(pat):
        hits = glob.glob(str(E.A / pat), recursive=True)
        d = json.load(open(hits[0], encoding="utf-8"))
        return np.array([d["adapted"][t] for t in TASKS])

    def pair(variant):
        lk = np.concatenate([vec(f"physgate-{'shot' if variant == 'shot' else 'm1'}-f{f.lower()}/**/"
                                 f"result_PU_M1_{variant}_F{f}to{f}_s2024.json") for f in "AB"])
        cl = np.concatenate([vec(f"physgate-{'shot' if variant == 'shot' else 'm1'}-f{f.lower()}/**/"
                                 f"result_PU_M1_{variant}_F{f}to{OTHER[f]}_s2024.json") for f in "AB"])
        return lk, cl
    rows = []
    for variant, name in (("as_released", "SDALR, as released (target-label checkpoint)"),
                          ("final_checkpoint", "SDALR, final checkpoint")):
        lk, cl = pair(variant)
        rows.append(f"{name} & {lk.mean():.1f} & {cl.mean():.1f} & {lk.mean() - cl.mean():.1f} " + BS)
    rows.append("\\midrule")
    rf = json.load(open(glob.glob(str(E.A / "physgate-c91-shallow-cpu" / "**" / "c91_result.json"),
                                 recursive=True)[0], encoding="utf-8"))
    for key, label in (("T", "Random forest, 10 time statistics"), ("F", "Random forest, 64 spectral bands"),
                       ("E", "Random forest, envelope spectrum"), ("TFE", "Random forest, all three feature sets")):
        b = rf[key]
        rows.append(f"{label} & {b['leaky_mean']:.1f} & {b['clean_mean']:.1f} & {b['delta']:.1f} " + BS)
    split_rows = t4_split_rows()
    assert sum(r != "\\midrule" for r in rows) == 6 and len(split_rows) == 7, "the caption names six and seven rows"
    rows += ["\\midrule"] + split_rows
    return wrap("\n".join(rows),
                "Adapted and non-adaptive methods on the same splits. Each row gives the mean accuracy (\\%) of one method on "
                "the leaky and bearing-disjoint (clean) Paderborn "
                "targets, over the 12 tasks of the two mechanical folds in the first six rows and over the ten random "
                "splits in the last seven. The random forests use no adaptation and no target data. The kinematic forest "
                "classifies full recordings, whose classes are not balanced, and is therefore given in ordinary and in "
                "balanced accuracy.", "methods", "lrrr",
                "Method & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ " + BS)


def t4_split_rows():
    """Split-level rows for the same non-SDALR methods, where they exist: these carry the inference."""
    rows = []
    rf = ROOT / "results" / "c101" / "c101_rf_splits.json"
    if rf.exists():
        d = json.load(open(rf, encoding="utf-8"))
        for fs, label in (("T", "Random forest, 10 time statistics, ten splits"),
                          ("TFE", "Random forest, all three feature sets, ten splits")):
            if fs in d:
                r = d[fs]["rows"]
                lk = np.mean([r[s]["leaky"] for s in d[fs]["splits"]])
                cl = np.mean([r[s]["clean"] for s in d[fs]["splits"]])
                rows.append(f"{label} & {lk:.1f} & {cl:.1f} & {lk - cl:.1f} " + BS)
        rf_bh = max(bh_of("RF (10 time"), bh_of("RF (time"))
    c105 = json.load(open(ROOT / "results" / "c105" / "c105_source_only.json", encoding="utf-8"))["sdalr_ten_splits"]
    s5 = c105["summary"]
    rows.insert(0, f"Source model only (before adaptation), ten splits & {s5['mean_pre_leaky']:.1f} & "
                   f"{s5['mean_pre_clean']:.1f} & {s5['mean_pre_leaky'] - s5['mean_pre_clean']:.1f} " + BS)
    pu = pu_rows()[:10]                                         # SDALR final checkpoint on the same ten splits (C88)
    assert [r[0] for r in pu] == [f"S{i:02d}" for i in range(10)]
    slk, scl = np.mean([r[1] for r in pu]), np.mean([r[2] for r in pu])
    rows.insert(1, f"SDALR, final checkpoint, ten splits & {slk:.1f} & {scl:.1f} & {slk - scl:.1f} " + BS)
    c113 = ROOT / "results" / "c113" / "c113_shot_splits.json"   # corrected SHOT (patch v2); the C100 run is withdrawn
    if c113.exists():
        d13 = json.load(open(c113, encoding="utf-8"))
        assert len(d13["splits"]) == 10 and not d13["missing"], "C113 incomplete: not all ten splits have both arms"
        rows.insert(2, f"SHOT (corrected implementation), ten splits & {d13['leaky_mean']:.1f} & "
                       f"{d13['clean_mean']:.1f} & {d13['leaky_mean'] - d13['clean_mean']:.1f} " + BS)
    kin = json.load(open(ROOT / "results" / "c112" / "c112_result.json", encoding="utf-8"))
    ks = [f"S{i:02d}" for i in range(10)]
    klk = np.mean([kin["per_split"][x]["leaky"] for x in ks])
    kcl = np.mean([kin["per_split"][x]["clean"] for x in ks])
    rows.append(f"Random forest, kinematic features, ordinary accuracy & {klk:.1f} & {kcl:.1f} & "
                f"{klk - kcl:.1f} " + BS)
    corrected = json.load(open(ROOT / "results/reporting_2026_10_09/reporting_corrections.json", encoding="utf-8"))["kinematic_balanced"]
    rows.append(f"Kinematic forest, balanced accuracy (sensitivity) & {corrected['mean_leaky']:.1f} & "
                f"{corrected['mean_clean']:.1f} & {corrected['mean_leaky'] - corrected['mean_clean']:.1f} " + BS)
    return rows


def bh_of(prefix: str, key: str = "bh") -> float:
    """BH-adjusted cluster p-value of one member of the C96 family (results/c96/c96_family.json)."""
    fam = json.load(open(ROOT / "results" / "c96" / "c96_family.json", encoding="utf-8"))["family"]
    hits = [m[key] for m in fam if m["effect"].startswith(prefix)]
    assert len(hits) == 1, f"BH family member {prefix!r}: {len(hits)} matches"
    return hits[0]


def t5_gates():
    roc = json.load(open(ROOT / "results/roc/roc_pu.json", encoding="utf-8"))
    fa = json.load(open(ROOT / "results/reporting_2026_10_09/reporting_corrections.json", encoding="utf-8"))["healthy_false_acceptance"]
    labels = {"pcv": "Envelope threshold", "v2": "Alias-guarded comb", "c30": "Surrogate-null comb", "eagle": "Raw-spectrum rule"}
    names = {"pcv": "envelope threshold rule", "v2": "shaft-alias-guarded comb", "c30": "surrogate-null comb", "eagle": "raw-spectrum band rule"}
    op = {"pcv": 10, "v2": 0.05, "c30": 0.05, "eagle": 2}
    rows=[]
    for g in labels:
        pts=roc[g]; key="z" if "z" in pts[0] else "alpha"
        here=min(pts,key=lambda r:abs(r[key]-op[g]))
        counts=fa[names[g]]["per_bearing"]
        assert sum(counts.values()) == here['healthy_FA']
        by=', '.join(str(counts[f'K{i:03d}']) for i in range(1,7))
        zero=[r['correct'] for r in pts if r['healthy_FA']==0]
        rows.append(f"{labels[g]} & ${'z' if key=='z' else chr(92)+'alpha'}={op[g]:g}$ & {here['healthy_FA']}/480 & {by} & {here['correct']} & {here['wrong_family']} & {max(zero) if zero else '--'} " + BS)
    return wrap("\n".join(rows),
                "Gate verdicts at the fixed operating points. Each row gives one gate at its operating point, fixed before evaluation, on 480 healthy and 1839 faulty "
                "Paderborn recordings. Healthy FA is the number of fault verdicts on healthy recordings, also given by "
                "bearing for K001--K006 (80 recordings each), and Wrong family the number of fault verdicts that name the "
                "other fault family. At zero FA is the largest number of correct verdicts over the gate's parameter sweep "
                "with no healthy false acceptance.",
                "gates", "llrlrrr",
                "Gate & Op. point & Healthy FA & FA by bearing & Correct & Wrong family & At zero FA " + BS,
                small=True)


def t6_gains():
    R = P.load()
    seeds = sorted({k[2] for k in R if k[0] == "final_checkpoint" and k[1] == "pcv"})
    rows = []
    for g, name in (("v2", "Shaft-alias-guarded comb"), ("pcv", "Envelope threshold rule")):
        for i, s in enumerate(seeds):
            run = {f: sorted({k[5] for k in R if k[:5] == ("final_checkpoint", "v2", s, f, OTHER[f])})[0] for f in "AB"}
            base = {f: P.pick(R, "final_checkpoint", "none", s, f, OTHER[f], run[f]) for f in "AB"}
            arm = {f: P.pick(R, "final_checkpoint", g, s, f, OTHER[f], run[f]) for f in "AB"}
            d = np.concatenate([P.vec(arm[f]) - P.vec(base[f]) for f in "AB"])
            rows.append(f"{name if i == 0 else ''} & {s} & {d.mean():+.2f} & {np.median(d):+.2f} & {d.min():+.2f} & "
                        f"{d.max():+.2f} & {int((d > 0).sum())}/12 " + BS)
        rows.append("\\midrule")
    run = {f: f"physgate-m2-f{f.lower()}" for f in "AB"}     # the gating job, where the raw-spectrum arm ran
    base = {f: P.pick(R, "final_checkpoint", "none", 2024, f, OTHER[f], run[f]) for f in "AB"}
    arm = {f: P.pick(R, "final_checkpoint", "eagle", 2024, f, OTHER[f], run[f]) for f in "AB"}
    dA, dB = (P.vec(arm[f]) - P.vec(base[f]) for f in "AB")
    d = np.concatenate([dA, dB])
    rows.append(f"Raw-spectrum band rule & 2024 & {d.mean():+.2f} & {np.median(d):+.2f} & {d.min():+.2f} & "
                f"{d.max():+.2f} & {int((d > 0).sum())}/12 " + BS)
    rows.append("\\midrule")
    return wrap("\n".join(rows[:-1]),
                "Each row summarises the paired effect of one gate inside SDALR, gated minus ungated accuracy in percentage "
                "points, over the 12 bearing-disjoint tasks of the two mechanical folds at one seed. Both arms of every "
                "comparison ran in one job from the same source checkpoint. The 12 tasks share two source folds, so these "
                "summaries are descriptive.", "gains", "llrrrrr",
                "Gate & Seed & Mean & Median & Min & Max & Tasks $>0$ " + BS, small=True)


def t7_hust():
    R = {}
    for p in glob.glob(str(H.A / "**" / "result_HUST_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if len(d.get("adapted", {})) == 6:
            R[(d["src_fold"], d["tgt_fold"])] = np.array([d["adapted"][t] for t in H.TASKS])
    kl = list(H.A.rglob("kernel_log_hust.json"))
    types = {f"H{i}": s for i, s in enumerate(json.load(open(kl[0], encoding="utf-8")).get("splits", []))} if kl else {}
    rows = []
    for v in sorted({s for s, _ in R}):
        a, b = R[(v, v)].mean(), R[(v, v + "c")].mean()
        rows.append(f"{v} & {', '.join('620' + t for t in types.get(v, []))} & {a:.1f} & {b:.1f} & {a - b:.1f} " + BS)
    return wrap("\n".join(rows),
                "Each row gives the accuracy (\\%) of SDALR on one of six pre-specified type-disjoint HUST bearing splits, "
                "as the mean over its six condition pairs. The source is the three listed bearing types and the clean "
                "target the other two, at the target load. Each type has a different size, so the clean target also "
                "changes geometry.", "hust", "llrrr",
                "Split & Source bearings & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ " + BS)


def t8_bearings():
    d = json.load(open(ROOT / "results" / "c106" / "c106_within_bearing.json", encoding="utf-8"))
    rows = []
    for r in d["rows"]:
        if r["bearing"].startswith("K0"):
            continue
        mode = {"fatigue": "pitting", "plastic deformation": "indentation"}.get(r["mode"], r["mode"])
        w = r["width_mm"].replace("total", "full")
        L = r["length_mm"].replace("< ", "<").replace("<", "$<$")
        w = w.replace("< ", "<").replace("<", "$<$")
        rows.append(f"{r['bearing']} & {r['manufacturer'].replace(' ', '')} & {mode} & {r['extent']} & "
                    f"{L} $\\times$ {w} & {r['combination']} & {r['seen_acc']:.0f} & {r['unseen_acc']:.0f} & "
                    f"{r['diff']:+.0f} & "
                    f"{r['correct_fault_verdicts_adapt_conditions']['pcv']}/{r['records_adapt_conditions']} " + BS)
    h = [r for r in d["rows"] if r["bearing"].startswith("K0")]
    rows.append("\\midrule")
    rows.append(f"K001--K006 & IBU & healthy & -- & -- & -- & {np.mean([r['seen_acc'] for r in h]):.0f} & "
                f"{np.mean([r['unseen_acc'] for r in h]):.0f} & {np.mean([r['diff'] for r in h]):+.0f} & "
                f"{sum(r['fault_verdicts_adapt_conditions']['pcv'] for r in h)}/360 " + BS)
    return wrap("\n".join(rows),
                "Real-damage Paderborn bearings, seen and unseen. Each row describes one Paderborn bearing from its own datasheet and gives SDALR's accuracy (\\%) on it over "
                "the ten splits when it was in the source (Seen) and in the clean target (Unseen). Gate counts the correct "
                "fault verdicts of the envelope threshold rule at the three adaptation conditions, and false acceptances in "
                "the last row, which pools the six healthy bearings. Mfr.\\ is the "
                "manufacturer, Extent the datasheet's extent class (1--3), Size the length $\\times$ width of the first "
                "listed damage and Comb.\\ single (S), repetitive (R) or multiple (M) damage; Supplementary~S3 lists every "
                "damage.", "bearings", "llllllrrrr",
                "Bearing & Mfr. & Damage & Extent & Size (mm) & Comb. & Seen & Unseen & Diff. & Gate " + BS,
                small=True)


def t9_gate_accounting():
    d = json.load(open(ROOT / "results" / "c107" / "c107_gate_spillover.json", encoding="utf-8"))
    ov = json.load(open(ROOT / "results" / "c116" / "c116_gate_override.json", encoding="utf-8"))
    rows = []
    for r in d["rows"]:
        g = r["groups"]
        c, u, h = g["certified"], g["uncovered_faulty"], g["uncovered_healthy"]
        cert = (f"{100 * c['share']:.0f} & {c['acc_ungated']:.1f} $\\to$ {c['acc_gated']:.1f}" if c["windows"]
                else "0 & --")
        rows.append(f"{r['split']} & {cert} & {u['acc_ungated']:.1f} $\\to$ {u['acc_gated']:.1f} & "
                    f"{h['acc_ungated']:.1f} $\\to$ {h['acc_gated']:.1f} & {r['gain']:+.1f} & "
                    f"{c['contribution_pp']:+.1f} & {u['contribution_pp'] + h['contribution_pp']:+.1f} & "
                    f"{ov['rows'][r['split']]['override_gain']:+.1f} " + BS)
    return wrap("\n".join(rows),
                "Envelope-gate gain by verdict group and the gate override. Each row splits the clean-target windows of one Paderborn split by the envelope gate's verdict on their "
                "recording and gives SDALR's accuracy (\\%) on each group, ungated $\\to$ gated. Certified recordings "
                "received a fault verdict and silent ones none; Cert.\\ is the certified share of the windows, and Gain is "
                "the sum of the contributions from certified and from silent windows (group share $\\times$ change in "
                "accuracy). Override is the gain over the ungated arm when every window of a certified recording takes the "
                "gate's verdict, with adaptation unchanged.",
                "gateacc", "lrrrrrrrr",
                "Split & Cert.\\ (\\%) & Certified & Silent faulty & Silent healthy & Gain & from cert. & from silent & "
                "Override " + BS, small=True)


S6 = ROOT / "paper" / "supplementary_S6_reporting_audit.md"
S6_HEAD = "## S6.12 HUST splits and fold gate gains (moved from the main text, 30 October 2026)"


def tex_to_md(tex):
    """The header and body rows of a generated tabular as a Markdown table (same numbers, LaTeX markup removed)."""
    rows = [ln.rstrip()[:-len(BS)].strip() for ln in tex.splitlines() if ln.rstrip().endswith(BS)]
    clean = lambda c: (c.replace("$\\Delta_{\\mathrm{leak}}$", "Delta_leak").replace("$>0$", "> 0")
                       .replace("\\%", "%").replace("$", "").strip())
    cells = [[clean(c) for c in r.split("&")] for r in rows]   # no escaped & in the tables converted here
    for prev, row in zip(cells[1:], cells[2:]):
        row[0] = row[0] or prev[0]                               # a blank first cell continues the row above
    out = ["| " + " | ".join(cells[0]) + " |", "|" + "---|" * len(cells[0])]
    return "\n".join(out + ["| " + " | ".join(r) + " |" for r in cells[1:]])


def s6_moved_tables():
    """Tables 6 and 10 of the 24 October manuscript duplicated Fig. 2b and Fig. 6; their values move to S6.12."""
    text = S6.read_text(encoding="utf-8")
    text = text[:text.index(S6_HEAD)].rstrip() if S6_HEAD in text else text.rstrip()
    sec = [S6_HEAD, "",
           "Accuracy (%) of SDALR on the six pre-specified type-disjoint HUST bearing splits, as the mean over the six "
           "condition pairs of each split; the source is the three listed bearing types and the clean target the other "
           "two, at the target load. The same leaky and clean values are plotted in Fig. 2b of the main text "
           "[src: results/c94; experiments/c94_eval.py; paper/make_tables.py].", "",
           tex_to_md(t7_hust()), "",
           "Paired effect of each gate inside SDALR on the 12 bearing-disjoint tasks of the two mechanical folds, gated "
           "minus ungated accuracy in percentage points, at one seed per row; both arms of every comparison ran in one "
           "job from the same source checkpoint, and the 12 tasks share two source folds, so these summaries are "
           "descriptive. The per-task values of the two envelope-based gates are plotted in Fig. 6 of the main text "
           "[src: results/PAIRED_GATING.md; experiments/paired_gating.py; paper/make_tables.py].", "",
           tex_to_md(t6_gains()), ""]
    S6.write_text(text + "\n\n" + "\n".join(sec), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("t1_datasets", t1_datasets), ("t2_splits", t2_splits), ("t3_collapse", t3_collapse),
                     ("t4_methods", t4_methods), ("t5_gates", t5_gates), ("t8_bearings", t8_bearings), ("t9_gate_accounting", t9_gate_accounting)):
        (OUT / f"{name}.tex").write_text(fn(), encoding="utf-8")
        print("wrote", name)
    s6_moved_tables()
    print("wrote S6.12 (HUST splits and fold gate gains)")


if __name__ == "__main__":
    main()
