# Supplementary S3 — Dataset corrections and hygiene findings

These findings are independent of the adaptation experiments and are reported so that others can reuse the corrected values.

## S3.1 Paderborn uses two 6203 geometries

Per-bearing damage documentation gives pitch diameter 29.05 mm for the 26 IBU/MTK bearings and 28.55 mm for the 6 FAG bearings
(KA04, KA15, KB24, KB27, KI16, KI21), with 8 balls of 6.75 mm [src: the per-specimen datasheets themselves, tabulated in S3.1a]. The resulting outer-race orders are
3.0706 and 3.0543, against 3.0531 for CWRU's SKF 6203 that is commonly reused for Paderborn. A bearing designation is not a
geometry: every rig's own documentation must be used.

### S3.1a Per-specimen geometry and damage, read from the Paderborn datasheets

All 32 specimens distributed with the dataset. Geometry is on page 1 of each
`data/pu/<bearing>/<bearing>.pdf`; damage mode, symptom, component, size and combination are on page 2, one column
per damage (joined here with +). Combination: S single, R repetitive, M multiple damage. Reproduce with
`python paper/make_s3_table.py`.

| Bearing | Manufacturer | Pitch (mm) | Balls | Ball dia (mm) | Damages | Comb. | Damage mode | Symptom | Component | Length × width (mm) | Used here |
|---|---|---|---|---|---|---|---|---|---|---|---|
| K001 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| K002 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| K003 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| K004 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| K005 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| K006 | IBU | 29.05 | 8 | 6.75 | -- | -- | healthy | -- | -- | -- | yes |
| KA01 | MTK | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 0.25 × total | yes |
| KA03 | MTK | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 3 × 2 | yes |
| KA04 | FAG | 28.55 | 8 | 6.75 | 1 | S | fatigue | Pitting | OR | 2 × 3 | yes |
| KA05 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 1 × 1 | yes |
| KA06 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 3 × 3 | yes |
| KA07 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 0.9 × 0.9 | yes |
| KA08 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | AR | 2 × 2 | yes |
| KA09 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | OR | 3 × 3 | yes |
| KA15 | FAG | 28.55 | 8 | 6.75 | 1 | S | plastic deformation | particle-caused indentations | OR | <1 × <1 | yes |
| KA16 | MTK | 29.05 | 8 | 6.75 | 2 | R | fatigue + fatigue | Pitting + Pitting | OR + OR | 2 × total + 3 × total | yes |
| KA22 | IBU / IBB | 29.05 | 8 | 6.75 | 1 | S | fatigue | Pitting | OR | < 2 × 1 | yes |
| KA30 | MTK | 29.05 | 8 | 6.75 | 1 | R | plastic deformation | particle-caused indentations | OR | <1 × <1 | yes |
| KB23 | MTK | 29.05 | 8 | 6.75 | 3 | R | fatigue + fatigue + fatigue | Pitting + Pitting + Pitting | IR + IR + OR | 1.5 × 6 + 3 × 6 + 3 × 2 | no (double damage) |
| KB24 | FAG | 28.55 | 8 | 6.75 | 2 | M | fatigue + plastic deformation | Pitting + particle-caused indentations | IR + OR | 9.4 × total + <1 × <1 | no (double damage) |
| KB27 | FAG | 28.55 | 8 | 6.75 | 2 | M | plastic deformation + plastic deformation | particle-caused indentations + particle-caused indentations | OR + IR | <1 × <1 + <1 × <1 | no (double damage) |
| KI01 | MTK | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | IR | 0.25 × total | yes |
| KI03 | MTK | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | IR | < 2 × < 1 | yes |
| KI04 | MTK | 29.05 | 8 | 6.75 | 2 | M | fatigue + plastic deformation | Pitting + particle-caused indentations | IR + OR | 2 × 1 + n/a | yes |
| KI05 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | IR | 1 × 1 | yes |
| KI07 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | IR | 2.2 × 1 | yes |
| KI08 | IBU | 29.05 | 8 | 6.75 | 1 | S | artificial | n/a | IR | 3 × 1 | yes |
| KI14 | MTK | 29.05 | 8 | 6.75 | 2 | M | fatigue + plastic deformation | Pitting + particle-caused indentations | IR + OR | 1 × 1 + 1 × 1 | yes |
| KI16 | FAG | 28.55 | 8 | 6.75 | 1 | S | fatigue | Pitting | IR | 6 × total | yes |
| KI17 | MTK | 29.05 | 8 | 6.75 | 2 | R | fatigue + fatigue | Pitting + Pitting | IR + IR | 1 × 2 + 1 × 2 | yes |
| KI18 | MTK | 29.05 | 8 | 6.75 | 1 | S | fatigue | Pitting | IR | 2.5 × total | yes |
| KI21 | FAG | 28.55 | 8 | 6.75 | 1 | S | fatigue | Pitting | IR | 1 × 2 | yes |

Summary: pitch 28.55 mm on 6 specimens; pitch 29.05 mm on 26 specimens. Every specimen has 8 rolling elements of 6.75 mm, so the two geometries differ only in pitch diameter,
giving outer-race orders 3.0706 (29.05 mm) and 3.0543 (28.55 mm). Two specimens of the inner-race class carry a
second damage on the other ring (KI04 and KI14: particle-caused indentations on the outer ring, combination M);
the dataset classifies a specimen with several damages by its largest damage, here the inner-ring pitting.

### S3.1b Byte-identical vibration signals

Recordings of the healthy and real-damage specimens used here, at the three adaptation conditions, whose
`vibration_1` samples are byte-identical (SHA-256 of the stored samples). Each copy is a separate file and a
separate recording in the gate counts; all copies of a group belong to one bearing and so stay on one side of
every split.

| Recordings | SHA-256 of `vibration_1` |
|---|---|
| N15_M07_F04_KA04_15, N15_M07_F04_KA04_20, N15_M07_F04_KA04_6 | `339f4cf03c6daa8f85a7bb11543870f8c16e667a2fca3d68477859fef3bb82f3` |
| N15_M07_F04_KA04_19, N15_M07_F04_KA04_5 | `cd153ed41fb6f234b3f8014b7368e8c60e3932c398b5561a255f5ff708595df9` |


## S3.2 UORED-VAFCLS logged speed

The logged Hall reading disagrees with the cage-comb estimate by −5.2 % to +25 % in several files, and the strong spectral peak
near 29.7 Hz is not the shaft rate [src: results/b7_uored/B7_UORED_RESULT.md]. Speed on this rig is therefore treated as
unresolved: both arms are reported, six files are a declared sensitivity exclusion, and UORED is excluded from any analysis that
needs an independent speed (including the slip measurement of Supplementary S5).

## S3.3 CWRU cross-end contamination

Fan-end channels recorded during drive-end faults accept the correct **drive-end** fault family in 13 of 52 runs (25.0 %,
Wilson 95 % [15.2, 38.2]; bearing-cluster bootstrap [11.5, 40.4]), while the fan-end bearing's own families never fire
[src: results/b6a/B6A_RESULT.md]. Such signals should not be used as healthy data. This measures what Hendriks et al. and Vieira
et al. conservatively assume.

## S3.4 Within-CWRU control for the shaft-order lock (null)

Comparing fan-end (6203, lock-affected) with drive-end (6205, immune) recordings gave 6/33 versus 3/44 confusions,
one-sided Fisher p = 0.12, and 5 of the 6 fan-end confusions were not shaft-aliased [src: results/c78/C78_RESULT.md]. The
population-level effect is not supported, which is why Supplementary S5 rests on the direct slip measurement instead.

## S3.5 Blocked items

- HUST bearing: pitch diameter is unpublished, so no kinematics and no gates are computed for it. The HUST experiment in
  Section 6.3 uses raw windows only.
- JNU: roller count and roller diameter unpublished for the N205/NU205 pair; used for reproduction only.
