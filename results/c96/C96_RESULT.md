# C96 — clustered inference and multiplicity control

Raised in review: within a fold the 12 tasks share source checkpoints and bearing sets, so they are not independent. Each effect below is reported three ways: the task-level Wilcoxon test as originally stated, a bootstrap that resamples whole clusters, and an exact permutation test that flips the sign of entire clusters. The cluster is the source fold (2 clusters) for the fold experiments and the split (10 or 6 clusters) elsewhere.

| effect | unit | n clusters | mean effect (pp) | 95% cluster bootstrap | task-level p | cluster p |
|---|---|---|---|---|---|---|
| Collapse (leaky − clean), two folds | source fold | 2 | 37.28 | [29.97, 44.60] | 0.00024 | 0.250 |
| Collapse, ten random splits | split | 10 | 38.17 | [27.81, 48.43] | 0.00098 | 0.0010 |
| Gate gain, ten random splits | split | 10 | 7.82 | [3.30, 13.07] | 0.00293 | 0.0029 |
| Shaft-alias-guarded comb gain, two folds (seed 2024) | source fold | 2 | 3.73 | [3.52, 3.95] | 0.0068 | 0.250 |
| Envelope threshold rule gain, two folds (seed 2024) | source fold | 2 | 5.70 | [4.41, 6.99] | 0.0010 | 0.250 |
| RF (10 time statistics) collapse, ten splits | split | 10 | 23.35 | [16.77, 29.42] | 0.00000 | 0.0010 |
| RF (time + spectral + envelope) collapse, ten splits | split | 10 | 35.47 | [28.85, 43.54] | 0.00000 | 0.0010 |
| HUST collapse, six type-disjoint splits | split | 6 | 39.12 | [30.14, 49.77] | 0.00000 | 0.0156 |
| Same-condition RF collapse, ten splits (C104) | split | 10 | 29.81 | [23.59, 36.08] | 0.00000 | 0.0010 |
| SHOT collapse, 10 splits | split | 10 | 25.30 | [16.36, 35.21] | 0.00000 | 0.0010 |

## Benjamini--Hochberg adjustment across this family of primary tests

| effect | cluster p | BH-adjusted | BY-adjusted (any dependence) |
|---|---|---|---|
| collapse, two folds | 0.2500 | 0.2500 | 0.7322 |
| Collapse, ten random splits | 0.0010 | 0.0020 | 0.0057 |
| Gate gain, ten random splits | 0.0029 | 0.0049 | 0.0143 |
| Shaft-alias-guarded comb gain, two folds (seed 2024) | 0.2500 | 0.2500 | 0.7322 |
| Envelope threshold rule gain, two folds (seed 2024) | 0.2500 | 0.2500 | 0.7322 |
| RF (10 time statistics) collapse, ten splits | 0.0010 | 0.0020 | 0.0057 |
| RF (time + spectral + envelope) collapse, ten splits | 0.0010 | 0.0020 | 0.0057 |
| HUST collapse, six type-disjoint splits | 0.0156 | 0.0223 | 0.0654 |
| Same-condition RF collapse, ten splits (C104) | 0.0010 | 0.0020 | 0.0057 |
| SHOT collapse, 10 splits | 0.0010 | 0.0020 | 0.0057 |

## Reading

With only two source folds, an exact cluster-level test cannot reach a p-value below 0.25, so the fold experiments should be read as descriptive: the effect is large and in the same direction in both folds, but two clusters cannot carry significance on their own. The ten random splits are the inferential backbone: both the collapse and the gate gain survive cluster-level permutation and Benjamini--Hochberg adjustment. Task-level p-values reported elsewhere in the paper assume independent tasks and are therefore optimistic; they are retained only as descriptive statistics and are marked as such.
