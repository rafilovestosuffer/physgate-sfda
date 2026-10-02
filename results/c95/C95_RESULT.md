# C95 — gate-evaluation population and coverage by damage origin

Descriptive re-analysis of the retained per-record verdicts (`results/h7/h7_records.csv`, `results/comb_v2/v2_records.csv`). No new runs.

## Population

2319 recordings from 29 physical bearings at four operating conditions: 6 healthy, 11 real-damage and 12 artificial-damage. The adaptation experiments use the 11 real-damage bearings and 6 healthy bearings at three of the four conditions.

| damage origin | recordings, all 4 conditions | of which at the 3 adaptation conditions |
|---|---|---|
| healthy | 480 | 360 |
| real | 880 | 660 |
| artificial | 959 | 719 |

## Coverage at the pre-registered operating points

A bearing counts as engaged when at least one of its recordings receives the correct fault verdict.

| gate | healthy false acceptance | real: correct / records | real bearings engaged | artificial: correct / records | artificial bearings engaged |
|---|---|---|---|---|---|
| Envelope threshold rule | 1/480 | 209/880 | 7/11 | 157/959 | 6/12 |
| Shaft-alias-guarded comb | 0/480 | 151/880 | 5/11 | 161/959 | 4/12 |
| Surrogate-null comb test | 9/480 | 148/880 | 6/11 | 161/959 | 4/12 |
| Raw-spectrum band rule | 214/480 | 290/880 | 9/11 | 139/959 | 10/12 |

- **Envelope threshold rule** engages real-damage bearings KA04, KA15, KA16, KA30, KI16, KI18, KI21; artificial-damage bearings KA01, KA06, KA09, KI01, KI05, KI07.
- **Shaft-alias-guarded comb** engages real-damage bearings KA04, KA16, KI04, KI16, KI18; artificial-damage bearings KA01, KI01, KI05, KI07.
- **Surrogate-null comb test** engages real-damage bearings KA04, KA16, KI04, KI14, KI16, KI18; artificial-damage bearings KA01, KI01, KI05, KI07.
- **Raw-spectrum band rule** engages real-damage bearings KA04, KA15, KA16, KA30, KI04, KI14, KI16, KI17, KI18; artificial-damage bearings KA03, KA06, KA07, KA08, KA09, KI01, KI03, KI05, KI07, KI08.

## Reading

The gate study characterises safety on 480 real healthy recordings, which is the quantity that matters before a gate is trusted inside adaptation. Detection coverage, however, is not uniform across damage origin: the engaged-bearing counts above separate the artificial (EDM, drilling, manual indentation) bearings from the real fatigue and plastic-deformation damage used in the transfer experiments. Only the real-damage row bears on the gating results of the adaptation sections; the artificial bearings enter the safety study only.
