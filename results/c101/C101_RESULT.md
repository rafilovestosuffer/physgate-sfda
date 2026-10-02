# C101 - the shallow baseline over the ten splits

Both arms come from the same C92 job and the same windows as the SDALR arms of that split. The split is the
unit; task-level tests are not reported because tasks within a split share a training set.

## Feature set T

| Split | Leaky | Clean | $\Delta$ |
|---|---|---|---|
| S00 | 87.5 | 71.1 | 16.4 |
| S01 | 83.8 | 63.1 | 20.7 |
| S02 | 88.6 | 64.7 | 23.9 |
| S03 | 90.9 | 58.4 | 32.4 |
| S04 | 77.0 | 74.5 | 2.5 |
| S05 | 90.5 | 52.0 | 38.5 |
| S06 | 88.0 | 73.0 | 15.0 |
| S07 | 89.6 | 68.2 | 21.4 |
| S08 | 89.0 | 53.1 | 35.9 |
| S09 | 84.7 | 58.1 | 26.7 |

Over 10 splits: median $\Delta_{leak}$ **22.7 pp**, cluster-bootstrap mean **23.4 pp** (95% CI 17.0 to 29.5; exact sign-flip p = 0.0010, positive in 10/10).

## Feature set TFE

| Split | Leaky | Clean | $\Delta$ |
|---|---|---|---|
| S00 | 93.4 | 50.1 | 43.3 |
| S01 | 94.0 | 57.1 | 36.9 |
| S02 | 90.4 | 64.9 | 25.5 |
| S03 | 93.3 | 62.8 | 30.4 |
| S04 | 93.1 | 63.8 | 29.4 |
| S05 | 96.2 | 52.3 | 43.9 |
| S06 | 93.9 | 60.2 | 33.7 |
| S07 | 93.3 | 69.3 | 24.1 |
| S08 | 96.6 | 32.3 | 64.3 |
| S09 | 86.7 | 63.6 | 23.1 |

Over 10 splits: median $\Delta_{leak}$ **32.1 pp**, cluster-bootstrap mean **35.5 pp** (95% CI 28.9 to 43.7; exact sign-flip p = 0.0010, positive in 10/10).

## Multiplicity

BH correction across the two feature sets: T p_BH = 0.0010, TFE p_BH = 0.0010

