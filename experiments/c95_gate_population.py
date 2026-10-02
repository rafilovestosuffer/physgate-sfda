"""C95: disclose the gate-evaluation population and report coverage separately for real- and artificial-damage bearings.

Raised in review: the gate study uses 2,319 Paderborn recordings spanning 6 healthy, 11 real-damage and 12 artificial-damage
bearings at all four operating conditions, while the adaptation experiments use only the real-damage bearings at three
conditions. Coverage on the bearings that actually enter adaptation was never reported separately. This script reads the
retained per-record verdicts and writes results/c95/C95_RESULT.md. No new runs; descriptive only.
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "c95"
REAL = {"KA04", "KA15", "KA16", "KA22", "KA30", "KI04", "KI14", "KI16", "KI17", "KI18", "KI21"}
ADAPT_CONDITIONS = {"N15_M01_F10", "N15_M07_F04", "N15_M07_F10"}


def origin(bid: str) -> str:
    if bid.startswith("K0"):
        return "healthy"
    return "real" if bid in REAL else "artificial"


def load():
    rows = {r["record_id"]: dict(r) for r in csv.DictReader(open(ROOT / "results" / "h7" / "h7_records.csv", encoding="utf-8"))}
    for r in csv.DictReader(open(ROOT / "results" / "comb_v2" / "v2_records.csv", encoding="utf-8")):
        if r.get("dataset") == "PU" and r["record_id"] in rows:
            rows[r["record_id"]]["v2_class"] = r["v2"]
    return list(rows.values())


def block(rows, col):
    """false acceptance on healthy; correct verdicts and engaged bearings by damage origin."""
    fa = sum(1 for r in rows if origin(r["bearing_id"]) == "healthy" and r.get(col) not in (None, "", "normal"))
    n_h = sum(1 for r in rows if origin(r["bearing_id"]) == "healthy")
    out = {"healthy_false_accept": f"{fa}/{n_h}"}
    for kind in ("real", "artificial"):
        sel = [r for r in rows if origin(r["bearing_id"]) == kind]
        ok = [r for r in sel if r.get(col) == r["fault_type"]]
        eng = {r["bearing_id"] for r in ok}
        allb = {r["bearing_id"] for r in sel}
        out[kind] = {"records": len(sel), "correct": len(ok), "recall": len(ok) / max(len(sel), 1),
                     "bearings_engaged": f"{len(eng)}/{len(allb)}", "engaged": sorted(eng)}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load()
    by = defaultdict(int)
    for r in rows:
        by[(origin(r["bearing_id"]), r["condition"] in ADAPT_CONDITIONS)] += 1
    gates = [("pcv_class", "Envelope threshold rule"), ("v2_class", "Shaft-alias-guarded comb"),
             ("comb_class", "Surrogate-null comb test"), ("eagle_class", "Raw-spectrum band rule")]
    L = ["# C95 — gate-evaluation population and coverage by damage origin", "",
         "Descriptive re-analysis of the retained per-record verdicts (`results/h7/h7_records.csv`, "
         "`results/comb_v2/v2_records.csv`). No new runs.", "",
         "## Population", "",
         f"{len(rows)} recordings from 29 physical bearings at four operating conditions: 6 healthy, 11 real-damage and "
         f"12 artificial-damage. The adaptation experiments use the 11 real-damage bearings and 6 healthy bearings at three "
         f"of the four conditions.", "",
         "| damage origin | recordings, all 4 conditions | of which at the 3 adaptation conditions |", "|---|---|---|"]
    for kind in ("healthy", "real", "artificial"):
        L.append(f"| {kind} | {by[(kind, True)] + by[(kind, False)]} | {by[(kind, True)]} |")
    L += ["", "## Coverage at the pre-registered operating points", "",
          "A bearing counts as engaged when at least one of its recordings receives the correct fault verdict.", "",
          "| gate | healthy false acceptance | real: correct / records | real bearings engaged | artificial: correct / records | artificial bearings engaged |",
          "|---|---|---|---|---|---|"]
    detail = []
    for col, name in gates:
        if not any(col in r for r in rows):
            continue
        b = block(rows, col)
        L.append(f"| {name} | {b['healthy_false_accept']} | {b['real']['correct']}/{b['real']['records']} | "
                 f"{b['real']['bearings_engaged']} | {b['artificial']['correct']}/{b['artificial']['records']} | "
                 f"{b['artificial']['bearings_engaged']} |")
        detail.append(f"- **{name}** engages real-damage bearings {', '.join(b['real']['engaged']) or 'none'}; "
                      f"artificial-damage bearings {', '.join(b['artificial']['engaged']) or 'none'}.")
    L += ["", *detail, "",
          "## Reading", "",
          "The gate study characterises safety on 480 real healthy recordings, which is the quantity that matters before a "
          "gate is trusted inside adaptation. Detection coverage, however, is not uniform across damage origin: the "
          "engaged-bearing counts above separate the artificial (EDM, drilling, manual indentation) bearings from the "
          "real fatigue and plastic-deformation damage used in the transfer experiments. Only the real-damage row bears on "
          "the gating results of the adaptation sections; the artificial bearings enter the safety study only.",
          ]
    (OUT / "C95_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
