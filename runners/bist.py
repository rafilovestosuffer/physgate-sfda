"""BIST-W — class-conditional bearing-identity-adversarial source training (PROTOCOL C87, replacing C86).

C86's unconditional adversary was withdrawn before running: in the source set Y = g(B), so Z independent of B forces Z
independent of Y. BIST-W restricts the bearing-ID softmax to the source bearings of the sample's TRUE class (target property
Z independent of B given Y).

Injected into SDALR's source-training loop by the runner. A bearing-ID head sits on the feature extractor output behind a
gradient-reversal layer; its cross-entropy is added to the fault loss with the DANN schedule lambda(p) = LMAX*(2/(1+e^{-10p})-1).
Bearing IDs come from the source npz `bearing_id` field via the dataset line "npz|stem|index". Source-side only.
"""
from __future__ import annotations

import math

import numpy as np
import torch
import torch.nn as nn

LMAX = 1.0          # fixed by C86, never tuned
HIDDEN = 256
STATE: dict = {"bearings": {}, "labels": {}, "head": None, "opt": None, "vocab": None, "log": []}


class _GRL(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lam):
        ctx.lam = lam
        return x.view_as(x)

    @staticmethod
    def backward(ctx, g):
        return -ctx.lam * g, None


def register(stem: str, bearing_ids: np.ndarray, record_ids: np.ndarray | None = None, y: np.ndarray | None = None) -> None:
    STATE["bearings"][stem] = np.asarray(bearing_ids).astype(str)
    if y is not None:
        STATE["labels"][stem] = np.asarray(y).astype(int)
    if record_ids is not None:
        STATE.setdefault("records", {})[stem] = np.asarray(record_ids).astype(str)


def _ids(dataset, index: torch.Tensor) -> np.ndarray:
    out = []
    for i in index.tolist():
        _, stem, j = dataset.contents[int(i)][0].strip().split("|")
        out.append(STATE["bearings"][stem][int(j)])
    return np.asarray(out)


def _vocab(dataset) -> tuple[dict, torch.Tensor]:
    """Bearing vocabulary of THIS training dataset (source bearings only) and a class x bearing admissibility mask."""
    pairs = set()
    for line in dataset.contents:
        _, stem, j = line[0].strip().split("|")
        pairs.add((STATE["bearings"][stem][int(j)], int(STATE["labels"][stem][int(j)])))
    bearings = sorted({b for b, _ in pairs})
    cls_of = {}
    for b, c in pairs:
        if cls_of.setdefault(b, c) != c:
            raise SystemExit(f"REFUSED: bearing {b} carries two classes; BIST-W assumes Y = g(B)")
    vocab = {b: k for k, b in enumerate(bearings)}
    n_cls = max(cls_of.values()) + 1
    mask = torch.zeros(n_cls, len(vocab), dtype=torch.bool)
    for b, c in cls_of.items():
        mask[c, vocab[b]] = True
    return vocab, mask


def loss(features: torch.Tensor, index: torch.Tensor, dataset, iter_num: int, max_iter: int,
         labels: torch.Tensor | None = None) -> torch.Tensor:
    if labels is None:
        raise SystemExit("REFUSED: BIST-W needs the fault labels (class-conditional adversary, C87)")
    ids = _ids(dataset, index)
    f = features.flatten(1)
    if iter_num == 1 or STATE["vocab"] is None:     # each SDALR source domain trains from iter 1: fresh adversary + vocab
        STATE["vocab"], STATE["mask"] = _vocab(dataset)
        STATE["head"] = None
    vocab, mask = STATE["vocab"], STATE["mask"].to(f.device)
    y = torch.as_tensor([vocab[b] for b in ids], device=f.device)
    if STATE["head"] is None:
        STATE["head"] = nn.Sequential(nn.Linear(f.shape[1], HIDDEN), nn.ReLU(), nn.Linear(HIDDEN, len(vocab))).to(f.device)
        STATE["opt"] = torch.optim.Adam(STATE["head"].parameters(), lr=1e-3)
    p = iter_num / max(1, max_iter)
    lam = LMAX * (2.0 / (1.0 + math.exp(-10.0 * p)) - 1.0)
    logits = STATE["head"](_GRL.apply(f, lam))
    logits = logits.masked_fill(~mask[labels.long()], float("-inf"))   # softmax over same-class bearings only
    l = nn.functional.cross_entropy(logits, y)
    STATE["_pending"] = True
    if iter_num % 50 == 0:
        acc = float((logits.argmax(1) == y).float().mean())
        chance = float((1.0 / mask[labels.long()].sum(1).float()).mean())
        STATE["log"].append({"iter": iter_num, "lambda": round(lam, 3), "within_class_bearing_ce": float(l),
                             "within_class_bearing_acc": acc, "chance": round(chance, 3)})
    return l


def head_step() -> None:
    """Called after the main optimizer step: the head minimises bearing CE (the GRL already reversed it for features)."""
    if STATE.get("_pending") and STATE["opt"] is not None:
        STATE["opt"].step()
        STATE["opt"].zero_grad()
        STATE["_pending"] = False


SOURCE_PATCH_OLD = "            print_loss = final_classifier_loss\n            optimizer.zero_grad()\n            final_classifier_loss.backward()\n            optimizer.step()"
SOURCE_PATCH_NEW = ("            import bist as _bist  # PATCHED BIST-W (C87)\n"
                    "            final_classifier_loss = final_classifier_loss + _bist.loss(feature_src, _, dset_loaders['train'].dataset, iter_num, max_iter, labels_source)\n"
                    "            print_loss = final_classifier_loss\n            optimizer.zero_grad()\n"
                    "            if _bist.STATE['opt'] is not None: _bist.STATE['opt'].zero_grad()\n"
                    "            final_classifier_loss.backward()\n            optimizer.step()\n            _bist.head_step()")


def patch_source(src: str) -> str:
    if src.count(SOURCE_PATCH_OLD) != 1:
        raise SystemExit("REFUSED: BIST anchor not found exactly once in the SDALR source-training script")
    return src.replace(SOURCE_PATCH_OLD, SOURCE_PATCH_NEW)


def probe(networks, loader) -> dict:
    """C87 negative control N1 / mechanism check: is PHYSICAL BEARING ID linearly decodable from frozen source features?

    Record-disjoint halves (CRC32 parity of record_id). Reports (a) the all-bearing probe with its class-only ceiling and
    (b) within-class bearing probes (one per class, chance 1/n_c), at window level and record level (majority vote)."""
    import zlib
    from collections import Counter
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    feats, bids, rids, ys = [], [], [], []
    for net in networks:
        net.eval()
    with torch.no_grad():
        for data in loader:
            f = data[0].cuda()
            for net in networks[:-1]:
                f = net(f)
            feats.append(f.flatten(1).float().cpu().numpy())
            for i in data[-1].tolist():
                _, stem, j = loader.dataset.contents[int(i)][0].strip().split("|")
                bids.append(STATE["bearings"][stem][int(j)])
                rids.append(STATE["records"][stem][int(j)])
                ys.append(int(STATE["labels"][stem][int(j)]))
    for net in networks:
        net.train()
    X = np.concatenate(feats); B = np.asarray(bids); R = np.asarray(rids); Y = np.asarray(ys)
    te = np.asarray([zlib.crc32(r.encode()) % 2 for r in R]) == 1
    tr = ~te
    res = {"n_train": int(tr.sum()), "n_test": int(te.sum()), "n_bearings": int(len(set(B)))}
    if tr.sum() < 10 or te.sum() < 10:
        res["error"] = "insufficient split"
        STATE.setdefault("probes", []).append(res)
        return res

    def fit(mask_tr, mask_te):
        sc = StandardScaler().fit(X[mask_tr])
        clf = LogisticRegression(max_iter=2000).fit(sc.transform(X[mask_tr]), B[mask_tr])
        return clf.predict(sc.transform(X[mask_te]))

    def record_level(pred, mask_te):
        votes = {}
        for r, b, p_ in zip(R[mask_te], B[mask_te], pred):
            votes.setdefault(r, [b, Counter()])[1][p_] += 1
        return sum(v[0] == v[1].most_common(1)[0][0] for v in votes.values()), len(votes)

    pred = fit(tr, te)
    k, n = record_level(pred, te)
    n_per_class = {c: len(set(B[Y == c])) for c in set(Y.tolist())}
    res["all_bearings"] = {"window_acc": float((pred == B[te]).mean()), "record_correct": k, "record_n": n,
                           "chance": 1.0 / len(set(B)), "class_only_ceiling": float(np.mean([1.0 / n_per_class[c] for c in Y[te]]))}
    wk = wn = 0; wwin = []; chance_sum = 0.0
    per = {}
    for c, nc in n_per_class.items():
        mtr, mte = tr & (Y == c), te & (Y == c)
        if nc < 2 or mtr.sum() < 5 or mte.sum() < 5 or len(set(B[mtr])) < nc:
            per[int(c)] = {"skipped": True, "n_bearings": nc}
            continue
        pc = fit(mtr, mte)
        kc, ncr = record_level(pc, mte)
        per[int(c)] = {"n_bearings": nc, "window_acc": float((pc == B[mte]).mean()), "record_correct": kc, "record_n": ncr}
        wk += kc; wn += ncr; chance_sum += ncr / nc; wwin.append(float((pc == B[mte]).mean()))
    res["within_class"] = {"per_class": per, "record_correct": wk, "record_n": wn,
                           "pooled_chance": (chance_sum / wn if wn else None),
                           "record_acc": (wk / wn if wn else None), "mean_window_acc": (float(np.mean(wwin)) if wwin else None)}
    STATE.setdefault("probes", []).append(res)
    STATE["probe"] = res
    return res


PROBE_OLD = "\n    return networks\n"
PROBE_NEW = ("\n    import bist as _bist  # PATCHED probe (C87 N1)\n    print('BIST_PROBE', _bist.probe(networks, dset_loaders['test']))\n"
             "    return networks\n")


def patch_probe(src: str) -> str:
    if src.count(PROBE_OLD) != 1:
        raise SystemExit("REFUSED: probe anchor not found exactly once")
    return src.replace(PROBE_OLD, PROBE_NEW)
