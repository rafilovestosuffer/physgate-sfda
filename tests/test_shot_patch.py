"""SHOT patch (C85/C113): pseudo-labels must come back in DATASET order, whatever order a shuffled loader visits.

The C100 defect was exactly this: labels returned in traversal order, then indexed by dataset index in train_target.
The test feeds a shuffled loader whose traversal order differs from dataset order and checks every label by index.
"""
import importlib.util, io, pathlib, sys

import numpy as np
import pytest
import torch
import torch.nn as nn
from scipy.spatial.distance import cdist
from torch.utils.data import DataLoader, Dataset

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _load_patch():
    spec = importlib.util.spec_from_file_location("shot_patch", ROOT / "runners" / "shot_patch.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class _Toy(Dataset):
    """Sample i has class i % 3 and a feature vector pointing at its class axis. Returns (x, y, index) like SDALR."""
    def __init__(self, n=97, dim=3, seed=0):
        g = np.random.default_rng(seed)
        self.y = np.arange(n) % 3
        x = np.zeros((n, dim), dtype=np.float32)
        x[np.arange(n), self.y] = 10.0
        self.x = x + g.normal(0, 0.1, size=x.shape).astype(np.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        return torch.from_numpy(self.x[i]), int(self.y[i]), i


def _obtain_label():
    m = _load_patch()
    ns = {"torch": torch, "nn": nn, "np": np, "cdist": cdist}
    torch.Tensor.cuda = lambda self, *a, **k: self        # CPU: the patch calls .cuda() unconditionally
    exec(m.SHOT_CODE, ns)
    assert ns["SHOT_PATCH_VERSION"] >= 2, "stale SHOT patch (pre-C113)"
    return ns["obtain_label"]


class _Args:
    out_file = io.StringIO()


def test_pseudo_labels_are_in_dataset_order_under_a_shuffled_loader():
    obtain_label = _obtain_label()
    ds = _Toy()
    nets = [nn.Identity(), nn.Identity()]                   # features = logits = x
    torch.manual_seed(3)
    loader = DataLoader(ds, batch_size=16, shuffle=True, drop_last=False)
    visited = [int(i) for _, _, idx in loader for i in idx]
    assert visited != list(range(len(ds))), "loader must actually shuffle for this test to mean anything"
    lab = obtain_label(loader, nets, _Args())
    assert lab.shape == (len(ds),)
    np.testing.assert_array_equal(lab, ds.y)               # label i belongs to dataset sample i


def test_two_different_shuffles_give_identical_labels():
    obtain_label = _obtain_label()
    ds = _Toy()
    nets = [nn.Identity(), nn.Identity()]
    out = []
    for seed in (1, 2):
        torch.manual_seed(seed)
        out.append(obtain_label(DataLoader(ds, batch_size=10, shuffle=True), nets, _Args()))
    np.testing.assert_array_equal(out[0], out[1])


def test_incomplete_loader_pass_is_refused():
    obtain_label = _obtain_label()
    ds = _Toy(n=50)
    nets = [nn.Identity(), nn.Identity()]
    torch.manual_seed(0)
    with pytest.raises(RuntimeError, match="exactly once"):
        obtain_label(DataLoader(ds, batch_size=16, shuffle=True, drop_last=True), nets, _Args())
