# H6 — corrected-geometry re-run (C35) and the bearing-level reading

Artifacts: `h6_records.csv`, `h6_summary.json`, `h6_cluster_bootstrap.json` (this folder); pre-registered run
in `results/h6/` (pre-C35 geometry), kept unchanged. Decision rule PROTOCOL C28 via C31; geometry C35.

## 1. Pre-registered analysis (record level) — NOT SUPPORTED, again

| arm | run | outer precision [Wilson 95 %] | says outer | inner precision | called normal | I→O | healthy false acceptance |
|---|---|---|---|---|---|---|---|
| none | pre-C35 | 0.690 [0.631, 0.744] | 255 | 0.870 | 80.4 % | 79 | 18/480 = 3.8 % |
| none | **C35** | **0.742 [0.683, 0.793]** | 240 | 0.880 | 80.3 % | 62 | 15/480 = 3.1 % |
| cepstrum | pre-C35 | 0.955 [0.910, 0.978] | 156 | 0.880 | 85.0 % | 7 | 15/480 = 3.1 % |
| cepstrum | **C35** | **0.955 [0.910, 0.978]** | 155 | 0.875 | 85.4 % | 7 | **9/480 = 1.9 % [1.0, 3.5]** |

Outer prevalence 0.414. `none` is not at chance → H6 NOT SUPPORTED as worded, in both runs. The geometry
correction moved the raw arm up (+0.05) and halved healthy false acceptance in the cepstrum arm; it did not
change any conclusion.

## 2. Secondary: by physical bearing — this changes how the numbers may be read

Records per bearing = 80 (KA08: 79), and verdicts are strongly clustered within a bearing. Substantive fault
verdicts (≥ 10 of 80 records) occur on **6 of 23 fault bearings**:

| bearing | geometry | truth | none n/i/o | cepstrum n/i/o |
|---|---|---|---|---|
| KA01 | 29.05 (MTK) | outer, artificial | 0/0/80 | 0/0/80 |
| KA04 | 28.55 (FAG) | outer, real | 24/0/56 | 51/0/29 |
| KA16 | 29.05 (MTK) | outer, real | 40/0/40 | 41/0/39 |
| KI01 | 29.05 (MTK) | inner, artificial | 1/79/0 | 1/79/0 |
| **KI16** | **28.55 (FAG)** | inner, real | **0/23/57** | 41/32/7 |
| KI18 | 29.05 (MTK) | inner, real | 0/75/5 | 38/42/0 |

The other 17 fault bearings are called normal in ≥ 75/80 records in both arms. Healthy bearings K001–K006:
≤ 7/80 false calls each (raw), ≤ 3/80 (cepstrum).

- **Inner→outer confusion is one bearing.** 57 of the 62 raw I→O confusions come from KI16, a FAG bearing
  (full lock: 3·f_r inside the BPFO slip window). Pre-whitening removes 50 of them. This is exactly the
  predicted mechanism, but **n = 1 bearing**; KI21 and KA15 (also FAG) produce no verdicts at all. **No
  manufacturer-level claim is supported.** A geometry-pooled table (FAG raw outer precision 0.496 vs
  prevalence 0.500) exists in the analysis log and must not be presented without this row beside it.
- **Bearing-cluster bootstrap** (10,000 resamples of the 29 bearings): outer precision 95 % interval
  [0.03, 1.00] raw and [0.00, 1.00] cepstrum; precision − prevalence [−0.28, 0.66] and [−0.21, 0.71].
  **At the bearing level, H6 is uninformative in either direction.** The record-level Wilson intervals in §1
  treat 80 records of one bearing as 80 independent observations and are too narrow.

## 3. Consequences (logged as C56)

1. **Coverage is the binding constraint on claim 1.** Record-level outer recall is 0.15–0.18; bearing-level,
   the gate engages on 6/23 fault bearings. A gate that is silent on three quarters of faulty bearings supplies
   few pseudo-labels; M2/M3 must measure whether that helps or starves adaptation. This was the #1 risk; it
   is now measured, not hypothesised.
2. **Statistical unit.** Every real-data CI in the manuscript is reported at the physical-bearing level
   (cluster bootstrap) next to any record-level interval. Applies retroactively to H6 (both runs) and M4b.
3. **What H6 can still say, truthfully:** on the one real inner-race bearing whose geometry places 3·f_r
   inside the BPFO window, the raw gate calls it outer in 57/80 records and pre-whitening reduces that to 7/80;
   on the gate's healthy records, pre-whitening reduces false acceptance (18 → 15 → 9 of 480 across runs).
   That is a case study plus a false-alarm result, not a population-level precision claim.
