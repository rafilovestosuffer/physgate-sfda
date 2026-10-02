"""Backbones for Track A (C47, C60, C63). Input-adapted only; no architectural novelty is claimed.

resnet18_1d : 1D ResNet-18 in the ZhaoZhibin/UDTL style (BasicBlock x [2,2,2,2], widths 64-128-256-512,
              stem conv k=7 s=2 + maxpool, global average pool). Primary backbone for SFDA comparability.
wdcnn       : Zhang et al., Sensors 17(2):425 (2017): wide first-layer kernel (k=64, s=16, 16 filters), then
              four k=3 conv+BN+ReLU+maxpool(2) layers (32-64-64-64), FC-100. Second backbone (C60), selected by
              Vieira et al. 2026 on UORED.

Input adaptation rule (declared, identical for both): if the input length L < 1024 (spectral and KNEOS-HC
rungs), the stem is replaced by conv k=3 s=1 and the stem max-pool is removed, so a 45-sample KNEOS-HC axis
is not destroyed by the first layer. Nothing else changes.
"""
from __future__ import annotations

import torch
import torch.nn as nn

SHORT_INPUT = 1024


class BasicBlock1d(nn.Module):
    expansion = 1

    def __init__(self, cin, cout, stride=1):
        super().__init__()
        self.conv1 = nn.Conv1d(cin, cout, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm1d(cout)
        self.conv2 = nn.Conv1d(cout, cout, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm1d(cout)
        self.relu = nn.ReLU(inplace=True)
        self.down = None
        if stride != 1 or cin != cout:
            self.down = nn.Sequential(nn.Conv1d(cin, cout, 1, stride, bias=False), nn.BatchNorm1d(cout))

    def forward(self, x):
        idt = x if self.down is None else self.down(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return self.relu(out + idt)


class ResNet18_1d(nn.Module):
    def __init__(self, in_channels: int, length: int, n_classes: int):
        super().__init__()
        short = length < SHORT_INPUT
        self.stem = nn.Sequential(
            nn.Conv1d(in_channels, 64, 3 if short else 7, 1 if short else 2, 1 if short else 3, bias=False),
            nn.BatchNorm1d(64), nn.ReLU(inplace=True),
            nn.Identity() if short else nn.MaxPool1d(3, 2, 1))
        layers, cin = [], 64
        for cout, stride in ((64, 1), (128, 2), (256, 2), (512, 2)):
            layers += [BasicBlock1d(cin, cout, stride), BasicBlock1d(cout, cout, 1)]
            cin = cout
        self.body = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(512, n_classes)

    def features(self, x):
        return self.pool(self.body(self.stem(x))).flatten(1)

    def forward(self, x):
        return self.fc(self.features(x))


class WDCNN(nn.Module):
    def __init__(self, in_channels: int, length: int, n_classes: int):
        super().__init__()
        short = length < SHORT_INPUT
        stem = (nn.Conv1d(in_channels, 16, 3, 1, 1) if short else nn.Conv1d(in_channels, 16, 64, 16, 24))
        blocks = [stem, nn.BatchNorm1d(16), nn.ReLU(inplace=True), nn.MaxPool1d(2)]
        cin = 16
        for cout in (32, 64, 64, 64):
            blocks += [nn.Conv1d(cin, cout, 3, 1, 1), nn.BatchNorm1d(cout), nn.ReLU(inplace=True), nn.MaxPool1d(2, ceil_mode=True)]
            cin = cout
        self.body = nn.Sequential(*blocks)
        self.pool = nn.AdaptiveAvgPool1d(1)        # input-adaptation: global pool so any length maps to FC-100
        self.fc = nn.Sequential(nn.Linear(64, 100), nn.ReLU(inplace=True), nn.Linear(100, n_classes))

    def features(self, x):
        return self.pool(self.body(x)).flatten(1)

    def forward(self, x):
        return self.fc(self.features(x))


BACKBONES = {"resnet18_1d": ResNet18_1d, "wdcnn": WDCNN}


def receptive_field(model: nn.Module) -> int:
    """Exact 1D receptive field of the conv/pool stack along the main path (samples)."""
    rf, jump = 1, 1
    for m in model.modules():
        if isinstance(m, (nn.Conv1d, nn.MaxPool1d)):
            k = m.kernel_size[0] if isinstance(m.kernel_size, tuple) else m.kernel_size
            s = m.stride[0] if isinstance(m.stride, tuple) else m.stride
            if isinstance(m, nn.Conv1d) and k == 1:
                continue          # 1x1 downsample shortcuts do not widen the field
            rf += (k - 1) * jump
            jump *= s
    return rf


if __name__ == "__main__":
    for name, cls in BACKBONES.items():
        for c, L in ((1, 192000), (1, 2250), (13, 45)):
            m = cls(c, L, 3)
            y = m(torch.zeros(2, c, L))
            print(name, (c, L), tuple(y.shape), sum(p.numel() for p in m.parameters()), receptive_field(m))
