# notes/data_findings.md — facts verified on the actual files

Session 2, 2026-09-13. Everything here was measured on downloaded data, not taken from papers.

---

## CWRU (64 records, checksum-verified against predictive-maintenance-mcp)

- DE vibration, `X###_DE_time`; **per-file RPM is stored** (`X###RPM`), so `rpm_source = measured_in_file`.
- ~121 k samples per fault record = 10.1 s at 12 kHz.
- **The 4 normal baselines are 48 kHz, not 12 kHz.** Filtering the subset to 12 kHz silently
  deletes the entire healthy class. The loader defaults to no fs filter and carries fs per record.
- Physical bearing identity: one seeded bearing per (fault location, size, outer-race position),
  re-run at loads 0–3 hp. **All four loads share a `bearing_id`** — the leak Hendriks et al. named.
  The healthy class is **one** physical bearing.

## Paderborn (32 bearings, SHA-256 recorded per archive in `data/pu/_provenance.json`)

- Archives are ~170 MB each, **~5.5 GB total** (not the ~20 GB previously estimated).
- 80 `.mat` per bearing = 4 conditions × 20 repetitions; `vibration_1` = 256,823 samples ≈ 4.01 s
  at 64 kHz.
- **Shaft speed is measured** (`speed`, 4 kHz raster). K001 measured 899.8 / 1499.6 rpm against
  nominal 900 / 1500.
- **But speed is constant to ±0.3 rpm (0.02 %) within a record.** → see Finding 3.

## JNU (12 CSVs, GitHub `ClarkGableWang/JNU-Bearing-Dataset`)

- 50 kHz, single column. **Fault recordings are 500,500 samples = 10.01 s; the normal recording is
  1,501,500 = 30.03 s.** Secondary sources' "20 s segments" is wrong for this distribution.
- **Exactly one recording per (class, speed).** → Finding 1.

## HUST (Mendeley v3 zip, 697 MB, SHA-256 e39f0cdb0d85...; CC BY 4.0)

- 99 files `<FAULT><MODEL>0<LOAD>` (e.g. `B502` = ball, 6205, 200 W). 57 single-fault records from
  19 physical bearings (assumed one per fault x model); no 6204 ball records exist.
- **`fs` is the per-file SHAFT FREQUENCY, not the sampling rate.** max(`rpm` trace) == fs*60 exactly
  (B602 1444.2 = 24.07*60). Speed falls with load: 0 W ~1,484-1,498 rpm, 200 W ~1,438-1,465, 400 W
  ~1,352-1,394. **Open item 4 resolved, per file.** The `rpm` trace itself is partly corrupt; unused.
- 12 files are short (down to 2.36 s); all 12 are compound faults. Every single-fault record >= 3 s.
- Parts are KG Bearing (India), not SKF. HUST's 6205 is registered separately and left UNVERIFIED.

---

## FINDING 1 — a leakage-safe JNU split does not exist

JNU provides one continuous recording per class per speed, so each fault class is a single physical
bearing. Every speed-transfer task SDALR reports (B1→B2 …, 98.50 % average) places the same physical
bearing on both sides, and any within-speed split cuts windows from one recording. **No bearing-wise
JNU table can be built.** JNU is therefore Track R only, and this is stated as a structural finding
alongside "PU's SDALR classes are bearing IDs". It is *stronger* than the PU case: PU can be relabelled
and re-split; JNU cannot.

## FINDING 2 — the RMS-shortcut hypothesis is NOT supported (negative result, recorded honestly)

Class amplitudes differ markedly (std 0.09 normal → 0.61 roller at 1000 rpm), which suggested a
trivial amplitude classifier might explain near-ceiling JNU accuracy. Tested with an RMS-only
nearest-centroid classifier on 2048-sample windows under SDALR's cross-speed task structure:

```
600→800 0.212   600→1000 0.169   800→600 0.532   800→1000 0.294   1000→600 0.504   1000→800 0.558
```

Chance is 0.25. RMS scales strongly with shaft speed, so centroids learned at one speed do not
transfer. **RMS alone does not explain SDALR's JNU results. Do not claim it does.** Finding 1 stands
on its own.

## FINDING 3 — the H4 order-tracking confound extends to Paderborn

PROTOCOL H4 declared that angular resampling is near-vacuous on CWRU (nominal RPM, no tacho) and
planned to test H4 "primarily on PU/JNU where speed is better characterised". PU does measure speed,
but the speed is constant to 0.02 % within a record, and JNU has no speed channel at all. **On all
four datasets, order tracking contributes essentially a per-record scalar rescale.** Its real effect
is normalising speed *across* conditions and machines (900 vs 1500 vs 1772 rpm). H4 must be
interpreted as "does geometry normalisation add anything beyond speed normalisation", not "beyond
order tracking" in the variable-speed sense. Logged as C26.
