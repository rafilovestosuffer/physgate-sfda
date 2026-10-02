# C97 — bearing identity from handcrafted features (probe baseline)

Same protocol as the N1 probe on learned features: one logistic-regression probe per class, record-disjoint halves (CRC32 parity of record_id), record-level majority vote. Features are the ten time-domain statistics used for the non-adaptive baseline, computed on the same 2048-sample windows.

| source fold | condition | within-class record accuracy |
|---|---|---|
| A | N15_M01_F10 | 92/92 = 1.000 |
| A | N15_M07_F04 | 88/88 = 1.000 |
| A | N15_M07_F10 | 91/91 = 1.000 |
| B | N15_M01_F10 | 81/81 = 1.000 |
| B | N15_M07_F04 | 79/79 = 1.000 |
| B | N15_M07_F10 | 77/77 = 1.000 |

**Pooled: 508/508 = 1.000 against a pooled chance of 0.353 (one-sided binomial p = 1.91e-230).**

Learned source features (N1): 507/508 = 0.998 on the same protocol.

## Reading

Bearing identity is decodable within a class from ten elementary signal statistics alone, so the shortcut is present in the recordings and is not manufactured by the adaptation method: any classifier trained on a handful of physical bearings can separate the source classes by specimen. This is consistent with the non-adaptive random forests collapsing exactly like the adapted models, and it explains why an adaptation objective cannot remove the shortcut: the objective never sees a reason to prefer fault physics over identity.
