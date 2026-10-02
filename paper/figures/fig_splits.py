"""Figure: per-split leaky / clean / clean+gate / clean+oracle (C88) with RF-T clean (C92). Regenerate when splits arrive."""
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as e, glob, json
R = e.load(); rows = []
for s in e.SPLITS:
    k = [(s, s, "none"), (s, s + "c", "none"), (s, s + "c", "pcv"), (s, s + "c", "oracle")]
    if all(x in R for x in k):
        rows.append((s, *[R[x].mean() for x in k]))
rows += [(n.replace("M1 fold ", "fold "), *v) for n, *v in e.m1_rows()]
rf = {}
for p in glob.glob(str(ROOT / "results/artifacts/physgate-run-c92-*/**/c92_result.json"), recursive=True):
    rf.update({k: v["T"]["clean_mean"] for k, v in json.load(open(p, encoding="utf-8")).items()})
x = np.arange(len(rows)); w = 0.2
fig, ax = plt.subplots(figsize=(max(6, 0.72 * len(rows) + 1.5), 3.4), constrained_layout=True)
ax.grid(axis="y", lw=0.4, color="0.85", zorder=0)
ax.set_axisbelow(True)
for i, (lab, c) in enumerate((("leaky", "#34495e"), ("clean", "#c0392b"), ("clean + envelope gate", "#d68910"), ("clean + oracle filter", "#27ae60"))):
    ax.bar(x + (i - 1.5) * w, [r[i + 1] for r in rows], w, label=lab, color=c)
ax.scatter([xi for xi, r in zip(x, rows) if r[0] in rf], [rf[r[0]] for r in rows if r[0] in rf], marker="D", color="k", s=18, zorder=3,
           label="random forest (time stats), clean")
ax.axhline(100 / 3, ls=":", c="grey", lw=1)
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows]); ax.set_ylabel("accuracy (%)"); ax.set_ylim(0, 100)
ax.legend(fontsize=7.5, ncol=5, loc="lower center", bbox_to_anchor=(0.5, 1.02), frameon=False, columnspacing=1.2, handletextpad=0.5)
ax.set_ylim(0, 108)
ax.tick_params(labelsize=8)
ax.set_xlim(-0.6, len(rows) - 0.4)
ax.axvline(len(rows) - 2.5, color="0.6", lw=0.8, ls="--")
ax.text(len(rows) - 2.4, 101, "mechanical folds", fontsize=7, color="0.35")
ax.text(-0.5, 101, "ten pre-registered random bearing splits", fontsize=7, color="0.35")
fig.savefig(ROOT / "paper/figures/fig_splits.png", dpi=200)
print("rows", len(rows))
