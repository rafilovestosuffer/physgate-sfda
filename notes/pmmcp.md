# notes/pmmcp.md — predictive-maintenance-mcp

**Status: [VERIFIED — repository read and data extracted]** 2026-09-13.
`github.com/LGDiMaggio/predictive-maintenance-mcp` (also on PyPI).

---

## 1. Headline: it contains a usable Smith & Randall stratification

**Human open item #1 is substantially discharged.** Two vendored files:

- `benchmarks/cwru/labels.json` — keyed by opaque id; each entry carries
  `fault_type`, `fault_diameter_in`, `or_position`, `known_anomalies`, **`sr2015_grade`**.
- `benchmarks/cwru/records_ops.json` — `opaque_id` → CWRU `file_id`, `url`, `fs_hz`,
  `nominal_rpm`, `load_hp`, `channel`, `internal_mat_key`.

Both pulled to `notes/_pmmcp_labels.json` and `notes/_pmmcp_records_ops.json`; merged into
`metadata/smith_randall_cwru.csv` (64 rows).

They are deliberately split as a blind-protocol trust boundary — `records.py` docstring:
*"the ops table carries no fault semantics, no stage upstream of the scorer can leak a label."*
That design is worth citing approvingly in our evaluation-protocol section.

## 2. Verified content of the stratification

64 records, all `channel = DE`; 60 at 12 kHz + 4 at 48 kHz; 60 fault + 4 normal.

```
GRADE DISTRIBUTION   Y1 9 | Y2 35 | P1 1 | P2 5 | N1 10 | N2 0 | normal(no grade) 4
                     Y1+Y2 = 44     P1+P2 = 6     N1+N2 = 10
```

Exactly reproduces the README's claim of 60 fault + 4 normal with 44 diagnosable.

**Grade × fault type — this is the important table:**

```
               Y1   Y2   P1   P2   N1   N2  none
ball            0    7    0    4    5    0    0     <-- 0 textbook, 5 NOT diagnosable
inner_race      4    8    0    0    4    0    0
outer_race      5   20    1    1    1    0    0
normal          0    0    0    0    0    0    4
```

**This is independent expert corroboration of our pre-registered prediction that the gate will be
weak on ball/roller — obtained before any experiment.** 0 of 16 ball records are textbook-grade and
5 of 16 are not diagnosable by any classical method, against 25/28 diagnosable for the outer race.
Put this table in the paper as prior justification for reporting ball separately.

Also flagged: `known_anomalies = clipping_de_sections` on 2 records — carry as a data-quality column.

## 3. Reported benchmark results (README)

- Characteristic fault frequency detected: **44/44 (100%)**
- Correct fault ranked first: **34/44 (77.3%)**
- Textbook-signature subset (Y1): **9/9**
- **False indications on healthy baselines: 2/4** — directly relevant to our false-alarm framing;
  a rule-based screen produces a 50% false-positive rate on healthy records here.
- Protocol: opaque ids, a separate scorer as sole label reader, checksum + determinism guards in CI.

## 4. Two constraints we must respect

1. **Licence: sample data CC BY-NC-SA 4.0** (non-commercial, share-alike). Our repo is academic, but
   `ShareAlike` is viral for derivative data. **Record this in `configs/datasets.yaml` and attribute
   the stratification explicitly.** Do not silently absorb it.
2. **Their grade is a single collapsed value, not per-method.** PLAN §4.1 requires `method1/method2/
   method3` (raw / discrete-random separation / spectral kurtosis). PMMCP gives one `sr2015_grade`.
   `metadata/smith_randall_cwru.csv` therefore keeps `sr2015_grade_pmmcp` **plus empty
   `method1..3` columns still to be filled from the paper.** Human item #1 is reduced, not removed —
   the per-method fidelity is what powers the H6 argument that Method 2 (DRS) is the best performer.

## 5. Differentiation for the paper

Cite and differentiate: theirs is a **rule-based expert screen on in-domain CWRU data**; ours is an
**SFDA-specific, FAR-controlled statistical gate evaluated under domain shift**. Their 2/4 healthy
false indications are a useful foil for our controlled false-acceptance framing.
