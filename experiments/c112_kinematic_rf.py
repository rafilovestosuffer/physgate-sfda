"""C112 - Kinematic-feature forest under the leakage design (PROTOCOL C112, pre-registered before this run).

Per record (first 249,600 samples, as the gates): kurtogram band selection and squared envelope spectrum exactly as the
envelope rule's arm (h7_rules.process, prewhitening 'none'), normalised by comb.normalise; features = for BPFO and BPFI
and harmonics 1..5 the maximum normalised SES inside the per-bearing one-sided slip window (C35 kinematics, measured
speed), plus the maximum at shaft orders 1..3 (+/- 2 native bins): 13 features, all in shaft-order coordinates.
Random forest (500 trees, random_state 0) per C91/C92 cross-condition task on the ten C88 splits and the two folds:
train on the source bearings' records at the source condition, test at the target condition on the same bearings (leaky)
and on the complementary bearings (clean). Record-level accuracy. Split = unit, exact sign-flip p.
Single process (CLAUDE.md rule 4). Writes results/c112/.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import yaml
from sklearn.ensemble import RandomForestClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "physics"), str(ROOT / "data_prep"), str(ROOT / "experiments")]
import band_select, comb, prewhiten, pu, ses  # noqa: E402,E401
from h6_prewhitening import N_SAMPLES, PU_BAND_HI_HZ  # noqa: E402
from harmonic_coords import J_SIDE, K_HARM  # noqa: E402
from kinematics import kinematics, slip_window  # noqa: E402
from rev6_load import sign_flip_p, boot_median_ci  # noqa: E402

OUT = ROOT / "results" / "c112"
COND = {"A1": "N15_M01_F10", "A2": "N15_M07_F04", "A3": "N15_M07_F10"}
TASKS = [("A1", "A3"), ("A1", "A2"), ("A3", "A1"), ("A3", "A2"), ("A2", "A1"), ("A2", "A3")]
CLASSES = {"normal": 0, "inner_race": 1, "outer_race": 2}
BEARINGS = ["K001", "K002", "K003", "K004", "K005", "K006", "KA04", "KA15", "KA16", "KA22", "KA30",
            "KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]
FEATURES = [f"{fam}_h{h}" for fam in ("BPFO", "BPFI") for h in range(1, 6)] + ["shaft_1", "shaft_2", "shaft_3"]


def label(bid):
    return 0 if bid.startswith("K0") else (2 if bid.startswith("KA") else 1)


def record_features(path):
    r = pu.read_one(Path(path))
    k = kinematics(r.bearing_model)
    f_r = r.rpm / 60.0
    x = r.signal[:N_SAMPLES].astype(np.float64)
    y = prewhiten.prewhiten(x, "none")
    band = band_select.select_band(y, r.fs_hz, max_level=6, max_fault_hz=(K_HARM * k.BPFI + J_SIDE) * f_r,
                                   f_hi=PU_BAND_HI_HZ)
    f, S = ses.squared_envelope_spectrum(y, r.fs_hz, band=(band.lo_hz, band.hi_hz))
    z = comb.normalise(f, S)
    df = f[1] - f[0]
    vals = []
    for fam in ("BPFO", "BPFI"):
        for h in range(1, 6):
            lo, hi = slip_window(k, fam, harmonic=h)
            m = (f >= lo * f_r) & (f <= hi * f_r)
            if not m.any():
                m = np.abs(f - getattr(k, fam) * h * f_r) == np.abs(f - getattr(k, fam) * h * f_r).min()
            vals.append(float(z[m].max()))
    for h in (1, 2, 3):
        m = np.abs(f - h * f_r) <= 2 * df
        vals.append(float(z[m].max()))
    return r.record_id, r.bearing_id, r.condition, vals


def build_features():
    cache = OUT / "c112_features.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    paths = pu.files(BEARINGS, list(COND.values()))
    t0 = time.time()
    rows = []
    for i, p in enumerate(paths):
        rid, bid, cond, v = record_features(p)
        rows.append({"record_id": rid, "bearing": bid, "condition": cond, "features": v})
        if i % 100 == 0:
            print(f"{i}/{len(paths)} records, {time.time() - t0:.0f} s", flush=True)
    out = {"feature_names": FEATURES, "rows": rows, "elapsed_s": round(time.time() - t0)}
    OUT.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(out), encoding="utf-8")
    return out


def split_sets():
    cfg = yaml.safe_load(open(ROOT / "configs" / "splits_k10.yaml", encoding="utf-8"))["splits"]
    out = {s: ({b for v in d["source"].values() for b in v}, {b for v in d["target"].values() for b in v})
           for s, d in cfg.items()}
    sys.path.insert(0, str(ROOT / "data_prep"))
    from make_m1 import fold_bearings
    a = {b for v in fold_bearings("A").values() for b in v}
    bb = {b for v in fold_bearings("B").values() for b in v}
    out["fold A"], out["fold B"] = (a, bb), (bb, a)
    return out


def main():
    data = build_features()
    X = np.array([r["features"] for r in data["rows"]])
    B = np.array([r["bearing"] for r in data["rows"]])
    C = np.array([r["condition"] for r in data["rows"]])
    Y = np.array([label(b) for b in B])
    res = {}
    for name, (src, tgt) in split_sets().items():
        tasks = []
        for s, t in TASKS:
            tr = np.isin(B, list(src)) & (C == COND[s])
            lk = np.isin(B, list(src)) & (C == COND[t])
            cl = np.isin(B, list(tgt)) & (C == COND[t])
            clf = RandomForestClassifier(500, n_jobs=1, random_state=0).fit(X[tr], Y[tr])
            pl, pc = clf.predict(X[lk]), clf.predict(X[cl])
            bal = float(np.mean([(pc[Y[cl] == k] == k).mean() for k in np.unique(Y[cl])]))
            tasks.append({"task": f"{s}->{t}", "leaky": 100 * float((pl == Y[lk]).mean()),
                          "clean": 100 * float((pc == Y[cl]).mean()), "clean_balanced": 100 * bal,
                          "n_train": int(tr.sum()), "n_clean": int(cl.sum())})
        res[name] = {"tasks": tasks, "leaky": float(np.mean([x["leaky"] for x in tasks])),
                     "clean": float(np.mean([x["clean"] for x in tasks])),
                     "clean_balanced": float(np.mean([x["clean_balanced"] for x in tasks]))}
        res[name]["delta"] = res[name]["leaky"] - res[name]["clean"]
        print(f"{name}: leaky {res[name]['leaky']:.1f} clean {res[name]['clean']:.1f} delta {res[name]['delta']:.1f}")
    splits = [f"S{i:02d}" for i in range(10)]
    d = np.array([res[s]["delta"] for s in splits])
    med = float(np.median(d))
    p = sign_flip_p(d, "greater")
    decision = "KINEMATIC FEATURES COLLAPSE TOO" if (med >= 10 and p < 0.05) else (
        "KINEMATIC FEATURES TRANSFER" if med < 10 else "INCONCLUSIVE (median >= 10, p >= 0.05)")
    summary = {"median_delta": med, "ci95_median": boot_median_ci(d), "positive": int((d > 0).sum()), "p_one_sided": p,
               "decision": decision, "median_leaky": float(np.median([res[s]["leaky"] for s in splits])),
               "median_clean": float(np.median([res[s]["clean"] for s in splits])),
               "mean_clean": float(np.mean([res[s]["clean"] for s in splits]))}
    (OUT / "c112_result.json").write_text(json.dumps({"entry": "C112", "status": "pre-registered 2026-10-02",
                                                      "per_split": res, "summary": summary}, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
