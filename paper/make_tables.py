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
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "tex" / "tables"
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as E  # noqa: E402
import c94_eval as H  # noqa: E402
import paired_gating as P  # noqa: E402

TASKS = E.TASKS
OTHER = {"A": "B", "B": "A"}
BS = "\\\\"


def wrap(body, caption, label, spec, header, note="", small=False):
    """small=True for wide tables: \\small plus tighter column separation keeps them inside the text width."""
    out = ["\\begin{table}[htbp]", "\\centering", "\\caption{" + caption + "}", "\\label{tab:" + label + "}"]
    if small:
        out += ["\\small", "\\setlength{\\tabcolsep}{4pt}"]
    out += ["\\begin{tabular}{" + spec + "}", "\\toprule", header, "\\midrule", body.rstrip(), "\\bottomrule",
            "\\end{tabular}"]
    if note:
        out.append("\\begin{minipage}{\\linewidth}\\vspace{2pt}\\footnotesize " + note + "\\end{minipage}")
    out.append("\\end{table}")
    return "\n".join(out) + "\n"


def t1_datasets():
    rows = [
        "Paderborn (PU) \\cite{lessmeier2016} & 6 healthy, 5 outer, 6 inner (real) & 64 & 4 & 4 (3 adapt.) & adaptation, gating, slip",
        "HUST bearing \\cite{thuan2023hust} & 5 types $\\times$ \\{healthy, inner, outer\\} & 51.2 & 10 & 3 loads & second-rig replication",
        "CWRU \\cite{cwrubdc,smith2015} & 6205 drive end, 6203 fan end & 12 / 48$^{a}$ & 5--10 & 4 loads & slip, contamination",
        "UORED-VAFCLS \\cite{sehri2023uored} & 20 bearings, natural faults & 42 & 10 & 1 speed & gate assessment",
        "JNU \\cite{li2013jnu} & as published & 50 & 20 & 3 speeds & reproduction only",
    ]
    return wrap("\n".join(r + " " + BS for r in rows),
                "Test rigs and recordings used in this study. Bearings are physical bearings, not fault classes.",
                "datasets", "lp{3.85cm}lrrl",
                "Dataset & Bearings used & $f_s$ (kHz) & Record (s) & Conditions & Role " + BS,
                "$^{a}$ Fault recordings 12~kHz; the four normal baselines used for off-rig calibration 48~kHz. Paderborn: "
                "three conditions at 1500~rpm (25~Hz) for adaptation, all four for the gate and slip analyses. JNU: the "
                "three nominal speeds of the distributed data, as used by SDALR.", small=True)


def t2_splits():
    k10 = yaml.safe_load((ROOT / "configs" / "splits_k10.yaml").read_text(encoding="utf-8"))["splits"]
    m1 = yaml.safe_load((ROOT / "configs" / "splits.yaml").read_text(encoding="utf-8"))["pu"]
    rows = [("fold A", [m1[g]["A"] for g in ("healthy", "real_outer", "real_inner")]),
            ("fold B", [m1[g]["B"] for g in ("healthy", "real_outer", "real_inner")])]
    body = [f"{n} & " + " & ".join(", ".join(c) for c in cols) + " " + BS for n, cols in rows] + ["\\midrule"]
    for sid, d in k10.items():
        s = d["source"]
        body.append(f"{sid} & " + " & ".join(", ".join(s[c]) for c in ("normal", "outer_race", "inner_race")) + " " + BS)
    note = ("The clean target of each row is the complement within the real-damage pool (6 healthy, 5 outer-race, "
            "6 inner-race); the leaky target is the same bearings at the target operating condition. S00--S09 were drawn "
            "uniformly without replacement from the 4{,}000 possible 3/3/3 draws with a seed fixed before any run.")
    return wrap("\n".join(body), "Source bearing sets on Paderborn. The two mechanical folds are not symmetric: fold~B "
                "has two outer-race source bearings (KA22, KA30), not three, because the real-damage pool holds five.",
                "splits", "llll",
                "Split & Healthy & Outer race & Inner race " + BS, note, small=True)


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
    ci = json.load(open(ROOT / "results" / "c109" / "c109_intervals.json", encoding="utf-8"))["effects"]
    REF = E.m1_gating_reference()
    body = []
    for name, lk, cl, pc, orc, ref in rows:
        b = cl if ref is None else ref      # a fold's gated/oracle arms pair against the gating job's own clean arm
        if name == "fold A":
            body.append("\\midrule")
        rec = f"{100 * (orc - b) / (lk - b):.0f}" if ref is None else "--"
        body.append(f"{name} & {lk:.1f} & {cl:.1f} & {lk - cl:.1f} & {pre[name]:.1f} & {pc:.1f} & {pc - b:+.1f} & "
                    f"{orc:.1f} & {rec} " + BS)
    a = np.array([r[1:5] for r in rows[:10]], dtype=float)
    d, g = a[:, 0] - a[:, 1], a[:, 2] - a[:, 1]
    pL = wilcoxon(a[:, 0], a[:, 1], alternative="greater").pvalue
    pG = wilcoxon(a[:, 2], a[:, 1], alternative="greater", zero_method="zsplit").pvalue
    fold_clean = np.array([r[2] for r in rows if r[0] in ("fold A", "fold B")], dtype=float)
    sp = c105["sdalr_ten_splits"]["summary"]
    cd, cg, cr = (ci[k]["ci95_median"] for k in ("sdalr_collapse_ten_splits", "envelope_gate_gain_ten_splits",
                                                "recoverable_share_pct_ten_splits"))
    note = (f"Medians over the ten random splits, with conditional split-cluster bootstrap 95\\,\\% intervals: "
            f"$\\Delta_{{\\mathrm{{leak}}}}$ {np.median(d):.1f}~pp [{cd[0]:.1f}, {cd[1]:.1f}] (range {d.min():.1f}--"
            f"{d.max():.1f}, 10/10); source-only $\\Delta$, before any adaptation step, "
            f"{sp['median_pre_delta']:.1f}~pp [{sp['ci_pre_delta'][0]:.1f}, {sp['ci_pre_delta'][1]:.1f}]; gate gain "
            f"{np.median(g):+.1f}~pp [{cg[0]:.1f}, {cg[1]:.1f}] (positive in {int((g > 0).sum())}/10); "
            f"recoverable share {100 * np.median((a[:, 3] - a[:, 1]) / d):.0f}\\,\\% [{cr[0]:.0f}, {cr[1]:.0f}]. Below the "
            f"rule, the two mechanical folds: leaky, clean and source-only columns from the fold job; gated and oracle "
            f"from the gating job, with the gain taken against that job's own ungated clean arm ({REF['A']:.1f} and "
            f"{REF['B']:.1f}\\,\\%). The two jobs trained different source checkpoints (Section~\\ref{{sec:protocol}}) and "
            f"the gating job has no leaky arm, so no recoverable share is given for the folds. A share above 100\\,\\% "
            f"(S04) means the oracle arm beats the leaky arm. Differences are computed before rounding.")
    return wrap("\n".join(body),
                "Paderborn: accuracy (\\%) of SDALR (final checkpoint, seed 2024) on leaky and bearing-disjoint (clean) "
                "targets, the same gap for the source model before adaptation, and the clean target with the envelope "
                "threshold gate and with the oracle pseudo-label filter. Each entry is the mean over the six condition "
                "pairs of that split.", "collapse", "lrrrrrrrr",
                "Split & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ & Source-only $\\Delta$ & Gated & Gain & Oracle & "
                "Recov.\\ (\\%) " + BS,
                note, small=True)


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
    split_rows, split_note = t4_split_rows()
    rows += ["\\midrule"] + split_rows
    note = ("All rows above the second rule use the same windows, the same two mechanical folds and the same 12 paired "
            "tasks; the random forests use no adaptation and no target data. Tasks share source checkpoints; fold comparisons are descriptive (Section~\\ref{sec:protocol}). " + split_note + " Differences are computed before rounding.")
    return wrap("\n".join(rows),
                "SDALR and non-adaptive random-forest controls "
                "on Paderborn, leaky versus bearing-disjoint targets (accuracy, \\%).", "methods", "lrrr",
                "Method & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ " + BS, note)


def t4_split_rows():
    """Split-level rows for the same non-SDALR methods, where they exist: these carry the inference."""
    rows, notes = [], []
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
        notes.append("The rows below the second rule are means over the ten pre-specified splits, where the split is "
                     "the summary unit; the time-statistics and combined forests lose accuracy in 10 of 10 splits. Nominal tests are in S6.")
    c105 = json.load(open(ROOT / "results" / "c105" / "c105_source_only.json", encoding="utf-8"))["sdalr_ten_splits"]
    s5 = c105["summary"]
    rows.insert(0, f"Source model only (before adaptation), ten splits & {s5['mean_pre_leaky']:.1f} & "
                   f"{s5['mean_pre_clean']:.1f} & {s5['mean_pre_leaky'] - s5['mean_pre_clean']:.1f} " + BS)
    kin = json.load(open(ROOT / "results" / "c112" / "c112_result.json", encoding="utf-8"))
    ks = [f"S{i:02d}" for i in range(10)]
    klk = np.mean([kin["per_split"][x]["leaky"] for x in ks])
    kcl = np.mean([kin["per_split"][x]["clean"] for x in ks])
    rows.append(f"Random forest, kinematic features, ordinary accuracy & {klk:.1f} & {kcl:.1f} & "
                f"{klk - kcl:.1f} " + BS)
    notes.append("Source model only: batch-0 accuracy of the SDALR source checkpoint before any adaptation step "
                 f"(median $\\Delta$ {s5['median_pre_delta']:.1f}~pp). Kinematic forest: record-level, maxima of the "
                 "normalised envelope spectrum at the specimen's own BPFO/BPFI harmonics and shaft orders (median "
                 f"$\\Delta_{{\\mathrm{{leak}}}}$ {kin['summary']['median_delta']:.1f}~pp).")
    corrected = json.load(open(ROOT / "results/reporting_2026_10_09/reporting_corrections.json", encoding="utf-8"))["kinematic_balanced"]
    rows.append(f"Kinematic forest, balanced accuracy (sensitivity) & {corrected['mean_leaky']:.1f} & "
                f"{corrected['mean_clean']:.1f} & {corrected['mean_leaky'] - corrected['mean_clean']:.1f} " + BS)
    notes.append("Kinematic rows use full recordings: ordinary accuracy above, balanced accuracy below. "
                 "The clean record-level class ratio is 3 healthy : 3 inner : 2 outer bearings. "
                 "The post-hoc balanced sensitivity has median gap 10.4 pp (S6). "
                 "Intervals are conditional on reused bearings (Section 4).")
    return rows, " ".join(notes)


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
        rows.append(f"{labels[g]} & ${'z' if key=='z' else chr(92)+'alpha'}={op[g]:g}$ & {here['healthy_FA']}/480 & {by} & {here['correct']} & {max(zero) if zero else '--'} " + BS)
    note=("Six healthy bearings (K001--K006) contribute 80 recordings each, for 480 records. The per-bearing column follows that order. "
          "Correct verdicts are counted over 1{,}839 single-fault recordings; the full pool comprises 29 bearings (6 healthy, 11 real-damage, 12 artificial-damage) at four conditions. "
          "Operating points were fixed before evaluation. The final column is the largest correct-verdict count over the parameter sweep with no observed healthy false acceptance. "
          "Zero observed errors is not a new-bearing safety bound. Assumption-dependent intervals are in S6; operating curves are in S2.")
    return wrap("\n".join(rows),
                "Observed gate performance: false acceptance (FA) on 480 recordings from six healthy bearings, and correct fault verdicts.",
                "gates", "llrlrr",
                "Gate & Op. point & Healthy FA & FA by bearing & Correct & At zero FA " + BS, note, small=True)


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
    raw_note = (f" Raw-spectrum band rule: seed 2024 only and never run on the ten splits; its fold means are "
                f"{dA.mean():+.2f} (fold A source) and {dB.mean():+.2f}~pp (fold B source).")
    note = ("Every arm of a comparison runs in one job on the same source checkpoint according to the job configuration, with identical pre-update "
            "target accuracy as a consistency check, not a checkpoint-hash proof. The between-seed spread of the "
            "per-task gain is 1.7~pp (comb) and 2.4~pp (envelope), against 2.8~pp for ungated per-task accuracy. "
            "The 12 tasks of a seed share two source folds and are descriptive. The conditional split-level comparison is reported in "
            "Table~\\ref{tab:collapse}." + raw_note)
    return wrap("\n".join(rows[:-1]),
                "Paired per-task effect of gating inside SDALR on the 12 bearing-disjoint tasks of the two mechanical folds "
                "(gated $-$ ungated, percentage points).", "gains", "llrrrrr",
                "Gate & Seed & Mean & Median & Min & Max & Tasks $>0$ " + BS, note, small=True)


def t7_hust():
    R = {}
    for p in glob.glob(str(H.A / "**" / "result_HUST_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if len(d.get("adapted", {})) == 6:
            R[(d["src_fold"], d["tgt_fold"])] = np.array([d["adapted"][t] for t in H.TASKS])
    kl = list(H.A.rglob("kernel_log_hust.json"))
    types = {f"H{i}": s for i, s in enumerate(json.load(open(kl[0], encoding="utf-8")).get("splits", []))} if kl else {}
    rows, lk, cl = [], [], []
    for v in sorted({s for s, _ in R}):
        a, b = R[(v, v)].mean(), R[(v, v + "c")].mean()
        lk.append(a); cl.append(b)
        rows.append(f"{v} & {', '.join('620' + t for t in types.get(v, []))} & {a:.1f} & {b:.1f} & {a - b:.1f} " + BS)
    lk, cl = np.array(lk), np.array(cl)
    p = wilcoxon(lk, cl, alternative="greater", zero_method="zsplit").pvalue
    note = (f"Median $\\Delta_{{\\mathrm{{leak}}}}$ {np.median(lk - cl):.1f}~pp (range {np.min(lk - cl):.1f}--"
            f"{np.max(lk - cl):.1f}); positive in all six splits. These are descriptive results from a fixed pool of bearing types. "
            "The clean target changes bearing size together with specimen. Nominal tests and the pre-specified "
            "replication-rule assessment are in Supplementary~S6.")
    return wrap("\n".join(rows),
                "Second rig: SDALR on HUST bearing, six pre-specified type-disjoint splits (accuracy, \\%). The source is "
                "three bearing types; the clean target is the other two at the target load.", "hust", "llrrr",
                "Split & Source bearings & Leaky & Clean & $\\Delta_{\\mathrm{leak}}$ " + BS, note)


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
                    f"{L} $\\times$ {w} & {r['seen_acc']:.0f} & {r['unseen_acc']:.0f} & {r['diff']:+.0f} & "
                    f"{r['correct_fault_verdicts_adapt_conditions']['pcv']}/{r['records_adapt_conditions']} " + BS)
    h = [r for r in d["rows"] if r["bearing"].startswith("K0")]
    rows.append("\\midrule")
    rows.append(f"K001--K006 & IBU & healthy & -- & -- & {np.mean([r['seen_acc'] for r in h]):.0f} & "
                f"{np.mean([r['unseen_acc'] for r in h]):.0f} & {np.mean([r['diff'] for r in h]):+.0f} & "
                f"{sum(r['fault_verdicts_adapt_conditions']['pcv'] for r in h)}/360$^{{b}}$ " + BS)
    s_ = d["summary"]
    note = ("Manufacturer (page~1), damage mode, extent class (1--3) and damage length $\\times$ width in mm (page~2) are "
            "read from each bearing's own Paderborn datasheet; pitting = fatigue pitting, indentation = particle-caused "
            "plastic deformation. Seen / unseen: SDALR window accuracy (\\%) on that bearing over the ten splits in which it "
            "was in the source (scored in the leaky arm) or in the clean target. Gate: correct fault verdicts of the envelope "
            "threshold rule at the three adaptation conditions. $^{b}$ False acceptances. Over all 17 bearings the "
            f"within-bearing difference has median {s_['median_diff']:.1f}~pp (conditional 95\\,\\% CI {s_['ci_median_diff'][0]:.1f}--"
            f"{s_['ci_median_diff'][1]:.1f}): {s_['positive']} positive, {s_['ties_abs_lt_0.05']} ties, {s_['negative']} "
            "negative.")
    return wrap("\n".join(rows),
                "Per-bearing view of the Paderborn real-damage specimens: what each one is, how SDALR scores it when it was "
                "and was not in the source, and how often the envelope gate certifies it.", "bearings", "lllllrrrr",
                "Bearing & Mfr. & Damage & Extent & Size (mm) & Seen & Unseen & Diff. & Gate " + BS, note, small=True)


def t9_gate_accounting():
    d = json.load(open(ROOT / "results" / "c107" / "c107_gate_spillover.json", encoding="utf-8"))
    rows = []
    for r in d["rows"]:
        g = r["groups"]
        c, u, h = g["certified"], g["uncovered_faulty"], g["uncovered_healthy"]
        cert = (f"{100 * c['share']:.0f} & {c['acc_ungated']:.1f} $\\to$ {c['acc_gated']:.1f}" if c["windows"]
                else "0 & --")
        rows.append(f"{r['split']} & {cert} & {u['acc_ungated']:.1f} $\\to$ {u['acc_gated']:.1f} & "
                    f"{h['acc_ungated']:.1f} $\\to$ {h['acc_gated']:.1f} & {r['gain']:+.1f} & "
                    f"{c['contribution_pp']:+.1f} & {u['contribution_pp'] + h['contribution_pp']:+.1f} " + BS)
    s = d["spillover_summary"]
    note = ("Clean target of each split, SDALR ungated $\\to$ with the envelope threshold gate, windows grouped by the gate "
            "verdict of their recording. Certified: a fault verdict; silent faulty and silent healthy: no verdict. The "
            "split's gain is the sum of the last two columns (group share $\\times$ within-group change). Over the ten "
            f"splits, certified windows gain a median {s['certified']['median_change_pp']:.0f}~pp, silent faulty windows "
            f"{s['uncovered_faulty']['median_change_pp']:+.1f}~pp; certified windows carry "
            f"{100 * s['share_of_summed_gain_from_certified']:.0f}\\,\\% of the summed gain. SFDA is scored on the windows it "
            "adapts on, so the certified column reflects selective supervision on those same records; the gate filters existing pseudo-labels (C107).")
    return wrap("\n".join(rows),
                "Where the envelope-gate gain comes from: clean-target accuracy (\\%) on certified and silent recordings.",
                "gateacc", "lrrrrrrr",
                "Split & Cert.\\ (\\%) & Certified & Silent faulty & Silent healthy & Gain & from cert. & from silent " + BS,
                note, small=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("t1_datasets", t1_datasets), ("t2_splits", t2_splits), ("t3_collapse", t3_collapse),
                     ("t4_methods", t4_methods), ("t5_gates", t5_gates), ("t6_gains", t6_gains), ("t7_hust", t7_hust), ("t8_bearings", t8_bearings), ("t9_gate_accounting", t9_gate_accounting)):
        (OUT / f"{name}.tex").write_text(fn(), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
