# C102 - A/A noise floor: repeated executions of one configuration

Each pair below differs in nothing except the execution (same code path, seed, data, arm). Every retained
execution of the gating configuration is compared with the first one.

| Fold | Arm | Reference run | Repeat run | Ref. mean | Repeat mean | Fold-mean difference | Max task difference |
|---|---|---|---|---|---|---|---|
| A | ungated | physgate-m2-fa | physgate-m2rep-fa-r1 | 56.762 | 56.762 | +0.000 | 0.00 |
| A | shaft-alias-guarded comb | physgate-m2-fa | physgate-m2rep-fa-r1 | 60.712 | 60.712 | +0.000 | 0.00 |
| A | envelope threshold rule | physgate-m2-fa | physgate-m2rep-fa-r1 | 61.173 | 61.173 | +0.000 | 0.00 |
| A | ungated | physgate-m2-fa | physgate-m2rep-fa-r2 | 56.762 | 56.762 | +0.000 | 0.00 |
| A | shaft-alias-guarded comb | physgate-m2-fa | physgate-m2rep-fa-r2 | 60.712 | 60.712 | +0.000 | 0.00 |
| A | envelope threshold rule | physgate-m2-fa | physgate-m2rep-fa-r2 | 61.173 | 61.173 | +0.000 | 0.00 |
| A | ungated | physgate-m2-fa | c103-pretrain_in_process | 56.762 | 56.762 | +0.000 | 0.00 |
| A | ungated | physgate-m2-fa | c103-skip_pretrain | 56.762 | 56.762 | +0.000 | 0.00 |
| B | ungated | physgate-m2-fb | physgate-m2rep-fb-r1 | 55.312 | 55.312 | +0.000 | 0.00 |
| B | shaft-alias-guarded comb | physgate-m2-fb | physgate-m2rep-fb-r1 | 58.828 | 58.828 | +0.000 | 0.00 |
| B | envelope threshold rule | physgate-m2-fb | physgate-m2rep-fb-r1 | 62.302 | 62.302 | +0.000 | 0.00 |

## The floor

- 11 A/A arm pairs, 66 paired tasks: largest absolute per-task difference 0.00 pp, largest fold-mean difference 0.00 pp.
- The executions are separate (different wall-clock and kernels) but bit-identical in accuracy: under a fixed
  seed and a fixed code path the pipeline is deterministic on the T4.

## What an effect has to clear instead

A zero floor makes ratios against it meaningless. The relevant null for any single comparison is therefore the
random trajectory itself, i.e. the seed. Ungated clean fold means over seeds 0, 1 and 2024:

- fold A: 56.76, 59.69, 56.47 (range 3.22 pp)
- fold B: 55.31, 53.46, 55.30 (range 1.85 pp)

The collapse (median 36.2 pp over ten splits) exceeds this by an order of magnitude. The gate gain (median
4.5 pp over ten splits) is of the same order as the seed range, which is why the gate claim rests on paired,
same-seed, same-job arms and on the ten-split distribution rather than on any single pair of runs.

Consequence (see C103): a difference between two JOBS running one nominal configuration cannot be
non-deterministic arithmetic; it must come from something that differs between the jobs.

