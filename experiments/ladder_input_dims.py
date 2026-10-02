"""C47/C63: per rung x dataset x backbone -> input shape, parameters, receptive field (samples and physical units),
training windows per smallest class. Emits results/feasibility/ladder_input_dims.csv. CPU, no training."""
import csv, sys
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "models"))
from backbones import BACKBONES, receptive_field
T = 3.0
DS = {"PU": dict(fs=64000, rpm=1500, train_win=480), "CWRU": dict(fs=12000, rpm=1772, train_win=None),
      "UORED": dict(fs=42000, rpm=1750, train_win=3 * 2 * 8)}   # UORED: 3 train bearings x 2 fault records (developing, faulty) x 8 windows/10 s = 48 < 250 -> target only (C42)
FMAX_ORD = 30.0
def rungs(d):
    fs, fr = d["fs"], d["rpm"] / 60
    n_ses = int(round(FMAX_ORD * fr * T))                       # 0..30 orders at df = 1/T
    return [("L0 raw", 1, int(T * fs), f"{1e3/fs:.4f} ms/sample"),
            ("L1-L2.5 SES (Hz axis, 0-30 x f_r)", 1, n_ses, f"{1/T:.3f} Hz/bin"),
            ("L3 order SES (0-30 orders)", 1, int(round(FMAX_ORD * fr * T)), f"{1/(T*fr):.4f} order/bin"),
            ("L4 KNEOS-HC J=0", 5, 45, "k x sub-bin"),
            ("L5 KNEOS-HC J=2 (C63)", 13, 45, "k x sub-bin")]
rows = []
for ds, d in DS.items():
    for rung, c, L, unit in rungs(d):
        for bb, cls in BACKBONES.items():
            m = cls(c, L, 3)
            with torch.no_grad():
                m(torch.zeros(1, c, L))
            rf = receptive_field(m)
            rows.append(dict(dataset=ds, rung=rung, backbone=bb, in_channels=c, length=L, values=c * L,
                             params=sum(p.numel() for p in m.parameters()), receptive_field_samples=rf,
                             receptive_field_fraction_of_input=round(min(1.0, rf / L), 4), axis_unit=unit,
                             est_train_windows_smallest_class=d["train_win"]))
out = ROOT / "results" / "feasibility" / "ladder_input_dims.csv"
with out.open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
for r in rows:
    if r["dataset"] == "PU":
        print(r["rung"], r["backbone"], r["in_channels"], r["length"], r["params"], r["receptive_field_fraction_of_input"])
print("wrote", out)
