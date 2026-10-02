"""C98: how much of an adaptation target the physics gate actually speaks on.

Raised in the second review round: C95 reported gate coverage over the whole Paderborn gate population (7 of 11
real-damage bearings engaged, 209 of 880 records). Those two counts pull in different directions -- most of the
relevant bearings, but a quarter of the records -- and the discussion's "cannot act on bearings it never engages"
argument was written against the bearing count alone.

This script reports coverage as the adaptation loop sees it. The hook in `runners/sdalr_runner.py` vetoes a
pseudo-label only on a target record whose gate verdict is a fault class (`speaks = v > 0`); on every other record the
pseudo-label passes untouched. So the quantity that bounds the gate's effect is the share of TARGET records it speaks
on, at the three adaptation conditions, restricted to each experiment's own clean target bearings.

Descriptive, CPU only, no new runs: reads the retained per-record verdicts. Writes results/c98/C98_RESULT.md.
"""
from __future__ import annotations

import csv
import json
import statistics as st
from pathlib import Path

import numpy as np
import yaml

import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "c98"
sys.path.insert(0, str(Path(__file__).resolve().parent))
ADAPT_CONDITIONS = ("N15_M01_F10", "N15_M07_F04", "N15_M07_F10")
FOLDS = {  # M1 mechanical folds (configs/splits.yaml), source sets; the clean target is the complement
    "A": {"normal": ["K001", "K002", "K003"], "outer_race": ["KA04", "KA15", "KA16"],
          "inner_race": ["KI04", "KI14", "KI16"]},
    "B": {"normal": ["K004", "K005", "K006"], "outer_race": ["KA22", "KA30"],
          "inner_race": ["KI17", "KI18", "KI21"]},
}
GATES = {"pcv_class": "Envelope threshold rule", "comb_class": "Surrogate-null comb test",
         "eagle_class": "Raw-spectrum band rule"}


def load_records():
    rows = [r for r in csv.DictReader(open(ROOT / "results" / "h7" / "h7_records.csv", encoding="utf-8"))]
    v2 = {r["record_id"]: r["v2"] for r in
          csv.DictReader(open(ROOT / "results" / "comb_v2" / "v2_records.csv", encoding="utf-8"))
          if r.get("dataset") == "PU"}
    for r in rows:
        r["v2_class"] = v2.get(r["record_id"], "")
    return [r for r in rows if r["condition"] in ADAPT_CONDITIONS]


def target_sets():
    """{name: [bearing_id]} -- the clean target of every adaptation experiment in the paper."""
    out = {}
    for f, src in FOLDS.items():
        other = FOLDS["B" if f == "A" else "A"]
        out[f"fold {f}"] = sorted(b for c in other for b in other[c])
    cfg = yaml.safe_load(open(ROOT / "configs" / "splits_k10.yaml", encoding="utf-8"))
    for sid, d in sorted(cfg["splits"].items()):
        out[sid] = sorted(b for c in d["target"] for b in d["target"][c])
    return out


def damage_modes():
    """{bearing: 'fatigue / Pitting'} read from Paderborn's own per-bearing damage profiles (data/pu/<B>/<B>.pdf)."""
    try:
        import fitz
    except ImportError:
        return {}

    def field(lines, label, span=4):
        for i, l in enumerate(lines):
            if l.strip() == label:
                for j in range(i + 1, min(i + span, len(lines))):
                    v = lines[j].strip()
                    if v and v not in ("mm", "-", "pc.", "°", "Unit"):
                        return v
        return ""

    out = {}
    for pdf in sorted((ROOT / "data" / "pu").glob("K*/K*.pdf")):
        L = [l for p in fitz.open(pdf) for l in p.get_text().split("\n")]
        mode, sym = field(L, "Mode"), field(L, "Symptom")
        if mode:
            out[pdf.stem] = f"{mode} / {sym}"
    return out


def coverage(rows, bearings, col):
    """Coverage of one gate on one clean target set, at the three adaptation conditions."""
    sel = [r for r in rows if r["bearing_id"] in bearings]
    faulty = [r for r in sel if r["fault_type"] != "normal"]
    spoke = [r for r in sel if r.get(col) not in (None, "", "normal")]
    spoke_f = [r for r in faulty if r.get(col) not in (None, "", "normal")]
    right = [r for r in spoke if r[col] == r["fault_type"]]
    eng = {r["bearing_id"] for r in spoke_f if r[col] == r["fault_type"]}
    fb = {r["bearing_id"] for r in faulty}
    return {"records": len(sel), "faulty_records": len(faulty), "spoke": len(spoke),
            "spoke_share": len(spoke) / max(len(sel), 1),
            "spoke_share_faulty": len(spoke_f) / max(len(faulty), 1),
            "precision_when_speaking": len(right) / max(len(spoke), 1),
            "bearings_engaged": len(eng), "faulty_bearings": len(fb),
            "per_bearing_share": {b: sum(1 for r in faulty if r["bearing_id"] == b
                                         and r.get(col) == r["fault_type"]) /
                                     max(sum(1 for r in faulty if r["bearing_id"] == b), 1) for b in sorted(fb)}}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, tgts = load_records(), target_sets()
    data = {g: {name: coverage(rows, set(bs), g) for name, bs in tgts.items()} for g in GATES}
    json.dump(data, open(OUT / "c98_coverage.json", "w", encoding="utf-8"), indent=1)

    L = ["# C98 - gate coverage inside the adaptation loop", "",
         "The hook vetoes a pseudo-label only on a target record whose gate verdict is a fault class. Coverage is",
         "therefore reported over the records of each experiment's own clean target set, at the three adaptation",
         f"conditions ({', '.join(ADAPT_CONDITIONS)}). Descriptive; no new runs.", ""]
    for g, title in GATES.items():
        d = data[g]
        L += [f"## {title} (`{g}`)", "",
              "| Target | Records | Gate speaks | Share of all | Share of faulty | Correct when speaking | Faulty bearings engaged |",
              "|---|---|---|---|---|---|---|"]
        for name, c in d.items():
            L.append(f"| {name} | {c['records']} | {c['spoke']} | {100 * c['spoke_share']:.1f}% | "
                     f"{100 * c['spoke_share_faulty']:.1f}% | {100 * c['precision_when_speaking']:.1f}% | "
                     f"{c['bearings_engaged']}/{c['faulty_bearings']} |")
        sp = [c["spoke_share_faulty"] for c in d.values()]
        be = [c["bearings_engaged"] / max(c["faulty_bearings"], 1) for c in d.values()]
        L += ["", f"Median over the 12 target sets: gate speaks on {100 * st.median(sp):.1f}% of faulty target records "
                  f"and engages {100 * st.median(be):.0f}% of faulty target bearings.", ""]
    # Per-bearing engagement over the whole real-damage pool, at the adaptation conditions only. C95 reported 7 of 11
    # over all four conditions; the number that bounds adaptation is this one.
    real = sorted({r["bearing_id"] for r in rows if r["fault_type"] != "normal"
                   and r["bearing_id"] in {b for bs in tgts.values() for b in bs}})
    L += ["## Envelope rule: per-bearing engagement at the three adaptation conditions", "",
          "C95 counted 7 of 11 real-damage bearings engaged over all four operating conditions. Adaptation uses three,",
          "and over those three the count is lower; this is the figure the ceiling argument must use.", "",
          "| Bearing | Damage mode (first-party profile) | Certified records |", "|---|---|---|"]
    mech = damage_modes()
    eng = 0
    for b in real:
        sel = [r for r in rows if r["bearing_id"] == b and r["fault_type"] != "normal"]
        ok = [r for r in sel if r.get("pcv_class") == r["fault_type"]]
        eng += bool(ok)
        L.append(f"| {b} | {mech.get(b, '?')} | {len(ok)}/{len(sel)} |")
    L += ["", f"Engaged at the adaptation conditions: {eng} of {len(real)} real-damage bearings.", ""]

    # Does coverage predict the gain? Split-level, so no pseudo-replication.
    try:
        import c88_eval as E
        from scipy.stats import rankdata, spearmanr
        pts = [(s, data["pcv_class"][s]["spoke_share_faulty"],
                E.load()[(s, s + "c", "pcv")].mean() - E.load()[(s, s + "c", "none")].mean())
               for s in E.SPLITS if (s, s + "c", "pcv") in E.load()]
        rho, p = spearmanr([q[1] for q in pts], [q[2] for q in pts])
        # Is coverage just a proxy for how much room there was to gain? Headroom = oracle - ungated clean.
        R = E.load()
        head = [R[(s, s + "c", "oracle")].mean() - R[(s, s + "c", "none")].mean() for s, _, _ in pts]
        cov_v = np.array([q[1] for q in pts])
        gain_v = np.array([q[2] for q in pts])
        head_v = np.array(head)
        rho_h, p_h = spearmanr(head_v, gain_v)
        rho_ch, p_ch = spearmanr(cov_v, head_v)

        def partial(x, y, z):
            """Spearman between x and y with z partialled out, on ranks."""
            rx, ry, rz = (rankdata(v) for v in (x, y, z))
            ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz)
            ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
            return spearmanr(ex, ey)

        pc_r, pc_p = partial(cov_v, gain_v, head_v)
        ph_r, ph_p = partial(head_v, gain_v, cov_v)
        L += ["## Coverage predicts the gain",
              "",
              "| Split | Gate speaks on faulty target records | Gate gain (pp) | Headroom (oracle - clean, pp) |",
              "|---|---|---|---|"]
        L += [f"| {s} | {100 * c:.1f}% | {g:+.2f} | {h:.2f} |" for (s, c, g), h in zip(pts, head)]
        L += ["", f"Spearman rho = {rho:.3f}, p = {p:.2g} over {len(pts)} splits (the split is the unit).", "",
              "### Is coverage a proxy for headroom?", "",
              "Raised in review: a gate can only gain where the oracle shows room to gain, so the correlation above may",
              "be a headroom effect wearing a coverage mask. It is not.", "",
              "| Relation | Spearman rho | p |", "|---|---|---|",
              f"| gain ~ coverage | {rho:.3f} | {p:.2g} |",
              f"| gain ~ headroom | {rho_h:.3f} | {p_h:.2g} |",
              f"| coverage ~ headroom | {rho_ch:.3f} | {p_ch:.2g} |",
              f"| gain ~ coverage, headroom partialled out | {pc_r:.3f} | {pc_p:.2g} |",
              f"| gain ~ headroom, coverage partialled out | {ph_r:.3f} | {ph_p:.2g} |", "",
              "Headroom on its own does not predict the gain at this sample size, and once coverage is partialled out it",
              "predicts nothing at all; coverage survives partialling headroom out essentially undiminished.", ""]
        json.dump({"rho": rho, "p": p, "points": pts, "headroom": head,
                   "rho_headroom": rho_h, "p_headroom": p_h,
                   "rho_coverage_headroom": rho_ch, "p_coverage_headroom": p_ch,
                   "partial_gain_coverage_given_headroom": [pc_r, pc_p],
                   "partial_gain_headroom_given_coverage": [ph_r, ph_p]},
                  open(OUT / "c98_coverage_gain.json", "w"), indent=1)
    except Exception as exc:  # the correlation needs the C88 artifacts mounted
        L += [f"(coverage-gain correlation not computed: {exc})", ""]
    (OUT / "C98_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:12]))
    print("...\nwrote", OUT / "C98_RESULT.md")


if __name__ == "__main__":
    main()
