#!/usr/bin/env bash
# SDALR is not redistributed here (no licence upstream). Fetch the exact commit used in the paper:
set -e
git clone https://github.com/BdLab405/SDALR.git third_party/SDALR
git -C third_party/SDALR checkout fb9c379cf72d87234a260521300c3c6aab2254b2
