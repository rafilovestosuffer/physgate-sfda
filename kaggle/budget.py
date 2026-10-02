"""Project GPU-hours for a planned batch BEFORE pushing. Over quota => reduce scope and NAME deferrals.

Never silently shorten training or drop seeds to fit a budget.
"""
from __future__ import annotations
import argparse

WEEKLY_QUOTA_H = 30.0
HALT_BELOW_H = 3.0
SESSION_CAP_H = 9.0

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--runs", type=int, required=True)
    p.add_argument("--minutes-per-run", type=float, required=True)
    p.add_argument("--used-this-week-h", type=float, default=0.0)
    a = p.parse_args()
    need = a.runs * a.minutes_per_run / 60.0
    left = WEEKLY_QUOTA_H - a.used_this_week_h
    sessions = need / SESSION_CAP_H
    print(f"planned: {a.runs} runs x {a.minutes_per_run:.1f} min = {need:.2f} GPU-h "
          f"(~{sessions:.1f} x 9 h sessions)")
    print(f"quota remaining this week: {left:.2f} h (halt threshold {HALT_BELOW_H} h)")
    if left - need < HALT_BELOW_H:
        print("OVER BUDGET: reduce scope and list the deferred experiments in DECISIONS.md. "
              "Do NOT shorten training or drop seeds.")
        return 1
    print("within budget")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
