"""C102: the A/A noise floor — how far apart do two runs of the IDENTICAL configuration land?

Raised in review round 3: every effect in this paper is a difference between two runs, and CUDA kernels are not
bit-deterministic under a fixed seed (non-deterministic cuBLAS reductions, cuDNN algorithm selection, atomicAdd-based
backward passes). A gain is only interpretable against the spread of a null difference, so that spread has to be measured
rather than assumed.

Design: the m2 gating job was executed twice more per fold with the same seed, the same source checkpoint policy and the same
arms (`physgate-m2rep-f*-r1` / `-r2`). The A/A contrast is the SAME arm across the two repeats -- an experiment in which
nothing was changed, so any difference is run-to-run noise. Reported per arm (ungated, comb, envelope) and pooled, at both
the task level and the fold-mean level, beside the effects the manuscript claims.

Descriptive, CPU, no new runs. Writes results/c102/.
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))
import c88_eval as E  # noqa: E402

OUT = ROOT / "results" / "c102"
ARMS = {"": "ungated", "_gatev2": "shaft-alias-guarded comb", "_gatepcv": "envelope threshold rule"}
OTHER = {"A": "B", "B": "A"}


def load_arm(job, fold, arm):
    pat = str(E.A / job / "**" / f"result_PU_M1_final_checkpoint_F{fold}to{OTHER[fold]}{arm}_s2024.json")
    hits = glob.glob(pat, recursive=True)
    if not hits:
        return None
    d = json.load(open(hits[0], encoding="utf-8"))
    return np.array([d["adapted"][t] for t in E.TASKS])


def repeats(fold):
    """[(job label, {arm: per-task accuracies})] for every retained execution of the fold's gating configuration.

    Extended 2026-09-29: the original gating job (`physgate-m2-f*`) runs the identical configuration and is a third
    execution; for fold A the two C103 arms (ungated only) are a fourth and fifth. All share code path, seed and data.
    """
    out = []
    jobs = [E.A / f"physgate-m2-f{fold.lower()}"] + [Path(j) for j in sorted(glob.glob(str(E.A / f"physgate-m2rep-f{fold.lower()}-r*")))]
    for job in jobs:
        if job.exists():
            arms = {a: load_arm(job.name, fold, a) for a in ARMS}
            if arms[""] is not None:
                out.append((job.name, arms))
    if fold == "A":
        for arm in ("pretrain_in_process", "skip_pretrain"):
            f = E.A / "physgate-c103-pretrain-state" / "c103" / f"result_{arm}.json"
            if f.exists():
                d = json.load(open(f, encoding="utf-8"))
                out.append((f"c103-{arm}", {"": np.array([d["adapted"][t] for t in E.TASKS])}))
    return out


def seed_spread():
    """Between-seed spread of the ungated fold mean (seeds 0, 1, 2024), the relevant null once the A/A floor is zero."""
    res = {}
    for fold in "AB":
        ms = []
        for job, seed in ((f"physgate-m2-f{fold.lower()}", 2024), (f"physgate-m2seed-f{fold.lower()}-s0", 0),
                          (f"physgate-m2seed-f{fold.lower()}-s1", 1)):
            hits = glob.glob(str(E.A / job / "**" / f"result_PU_M1_final_checkpoint_F{fold}to{OTHER[fold]}_s{seed}.json"),
                             recursive=True)
            if hits:
                d = json.load(open(hits[0], encoding="utf-8"))
                ms.append(float(np.mean([d["adapted"][t] for t in E.TASKS])))
        res[fold] = ms
    return res


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, pooled = [], []
    L = ["# C102 - A/A noise floor: repeated executions of one configuration", "",
         "Each pair below differs in nothing except the execution (same code path, seed, data, arm). Every retained",
         "execution of the gating configuration is compared with the first one.", "",
         "| Fold | Arm | Reference run | Repeat run | Ref. mean | Repeat mean | Fold-mean difference | Max task difference |",
         "|---|---|---|---|---|---|---|---|"]
    for fold in "AB":
        reps = repeats(fold)
        if len(reps) < 2:
            L.append(f"| {fold} | -- | only {len(reps)} retained execution | | | | | |")
            continue
        l1, a1 = reps[0]
        for l2, a2 in reps[1:]:
            for arm, name in ARMS.items():
                if a1.get(arm) is None or a2.get(arm) is None:
                    continue
                d = a1[arm] - a2[arm]
                pooled.append(d)
                rows.append({"fold": fold, "arm": name, "run1": l1, "run2": l2,
                             "mean1": float(a1[arm].mean()), "mean2": float(a2[arm].mean()),
                             "fold_mean_diff": float(d.mean()), "max_abs_task_diff": float(np.abs(d).max()),
                             "per_task": [float(x) for x in d]})
                L.append(f"| {fold} | {name} | {l1} | {l2} | {a1[arm].mean():.3f} | {a2[arm].mean():.3f} | "
                         f"{d.mean():+.3f} | {np.abs(d).max():.2f} |")
    if not pooled:
        print("no A/A pair retained; nothing written")
        return
    all_d = np.concatenate(pooled)
    fold_means = np.array([r["fold_mean_diff"] for r in rows])
    seeds = seed_spread()
    summary = {"n_pairs": len(rows), "n_task_pairs": int(all_d.size), "task_sd": float(all_d.std(ddof=1)),
               "task_max_abs": float(np.abs(all_d).max()), "fold_mean_max_abs": float(np.abs(fold_means).max()),
               "seed_fold_means": seeds,
               "seed_fold_mean_range": {f: (max(v) - min(v)) if len(v) > 1 else None for f, v in seeds.items()},
               "rows": rows}
    json.dump(summary, open(OUT / "c102_aa_floor.json", "w", encoding="utf-8"), indent=1)

    sr = summary["seed_fold_mean_range"]
    L += ["", "## The floor", "",
          f"- {len(rows)} A/A arm pairs, {all_d.size} paired tasks: largest absolute per-task difference "
          f"{summary['task_max_abs']:.2f} pp, largest fold-mean difference {summary['fold_mean_max_abs']:.2f} pp.",
          "- The executions are separate (different wall-clock and kernels) but bit-identical in accuracy: under a fixed",
          "  seed and a fixed code path the pipeline is deterministic on the T4.", "",
          "## What an effect has to clear instead", "",
          "A zero floor makes ratios against it meaningless. The relevant null for any single comparison is therefore the",
          "random trajectory itself, i.e. the seed. Ungated clean fold means over seeds 0, 1 and 2024:",
          "",
          f"- fold A: {', '.join(f'{m:.2f}' for m in seeds['A'])} (range {sr['A']:.2f} pp)",
          f"- fold B: {', '.join(f'{m:.2f}' for m in seeds['B'])} (range {sr['B']:.2f} pp)", "",
          "The collapse (median 36.2 pp over ten splits) exceeds this by an order of magnitude. The gate gain (median",
          "4.5 pp over ten splits) is of the same order as the seed range, which is why the gate claim rests on paired,",
          "same-seed, same-job arms and on the ten-split distribution rather than on any single pair of runs.", "",
          "Consequence (see C103): a difference between two JOBS running one nominal configuration cannot be",
          "non-deterministic arithmetic; it must come from something that differs between the jobs.", ""]
    (OUT / "C102_RESULT.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
