# Paired gating analysis and collapse decomposition

Source: retained artifacts under results/artifacts (M1, M2, M2seed). Unit = (source fold, task); 12 per seed.

## 1. Is the comparison paired?

- seed 0, arm `v2`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**
- seed 1, arm `v2`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**
- seed 2024, arm `v2`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**
- seed 0, arm `pcv`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**
- seed 1, arm `pcv`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**
- seed 2024, arm `pcv`: pre-adaptation source_only (batch-0 accuracy in every adapt log) identical to the ungated arm: **True**

Identical batch-0 (pre-update) accuracy in every adapt log means the arms share the source checkpoint (same seed, same source model, gate on vs off). The comparison is **paired**; the relevant variance is that of the per-task difference.

## 2. Paired per-task differences (gated − ungated, pp)

| arm | seed | mean | sd | min | median | max | tasks > 0 | one-sided Wilcoxon p |
|---|---|---|---|---|---|---|---|---|
| v2 | 0 | +3.79 | 4.15 | -0.08 | +3.33 | +11.01 | 7/12 | 0.0078 |
| v2 | 1 | +4.56 | 4.95 | -0.08 | +3.28 | +15.45 | 8/12 | 0.0068 |
| v2 | 2024 | +3.73 | 3.23 | -0.05 | +3.67 | +8.07 | 8/12 | 0.0068 |
| pcv | 0 | +7.44 | 6.79 | -0.01 | +7.57 | +18.02 | 9/12 | 0.0020 |
| pcv | 1 | +7.99 | 7.77 | -0.70 | +6.65 | +19.44 | 10/12 | 0.0017 |
| pcv | 2024 | +5.70 | 4.75 | -0.05 | +5.59 | +14.52 | 10/12 | 0.0010 |

Between-seed sd of the **ungated** per-task accuracy (same task, different seed), mean over tasks: 2.75 pp (seeds [0, 1, 2024]). Compare with the sd of the paired differences above.
- `v2`: per-task gain averaged over seeds [0, 1, 2024]: mean +4.03, between-seed sd of the per-task gain 1.73 pp.
- `pcv`: per-task gain averaged over seeds [0, 1, 2024]: mean +7.05, between-seed sd of the per-task gain 2.44 pp.

## 3. Decomposition of the collapse (final_checkpoint, seed 2024, matched variant)

| leaky | clean (ungated) | clean + oracle filter | total collapse | recoverable by a perfect pseudo-label filter | not recoverable by any filter |
|---|---|---|---|---|---|
| 94.12 | 56.04 | 82.67 | 38.08 | 26.64 (70 %) | 11.45 (30 %) |

Clean ungated is taken from the same kernel as the oracle arm (shared source model). The M1 kernel's ungated clean run of the same configuration gave 56.84 (run-to-run GPU nondeterminism across kernels).

Caveats: one seed; the oracle filter keeps only correct pseudo-labels but still trains on the unchanged source model, so the non-recoverable part is source-representation failure *as seen through SDALR's adaptation*. The supervisor's figures (94.7 / 56.3 / 82.7) mixed the as_released leaky mean with final_checkpoint clean arms; the matched-variant values are above.
