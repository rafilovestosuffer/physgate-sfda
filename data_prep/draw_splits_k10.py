"""C88: draw K = 10 source bearing sets (3 healthy / 3 outer / 3 inner) uniformly without replacement, excluding M1 fold A."""
from itertools import combinations, product
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
H = ["K001", "K002", "K003", "K004", "K005", "K006"]
O = ["KA04", "KA15", "KA16", "KA22", "KA30"]
I = ["KI04", "KI14", "KI16", "KI17", "KI18", "KI21"]
FOLD_A = (("K001", "K002", "K003"), ("KA04", "KA15", "KA16"), ("KI04", "KI14", "KI16"))

draws = [d for d in product(combinations(H, 3), combinations(O, 3), combinations(I, 3)) if d != FOLD_A]
assert len(draws) == 3999
rng = np.random.default_rng(20260915)
pick = rng.choice(len(draws), size=10, replace=False)
out = {"rule": "C88: uniform without replacement over 4,000 3/3/3 draws minus M1 fold A, numpy default_rng(20260915)", "splits": {}}
for i, j in enumerate(pick):
    h, o, n = draws[j]
    src = {"normal": list(h), "outer_race": list(o), "inner_race": list(n)}
    tgt = {"normal": [b for b in H if b not in h], "outer_race": [b for b in O if b not in o], "inner_race": [b for b in I if b not in n]}
    assert not ({b for v in src.values() for b in v} & {b for v in tgt.values() for b in v})
    out["splits"][f"S{i:02d}"] = {"source": src, "target": tgt}
p = ROOT / "configs" / "splits_k10.yaml"
p.write_text(yaml.safe_dump(out, sort_keys=False), encoding="utf-8")
print(p.read_text())
