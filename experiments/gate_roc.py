"""C73 (iv): one ROC per dataset for all gates — PU H6-C35 population (2,319 records, 480 healthy).

x = healthy false acceptance (of 480), y = correct fault verdicts (inner+outer, of 1,839), plus wrong-family calls.
C30 / comb_v2 swept over alpha from stored p-values, line counts and alias fractions (no recomputation).
EAGLE-style swept over its robust-z threshold from stored z. PCV-style swept over its z threshold (recomputed SES, none arm).
"""
from __future__ import annotations

import csv
import io
import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
OUT = ROOT / "results" / "roc"
ALPHAS = [0.004, 0.006, 0.01, 0.02, 0.05, 0.1, 0.2, 0.4, 1.0]
PCV_Z = [3, 5, 8, 10, 15, 20, 40, 80]
EAGLE_Z = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
CLS = {"BPFO": "outer_race", "BPFI": "inner_race"}
NPOS = {"BPFO": 5, "BPFI": 25}


def point(rows, key):
    H = [r for r in rows if r["fault_type"] == "normal"]
    F = [r for r in rows if r["fault_type"] != "normal"]
    return {"healthy_FA": sum(r[key] != "normal" for r in H), "n_healthy": len(H),
            "correct": sum(r[key] == r["fault_type"] for r in F), "n_fault": len(F),
            "wrong_family": sum(r[key] not in ("normal", r["fault_type"]) for r in F)}


def pcv_record(path):
    import comb, pu, prewhiten, band_select, ses
    from h6_prewhitening import N_SAMPLES, PU_BAND_HI_HZ
    from harmonic_coords import K_HARM, J_SIDE
    from kinematics import kinematics, slip_window
    r = pu.read_one(Path(path)); k = kinematics(r.bearing_model); fr = r.rpm / 60
    y = prewhiten.prewhiten(r.signal[:N_SAMPLES].astype(float), "none")
    b = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * fr, f_hi=PU_BAND_HI_HZ)
    f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(b.lo_hz, b.hi_hz)); z = comb.normalise(f, S)
    peaks = {}
    for fam in CLS:
        peaks[fam] = []
        for h in (1, 2, 3):
            lo, hi = slip_window(k, fam, harmonic=h)
            m = (f >= lo * fr) & (f <= hi * fr)
            peaks[fam].append(float(z[m].max()) if m.any() else 0.0)
    return r.record_id, peaks


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    h6 = {r["record_id"]: r for r in csv.DictReader(io.open(ROOT / "results/h6_c35/h6_records.csv", encoding="utf-8")) if r["arm"] == "cepstrum"}
    v2 = {r["record_id"]: r for r in csv.DictReader(io.open(ROOT / "results/comb_v2/v2_records.csv", encoding="utf-8")) if r["dataset"] == "PU"}
    h7 = {r["record_id"]: r for r in csv.DictReader(io.open(ROOT / "results/h7/h7_records.csv", encoding="utf-8"))}
    ids = sorted(h6)
    curves = {"c30": [], "v2": [], "eagle": [], "pcv": []}
    for a in ALPHAS:
        rows = []
        for rid in ids:
            x = h6[rid]; out = {"fault_type": x["fault_type"]}
            adm = {fam: (float(x[f"excess_{fam}"]), int(x[f"lines_{fam}"])) for fam in CLS
                   if float(x[f"p_{fam}"]) <= a / 2 and int(x[f"lines_{fam}"]) >= 2}
            out["c30"] = CLS[max(adm, key=lambda f: adm[f][0])] if adm else "normal"
            adm2 = {f: v for f, v in adm.items() if float(v2[rid][f"alias_{f}"]) < 0.5}
            out["v2"] = CLS[max(adm2, key=lambda f: (adm2[f][1] / NPOS[f], adm2[f][0]))] if adm2 else "normal"
            rows.append(out)
        curves["c30"].append({"alpha": a, **point(rows, "c30")})
        curves["v2"].append({"alpha": a, **point(rows, "v2")})
    for zt in EAGLE_Z:
        rows = []
        for rid in ids:
            x = h7[rid]
            act = [f for f in CLS if float(x[f"eagle_zsnr_{f}"]) > zt or float(x[f"eagle_zE_{f}"]) > zt]
            rows.append({"fault_type": x["fault_type"],
                         "e": CLS[max(act, key=lambda f: float(x[f"eagle_zsnr_{f}"]))] if act else "normal"})
        curves["eagle"].append({"z": zt, **point(rows, "e")})
    import pu
    from h6_prewhitening import SINGLE_FAULT, UNREADABLE
    files = [str(p) for p in pu.files(bearings=SINGLE_FAULT) if p.stem not in UNREADABLE]
    with Pool(4) as pool:
        peaks = dict(pool.map(pcv_record, files, chunksize=4))
    for zt in PCV_Z:
        rows = []
        for rid in ids:
            S = {f: np.mean([p > zt for p in peaks[rid][f]]) for f in CLS}
            best = max(S.values()); win = [f for f in S if S[f] == best]
            rows.append({"fault_type": h6[rid]["fault_type"], "p": CLS[win[0]] if best >= 2 / 3 and len(win) == 1 else "normal"})
        curves["pcv"].append({"z": zt, **point(rows, "p")})
    (OUT / "roc_pu.json").write_text(json.dumps(curves, indent=2))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.4), constrained_layout=True)
    style = {"c30": ("#2471a3", "o", "comb gate C30 (α sweep)"), "v2": ("#1e8449", "s", "comb_v2 (α sweep)"),
             "pcv": ("#b9770e", "^", "PCV-style rule (z sweep)"), "eagle": ("#922b21", "v", "EAGLE-style rule (z sweep)")}
    for g, pts in curves.items():
        c, m, lab = style[g]
        ax.plot([p["healthy_FA"] / p["n_healthy"] for p in pts], [p["correct"] / p["n_fault"] for p in pts], marker=m, color=c, label=lab, lw=1.2, ms=4)
    ax.set_xscale("symlog", linthresh=0.005); ax.set_xlabel("healthy false acceptance (of 480 PU healthy records)")
    ax.set_ylabel("correct fault verdicts (of 1,839 PU fault records)"); ax.legend(fontsize=8); ax.grid(alpha=0.3)
    fig.savefig(OUT / "roc_pu.png", dpi=200)
    for g, pts in curves.items():
        print(g, [(p.get("alpha", p.get("z")), p["healthy_FA"], p["correct"], p["wrong_family"]) for p in pts])


if __name__ == "__main__":
    main()
