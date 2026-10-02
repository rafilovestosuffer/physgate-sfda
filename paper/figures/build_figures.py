"""Build every manuscript figure from retained artifacts. Run: python paper/figures/build_figures.py [name ...]

All data come through the same loaders the tables use (experiments/c88_eval.py, c94_eval.py, paired_gating.py), so a
figure cannot disagree with a table. Style and output paths: paper/figures/style.py.
"""
from __future__ import annotations

import csv
import glob
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(HERE), str(ROOT / "experiments")]
import style as S  # noqa: E402
import c88_eval as E  # noqa: E402
import c94_eval as H  # noqa: E402
import paired_gating as P  # noqa: E402

OTHER = {"A": "B", "B": "A"}


# ---------------------------------------------------------------- data helpers
def pu_splits():
    """[(name, leaky, clean, gated, oracle, rf_clean|None)] for the ten splits then the two folds."""
    R = E.load()
    rf = {}
    for p in glob.glob(str(E.A / "physgate-run-c92-rf-*" / "**" / "c92_result.json"), recursive=True):
        rf.update({k: v["T"]["clean_mean"] for k, v in json.load(open(p, encoding="utf-8")).items()})
    rows = []
    for s in E.SPLITS:
        k = [(s, s, "none"), (s, s + "c", "none"), (s, s + "c", "pcv"), (s, s + "c", "oracle")]
        if all(x in R for x in k):
            rows.append((s, *[R[x].mean() for x in k], rf.get(s)))
    rows += [(n.replace("M1 fold ", "fold "), *v[:4], None) for n, *v in E.m1_rows()]
    return rows


def hust_splits():
    R = {}
    for p in glob.glob(str(H.A / "**" / "result_HUST_M1_*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        if len(d.get("adapted", {})) == 6:
            R[(d["src_fold"], d["tgt_fold"])] = np.array([d["adapted"][t] for t in H.TASKS])
    return [(v, R[(v, v)].mean(), R[(v, v + "c")].mean()) for v in sorted({s for s, _ in R})]


def gate_diffs():
    """{(gate, seed): per-task differences} over the 12 fold tasks, paired within one job."""
    R, out = P.load(), {}
    for s in sorted({k[2] for k in R if k[0] == "final_checkpoint" and k[1] == "pcv"}):
        run = {f: sorted({k[5] for k in R if k[:5] == ("final_checkpoint", "v2", s, f, OTHER[f])})[0] for f in "AB"}
        base = {f: P.pick(R, "final_checkpoint", "none", s, f, OTHER[f], run[f]) for f in "AB"}
        for g in ("v2", "pcv"):
            arm = {f: P.pick(R, "final_checkpoint", g, s, f, OTHER[f], run[f]) for f in "AB"}
            if all(arm.values()):
                out[(g, s)] = np.concatenate([P.vec(arm[f]) - P.vec(base[f]) for f in "AB"])
    return out


# ---------------------------------------------------------------- figures
def fig2_collapse():
    """Dumbbells: leaky and clean endpoints per split, with gated, oracle and shallow-baseline markers."""
    pu, hu = pu_splits(), hust_splits()
    pu_sorted = sorted(pu[:10], key=lambda r: r[1] - r[2]) + list(reversed(pu[10:]))
    hu_sorted = sorted(hu, key=lambda r: r[1] - r[2])
    fig, axes = S.grid("double", 95, 1, 2, gridspec_kw={"width_ratios": [1, 0.58]})
    rows_csv = []

    def draw(ax, rows, ylabels, title, rf_col=True):
        for i, r in enumerate(rows):
            name, lk, cl = r[0], r[1], r[2]
            ax.plot([cl, lk], [i, i], color=S.C["faint"], lw=3.2, solid_capstyle="round", zorder=1)
            ax.plot([cl], [i], "o", color=S.C["clean"], ms=4.6, zorder=3)
            ax.plot([lk], [i], "o", color=S.C["leaky"], ms=4.6, zorder=3)
            if len(r) > 3:
                ax.plot([r[3]], [i], "|", color=S.C["gated"], ms=8, mew=1.6, zorder=4)
                ax.plot([r[4]], [i], "|", color=S.C["oracle"], ms=8, mew=1.6, zorder=4)
                if rf_col and r[5] is not None:
                    ax.plot([r[5]], [i], "D", color=S.C["shallow"], ms=2.8, zorder=5)
            ax.text(lk + 1.2, i, f"{lk - cl:.0f}", va="center", ha="left", fontsize=7.0, color=S.C["grey"])
        ax.axvline(100 / 3, color=S.C["grey"], ls=":", lw=0.7, zorder=0)
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(ylabels)
        ax.set_xlim(25, 108)
        ax.set_ylim(-0.7, len(rows) - 0.3)
        ax.set_xlabel("accuracy (%)")
        ax.set_title(title, fontsize=8, loc="left", pad=6)
        ax.invert_yaxis()

    draw(axes[0], pu_sorted, [r[0] for r in pu_sorted], "(a) Paderborn: 10 random splits + 2 folds")
    axes[0].axhline(9.5, color=S.C["grey"], lw=0.6, ls="--")
    draw(axes[1], [(r[0], r[1], r[2]) for r in hu_sorted], [r[0] for r in hu_sorted],
         "(b) HUST: 6 type-disjoint splits", rf_col=False)
    handles = [
        axes[0].plot([], [], "o", color=S.C["leaky"], ms=4.6, label="leaky target")[0],
        axes[0].plot([], [], "o", color=S.C["clean"], ms=4.6, label="bearing-disjoint target")[0],
        axes[0].plot([], [], "|", color=S.C["gated"], ms=8, mew=1.6, label="+ envelope gate")[0],
        axes[0].plot([], [], "|", color=S.C["oracle"], ms=8, mew=1.6, label="+ oracle filter")[0],
        axes[0].plot([], [], "D", color=S.C["shallow"], ms=2.8, label="random forest, no adaptation")[0],
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=5)
    for r in pu_sorted:
        rows_csv.append(["Paderborn", r[0], f"{r[1]:.2f}", f"{r[2]:.2f}", f"{r[3]:.2f}", f"{r[4]:.2f}",
                         "" if r[5] is None else f"{r[5]:.2f}"])
    for r in hu_sorted:
        rows_csv.append(["HUST", r[0], f"{r[1]:.2f}", f"{r[2]:.2f}", "", "", ""])
    S.save(fig, "fig2_collapse", rows_csv, ["rig", "split", "leaky", "clean", "gated", "oracle", "random_forest_clean"])


def fig4_decomposition():
    rows = sorted(pu_splits()[:10], key=lambda r: r[1] - r[2], reverse=True)
    fig, ax = S.figure("onehalf", 62)
    rec = np.array([r[4] - r[2] for r in rows])
    tot = np.array([r[1] - r[2] for r in rows])
    not_rec = tot - rec
    x = np.arange(len(rows))
    shown = np.minimum(rec, tot)                       # a split where the oracle arm beats the leaky arm is capped here
    ax.bar(x, shown, color=S.C["oracle"], width=0.66, label="recoverable by a perfect pseudo-label filter")
    ax.bar(x, np.clip(not_rec, 0, None), bottom=shown, color=S.C["leaky"], width=0.66,
           label="beyond any pseudo-label filter")
    for i, (r, t_) in enumerate(zip(rec, tot)):
        ax.text(i, t_ + max(tot) * 0.035, f"{100 * r / t_:.0f}%", ha="center", fontsize=7.0, color=S.C["oracle"])
        if r > t_:                                   # oracle arm beats the leaky arm: mark it, do not overdraw
            ax.plot([i], [t_ * 0.5], marker="^", ms=5, color="white", mec=S.C["oracle"], mew=0.8, zorder=4)
    med = np.median(rec / tot)
    ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows])
    ax.set_ylabel("collapse (percentage points)")
    ax.set_ylim(0, max(tot) * 1.22)
    ax.set_title(f"Recoverable share per split: median {100 * med:.0f}% (percentages above bars)",
                 fontsize=8, loc="left", pad=6)
    import matplotlib.lines as mlines
    handles, labels = ax.get_legend_handles_labels()
    handles.append(mlines.Line2D([], [], marker="^", ms=5, color="white", mec=S.C["oracle"], mew=0.8, ls="none",
                                 label="oracle arm exceeds the leaky arm (share > 100%)"))
    ax.legend(handles=handles, loc="upper right", ncol=1)
    S.save(fig, "fig4_decomposition", [[r[0], f"{t:.2f}", f"{rc:.2f}", f"{nr:.2f}", f"{100 * rc / t:.1f}"]
                                       for r, t, rc, nr in zip(rows, tot, rec, not_rec)],
           ["split", "total_collapse_pp", "filter_recoverable_pp", "not_recoverable_pp", "recoverable_pct"])


def fig5_roc():
    """(a) operating curves per gate; (b) what the gate can speak on predicts what it is worth."""
    roc = json.load(open(ROOT / "results" / "roc" / "roc_pu.json", encoding="utf-8"))
    meta = {"pcv": ("envelope threshold rule", S.C["gated"], "-", 10),
            "v2": ("shaft-alias-guarded comb", S.C["oracle"], "-", 0.05),
            "c30": ("surrogate-null comb test", S.C["comb"], "--", 0.05),
            "eagle": ("raw-spectrum band rule", S.C["eagle"], ":", 2)}
    fig, axes = S.grid("onehalf", 80, 1, 2, gridspec_kw={"width_ratios": [1, 0.92]})
    ax = axes[0]
    rows = []
    for g, (lab, col, ls, op) in meta.items():
        pts = sorted(roc[g], key=lambda r: (r["healthy_FA"], r["correct"]))
        fa = 100 * np.array([p["healthy_FA"] for p in pts]) / pts[0]["n_healthy"]
        keep = np.maximum.accumulate(np.array([p["correct"] for p in pts]))   # best reachable at each false-acceptance level
        ax.step(fa, keep, where="post", color=col, ls=ls, lw=1.1, label=lab)
        key = "z" if "z" in pts[0] else "alpha"
        here = min(roc[g], key=lambda r: abs(r[key] - op))
        ax.plot(100 * here["healthy_FA"] / here["n_healthy"], here["correct"], "o", color=col, ms=4, zorder=4)
        rows += [[g, p.get("z", p.get("alpha")), p["healthy_FA"], p["n_healthy"], p["correct"], p["n_fault"]] for p in roc[g]]
    ax.set_xlim(-0.4, 12)
    ax.set_ylim(292, 392)                       # the curves live here; the excluded region is described in the notes below
    ax.set_xlabel("false acceptance on healthy recordings (%)")
    ax.set_ylabel("correct fault verdicts (of 1839)")
    ax.set_title("(a) gate operating curves", fontsize=8, loc="left", pad=6)

    cg = json.load(open(ROOT / "results" / "c98" / "c98_coverage_gain.json", encoding="utf-8"))
    bx = axes[1]
    xs = [100 * p[1] for p in cg["points"]]
    ys = [p[2] for p in cg["points"]]
    bx.plot([min(xs) - 2, max(xs) + 2], [0, 0], color=S.C["grey"], lw=0.7, ls=":", zorder=0)
    bx.plot(xs, ys, "o", color=S.C["gated"], ms=4.2, zorder=3)
    fit = np.polyfit(xs, ys, 1)
    xg = np.linspace(min(xs), max(xs), 50)
    bx.plot(xg, np.polyval(fit, xg), "-", color=S.C["grey"], lw=0.8, zorder=2)
    for name, c, g in cg["points"]:      # label the top end only; the fitted line runs through the bottom-left corner
        if 100 * c == max(xs) or 100 * c == min(xs):
            bx.annotate(name, (100 * c, g), textcoords="offset points", xytext=(6, -2), ha="left",
                        fontsize=7.0, color=S.C["grey"])
    bx.set_xlabel("faulty target recordings spoken on (%)")
    bx.set_ylabel("gate gain (pp)")
    bx.set_title(f"(b) coverage predicts the gain: $\\rho$ = {cg['rho']:.2f}", fontsize=8, loc="left", pad=6)

    fig.legend(handles=ax.get_legend_handles_labels()[0], loc="outside lower center", ncol=2)
    rows += [["coverage_gain", p[0], "", "", f"{100 * p[1]:.1f}", f"{p[2]:.2f}"] for p in cg["points"]]
    S.save(fig, "fig5_roc", rows, ["gate", "parameter", "healthy_false_accept", "n_healthy", "correct", "n_fault"])


def fig6_gains():
    D = gate_diffs()
    gates = [("v2", "shaft-alias-guarded comb"), ("pcv", "envelope threshold rule")]
    seeds = sorted({s for _, s in D})
    fig, ax = S.figure("onehalf", 66)
    rng = np.random.default_rng(0)
    rows, xt, xl = [], [], []
    for gi, (g, gname) in enumerate(gates):
        for si, s in enumerate(seeds):
            d = D[(g, s)]
            x = gi * (len(seeds) + 0.8) + si
            col = S.C["gated"] if g == "pcv" else S.C["oracle"]
            ax.scatter(x + rng.uniform(-0.12, 0.12, d.size), d, s=9, color=col, alpha=0.75, lw=0, zorder=3)
            boot = [np.median(rng.choice(d, d.size)) for _ in range(2000)]
            lo, hi = np.percentile(boot, [2.5, 97.5])
            ax.plot([x + 0.3, x + 0.3], [lo, hi], color=S.C["leaky"], lw=1.1, zorder=4)
            ax.plot([x + 0.22, x + 0.38], [np.median(d)] * 2, color=S.C["leaky"], lw=1.6, zorder=5)
            xt.append(x); xl.append(str(s))
            rows += [[g, s, f"{v:.3f}"] for v in d]
    import matplotlib.transforms as mtrans
    blend = mtrans.blended_transform_factory(ax.transData, ax.transAxes)
    for gi, (g, gname) in enumerate(gates):
        ax.text(gi * (len(seeds) + 0.8) + 1.15, 1.02, gname, ha="center", va="bottom", fontsize=7.5, transform=blend)
    ax.axvspan(len(seeds) + 0.8 - 0.6, 2 * len(seeds) + 0.8, color=S.C["faint"], alpha=0.35, lw=0, zorder=0)
    ax.axhline(0, color=S.C["grey"], lw=0.8)
    ax.set_xticks(xt); ax.set_xticklabels(xl)
    ax.set_xlabel("seed")
    ax.set_ylabel("gated − ungated (pp)")
    S.save(fig, "fig6_gains", rows, ["gate", "seed", "per_task_difference_pp"])


def fig7_slip():
    rows = list(csv.DictReader(open(ROOT / "results" / "c90" / "c90_records.csv", encoding="utf-8")))
    groups = {"PU IBU/MTK (6203)": ("PU", "6203_PU_2905"), "PU FAG (6203)": ("PU", "6203_PU_2855"),
              "CWRU fan end (6203)": ("CWRU_FE", "6203")}
    fig, ax = S.figure("single", 68)   # +6 mm for the legend below the axes
    cols = [S.C["comb"], S.C["oracle"], S.C["eagle"]]
    csv_rows, stars = [], []
    for (lab, (ds, geo)), col in zip(groups.items(), cols):
        sel = [r for r in rows if r["dataset"] == ds and r["geometry"] == geo and r["unmasked_valid"] == "True"]
        if not sel:
            continue
        v = np.array([100 * float(r["unmasked_s_hat"]) for r in sel])
        ax.hist(v, bins=np.arange(-0.8, 1.0, 0.05), color=col, alpha=0.6, label=f"{lab}, n={v.size}")
        stars.append((100 * float(sel[0]["s_star"]), col))
        csv_rows += [[lab, f"{x:.4f}"] for x in v]
    lo, hi = min(s0 for s0, _ in stars), max(s0 for s0, _ in stars)
    ax.axvspan(lo - 0.06, hi + 0.06, color=S.C["faint"], alpha=0.8, lw=0, zorder=0)
    for s0, col in stars:
        ax.axvline(s0, color=col, ls="--", lw=1.0, zorder=2)
    ax.set_xlim(-0.8, 2.6)
    ax.set_ylim(0, 92)
    ax.annotate(f"$s^*$ = {lo:.2f}–{hi:.2f}%" + chr(10) + "(race lines lock" + chr(10) + "onto shaft orders)",
                xy=(lo - 0.07, 30), xytext=(0.42, 42), fontsize=8.6, ha="left", va="center", color="#444444",
                arrowprops=dict(arrowstyle="->", color="#444444", lw=0.7, shrinkA=2, shrinkB=1))
    ax.set_xlabel("measured cage slip (% of nominal order)")
    ax.set_ylabel("recordings")
    # legend outside the axes, as in the other figures: inside, it sat on the tall IBU/MTK bars near zero slip
    fig.legend(handles=ax.get_legend_handles_labels()[0], loc="outside lower center", ncol=2)
    S.save(fig, "fig7_slip", csv_rows, ["population", "measured_slip_pct"])


def _bearing_shares(logdir):
    """{bearing: (true_class, [share_normal, share_inner, share_outer], n_windows)} from saved per-window predictions."""
    import collections
    acc = collections.defaultdict(lambda: [0, 0, 0])
    truth, n = {}, collections.Counter()
    for f in sorted(Path(logdir).glob("pred_*.npz")):
        d = np.load(f, allow_pickle=False)
        pred = d["prob"].argmax(1)
        for rec, y, pr in zip(d["record_id"], d["label"], pred):
            b = str(rec).split("_")[3]
            acc[b][int(pr)] += 1
            truth[b] = int(y)
            n[b] += 1
    return {b: (truth[b], np.array(v) / sum(v), n[b]) for b, v in acc.items()}


def fig3_bearings():
    """(a) per-bearing accuracy when seen vs unseen (C106); (b) clean/leaky accuracy vs source bearings per class (C110)."""
    d = json.load(open(ROOT / "results" / "c106" / "c106_within_bearing.json", encoding="utf-8"))["rows"]
    c110 = json.load(open(ROOT / "results" / "c110" / "c110_result.json", encoding="utf-8"))
    fig, axes = S.grid("double", 78, 1, 2, gridspec_kw={"width_ratios": [1, 0.8]})
    ax = axes[0]
    order = sorted(d, key=lambda r: (r["bearing"][:2], r["bearing"]))
    rows = []
    for i, r in enumerate(order):
        cert = r["correct_fault_verdicts_adapt_conditions"]["pcv"] if not r["bearing"].startswith("K0") else 0
        col = S.C["gated"] if cert >= 30 else S.C["clean"]
        ax.plot([r["unseen_acc"], r["seen_acc"]], [i, i], color=S.C["faint"], lw=3.0, solid_capstyle="round", zorder=1)
        ax.plot([r["seen_acc"]], [i], "o", color=S.C["leaky"], ms=4.4, zorder=3)
        ax.plot([r["unseen_acc"]], [i], "o", color=col, ms=4.4, zorder=3)
        rows.append(["bearing", r["bearing"], f"{r['seen_acc']:.2f}", f"{r['unseen_acc']:.2f}", cert])
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([r["bearing"] for r in order], fontsize=6.8)
    ax.invert_yaxis()
    ax.set_xlim(-3, 103)
    ax.set_xlabel("SDALR window accuracy on the bearing (%)")
    ax.set_title("(a) the same bearing, seen vs unseen", fontsize=8, loc="left", pad=6)
    bx = axes[1]
    by = {}
    for r in c110["rows"]:
        by.setdefault(tuple(r["triple"]), {}).setdefault(r["n"], []).append(r)
    ns = [1, 2, 3, 4]
    for key, col, lab in (("leaky", S.C["leaky"], "seen bearings (held-out recordings)"),
                          ("clean", S.C["clean"], "unseen bearings")):
        per = np.array([[100 * np.mean([x[key] for x in v[n]]) for n in ns] for v in by.values()])
        q1, med, q3 = np.percentile(per, [25, 50, 75], axis=0)
        bx.fill_between(ns, q1, q3, color=col, alpha=0.18, lw=0)
        bx.plot(ns, med, "o-", color=col, ms=4, lw=1.2, label=lab)
        rows += [["curve", key, n, f"{m:.2f}", f"{a:.2f}", f"{b:.2f}"] for n, m, a, b in zip(ns, med, q1, q3)]
    bx.axhline(100 / 3, color=S.C["grey"], ls=":", lw=0.7)
    bx.set_xticks(ns)
    bx.set_ylim(25, 102)
    bx.set_xlabel("source bearings per class")
    bx.set_ylabel("balanced accuracy (%)")
    bx.set_title("(b) more source specimens, better transfer", fontsize=8, loc="left", pad=6)
    bx.legend(loc="lower right", fontsize=6.8)
    handles = [ax.plot([], [], "o", color=S.C["leaky"], ms=4.4, label="seen (in the source)")[0],
               ax.plot([], [], "o", color=S.C["clean"], ms=4.4, label="unseen")[0],
               ax.plot([], [], "o", color=S.C["gated"], ms=4.4, label="unseen, gate-certifiable bearing")[0]]
    fig.legend(handles=handles, loc="outside lower center", ncol=3)
    S.save(fig, "fig3_bearings", rows, ["panel", "key", "a", "b", "c", "d"])


def fig3_purity():
    base = E.A / "physgate-m2-fb" / "m2" / "logs_PU_M1_final_checkpoint_FBtoA_s2024"
    gated = E.A / "physgate-m2-fb" / "m2" / "logs_PU_M1_final_checkpoint_FBtoA_gatepcv_s2024"
    ung, gat = _bearing_shares(base), _bearing_shares(gated)
    order = sorted(ung, key=lambda b: (ung[b][0], b))
    names = {0: "normal", 1: "inner race", 2: "outer race"}
    short = {0: "healthy", 1: "inner", 2: "outer"}
    cols = [S.C["normal"], S.C["inner"], S.C["outer"]]
    fig, axes = S.grid("onehalf", 74, 1, 2, sharey=True, gridspec_kw={"width_ratios": [1, 1]})
    rows = []
    for ax, data, title in ((axes[0], ung, "(a) SDALR, no gate"), (axes[1], gat, "(b) + envelope threshold gate")):
        for i, b in enumerate(order):
            y_true, share, n = data[b]
            left = 0.0
            for c in range(3):
                ax.barh(i, share[c], left=left, color=cols[c], height=0.68,
                        edgecolor="white", linewidth=0.4)
                left += share[c]
            ax.text(1.02, i, f"{share.max():.2f}", va="center", fontsize=7.0, color=S.C["grey"])
            rows.append([title.split(") ")[1], b, names[y_true], *[f"{v:.3f}" for v in share], n])
        ax.set_yticks(range(len(order)))
        ax.set_yticklabels([f"{b} ({short[data[b][0]]})" for b in order], fontsize=7.0)
        ax.set_xlim(0, 1.13)
        ax.set_xticks([0, 0.5, 1.0])
        ax.set_xlabel("share of the bearing's windows")
        ax.set_title(title, fontsize=8, loc="left", pad=5)
        ax.invert_yaxis()
    handles = [axes[0].barh(0, 0, color=c, label=f"predicted {names[i]}") for i, c in enumerate(cols)]
    fig.legend(handles=handles, loc="outside lower center", ncol=3)
    S.save(fig, "fig3_purity", rows,
           ["arm", "bearing", "true_class", "share_normal", "share_inner", "share_outer", "n_windows"])


FIGS = {"fig2_collapse": fig2_collapse, "fig3_bearings": fig3_bearings, "fig3_purity": fig3_purity, "fig4_decomposition": fig4_decomposition, "fig5_roc": fig5_roc,
        "fig6_gains": fig6_gains, "fig7_slip": fig7_slip}

if __name__ == "__main__":
    names = sys.argv[1:] or list(FIGS)
    for n in names:
        print(n)
        FIGS[n]()
