# B6a — CWRU cross-end contamination (PROTOCOL C52, wording C64): contamination MEASURABLE

Artifacts: `b6a_records.csv`, `b6a_summary.json`, `b6a_cluster_bootstrap.json`. 56 of 64 files carry an FE channel
(the eight 48 kHz-series files 3001–3008 do not). Fan-end channel, 5.0 s, cepstrum arm, frozen comb gate, α = 0.05.

| test | n | gate fires | rate [Wilson 95 %] | bearing-cluster bootstrap 95 % |
|---|---|---|---|---|
| **primary:** FE channel of DE-fault runs, DE (6205) kinematics, accepts the **true DE fault family** | 52 records / 13 bearings | **13** | **25.0 % [15.2, 38.2]** | [11.5, 40.4] |
| FE channel of DE-fault runs, DE kinematics, **wrong** family | 52 | 0 | 0 % | — |
| FE channel of DE-fault runs, **FE (6203) kinematics** — the FE bearing is healthy | 52 | 0 | 0 % [0, 6.9] | — |
| FE channel of normal runs (either kinematics) | 4 | 0 | 0 % [0, 49] | — |

Decision rule (C52): Wilson lower bound 15.2 % > α = 5 % → **cross-end contamination is measurable.** It holds
under bearing clustering (lower bound 11.5 %), and 7 of 13 fault bearings contribute. Ball faults: 0/12 (the gate
does not detect CWRU ball faults on the DE channel either, M4b). By type: inner 5/12, outer 8/28.

## Reading (C64 framing)

Vieira et al. exclude CWRU healthy signals recorded while the opposite-end bearing is faulty, on the grounds that
they *may* contain artifacts. **This measurement supports that exclusion**: in a quarter of drive-end-fault runs the
fan-end sensor carries a statistically detectable, kinematically correct drive-end fault signature, while its own
bearing's family is silent. Those signals should not be relabelled "healthy". Zero GPU hours.
