### S3.1a Per-specimen geometry and damage, read from the Paderborn datasheets

All 32 specimens distributed with the dataset. Geometry is on page 1 of each
`data/pu/<bearing>/<bearing>.pdf`; damage mode and symptom are on page 2. Reproduce with
`python paper/make_s3_table.py`.

| Bearing | Manufacturer | Pitch (mm) | Balls | Ball dia (mm) | Damage mode | Symptom | Component | Used here |
|---|---|---|---|---|---|---|---|---|
| K001 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| K002 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| K003 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| K004 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| K005 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| K006 | IBU | 29.05 | 8 | 6.75 | healthy | -- | -- | yes |
| KA01 | MTK | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA03 | MTK | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA04 | FAG | 28.55 | 8 | 6.75 | fatigue | Pitting | OR | yes |
| KA05 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA06 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA07 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA08 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | AR | yes |
| KA09 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | OR | yes |
| KA15 | FAG | 28.55 | 8 | 6.75 | plastic deformation | particle-caused | OR | yes |
| KA16 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | OR | yes |
| KA22 | IBU / IBB | 29.05 | 8 | 6.75 | fatigue | Pitting | OR | yes |
| KA30 | MTK | 29.05 | 8 | 6.75 | plastic deformation | particle-caused | OR | yes |
| KB23 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | IR | no (double damage) |
| KB24 | FAG | 28.55 | 8 | 6.75 | fatigue | Pitting | IR | no (double damage) |
| KB27 | FAG | 28.55 | 8 | 6.75 | plastic deformation | particle-caused | OR | no (double damage) |
| KI01 | MTK | 29.05 | 8 | 6.75 | artificial | n/a | IR | yes |
| KI03 | MTK | 29.05 | 8 | 6.75 | artificial | n/a | IR | yes |
| KI04 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | IR | yes |
| KI05 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | IR | yes |
| KI07 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | IR | yes |
| KI08 | IBU | 29.05 | 8 | 6.75 | artificial | n/a | IR | yes |
| KI14 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | IR | yes |
| KI16 | FAG | 28.55 | 8 | 6.75 | fatigue | Pitting | IR | yes |
| KI17 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | IR | yes |
| KI18 | MTK | 29.05 | 8 | 6.75 | fatigue | Pitting | IR | yes |
| KI21 | FAG | 28.55 | 8 | 6.75 | fatigue | Pitting | IR | yes |

Summary: pitch 28.55 mm on 6 specimens; pitch 29.05 mm on 26 specimens. Every specimen has 8 rolling elements of 6.75 mm, so the two geometries differ only in pitch diameter,
giving outer-race orders 3.0706 (29.05 mm) and 3.0543 (28.55 mm).

