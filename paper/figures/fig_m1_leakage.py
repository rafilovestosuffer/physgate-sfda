"""Figure: M1 paired leaky vs clean accuracy (SDALR, source-only) and per-bearing label purity. Reads retained artifacts only."""
import json, glob, re
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "results" / "artifacts"
def adapted(variant, s, t):
    p = glob.glob(str(A / f"physgate-m1-f{s.lower()}" / "m1" / f"result_PU_M1_{variant}_F{s}to{t}_s2024.json"))[0]
    return json.load(open(p))["adapted"]
def src_only(s, t):
    out = {}
    for f in glob.glob(str(A / f"physgate-m1-f{s.lower()}" / "m1" / f"logs_PU_M1_as_released_F{s}to{t}_s2024" / "adapt_*.log")):
        txt = open(f, encoding="utf8", errors="ignore").read()
        m = re.search(r"\(B\d\)(\S+?)→\(B\d\)(\S+?);", txt); acc = float(re.findall(r"总正确率[:：]?\s*=?\s*([\d.]+)%", txt)[0])
        out[f.split("adapt_")[1][:2]] = acc
    return out
tasks = ["A1->A3", "A1->A2", "A3->A1", "A3->A2", "A2->A1", "A2->A3"]
fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8), constrained_layout=True, gridspec_kw={"width_ratios": [2.2, 1]})
ax = axes[0]; x = np.arange(12); w = 0.38
leak = [adapted("final_checkpoint", s, s)[t] for s in "AB" for t in tasks]
clean = [adapted("final_checkpoint", s, {"A": "B", "B": "A"}[s])[t] for s in "AB" for t in tasks]
ax.bar(x - w / 2, leak, w, color="#7f8c8d", label="leaky target (same bearings)")
ax.bar(x + w / 2, clean, w, color="#2471a3", label="clean target (unseen bearings)")
ax.axhline(100 / 3, color="k", ls=":", lw=1); ax.text(11.6, 35, "chance", ha="right", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels([f"{s}:{t.replace('->', '→')}" for s in "AB" for t in tasks], rotation=60, fontsize=7)
ax.set_ylabel("target accuracy (%)"); ax.set_ylim(0, 105); ax.legend(fontsize=8, loc="lower left")
ax.set_title(f"(a) SDALR final checkpoint: leaky {np.mean(leak):.1f}% vs clean {np.mean(clean):.1f}%", fontsize=9, loc="left")
ax = axes[1]
z = np.load(sorted(glob.glob(str(A / "physgate-m2-fb" / "m2" / "logs_PU_M1_final_checkpoint_FBtoA_s2024" / "pred_01.npz")))[0])
pred = z["prob"].argmax(1); lab = z["label"]; bid = np.array([r.split("_")[3] for r in z["record_id"]])
names = ["normal", "inner", "outer"]; bs = sorted(set(bid), key=lambda b: (lab[bid == b][0], b))
M = np.array([[np.mean(pred[bid == b] == c) for c in range(3)] for b in bs])
ax.imshow(M, cmap="Blues", vmin=0, vmax=1, aspect="auto")
for i, b in enumerate(bs):
    ax.add_patch(plt.Rectangle((lab[bid == b][0] - .5, i - .5), 1, 1, fill=False, ec="#c0392b", lw=1.5))
ax.set_yticks(range(len(bs))); ax.set_yticklabels(bs, fontsize=7); ax.set_xticks(range(3)); ax.set_xticklabels(names, fontsize=8)
ax.set_xlabel("predicted class (fraction of windows)"); ax.set_title("(b) one label per bearing (B→A, A1→A3)", fontsize=9, loc="left")
out = ROOT / "paper" / "figures"
for e in ("png", "pdf"): fig.savefig(out / f"fig_m1_leakage.{e}", dpi=200)
print("leak", np.mean(leak), "clean", np.mean(clean))
