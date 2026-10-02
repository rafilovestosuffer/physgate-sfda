"""Push a kernel to Kaggle. T4 IS ENFORCED IN CODE, NOT BY CONVENTION.

The P100 is compute capability sm_60 and current PyTorch wheels build for sm_70+:
torch.cuda.is_available() returns True and the FIRST CUDA OP FAILS with
"no kernel image is available for execution on the device" (Kaggle/docker-python issue #1546).
A silent P100 run wastes a 9-hour session, so any other accelerator exits non-zero WITHOUT pushing.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _cli

ALLOWED_ACCELERATOR = "NvidiaTeslaT4"


def build_metadata(slug: str, title: str, code_file: str, enable_gpu: bool,
                   dataset_sources: list[str], accelerator: str, enable_internet: bool = False) -> dict:
    if accelerator != ALLOWED_ACCELERATOR:
        raise SystemExit(
            f"REFUSED: accelerator={accelerator!r}. Only {ALLOWED_ACCELERATOR!r} is permitted.\n"
            "P100 is sm_60; current PyTorch requires sm_70+. The kernel would fail at the first "
            "CUDA op after burning session time. Nothing was pushed."
        )
    md = {
        "id": slug,
        "title": title,
        "code_file": code_file,
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": bool(enable_gpu),
        "enable_internet": bool(enable_internet),
        "dataset_sources": dataset_sources,
        "competition_sources": [],
        "kernel_sources": [],
    }
    if enable_gpu:
        md["accelerator"] = accelerator
    assert md.get("enable_gpu") is True or not enable_gpu, "enable_gpu must be true for GPU runs"
    return md


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--code", required=True, help="path to the script to run on Kaggle")
    p.add_argument("--name", required=True, help="kernel slug suffix, e.g. hello-t4")
    p.add_argument("--title", default=None)
    p.add_argument("--accelerator", default=ALLOWED_ACCELERATOR)
    p.add_argument("--no-gpu", action="store_true")
    p.add_argument("--internet", action="store_true", help="CPU kernels only: allow package installs (e.g. TeX Live)")
    p.add_argument("--dataset", action="append", default=[], help="owner/slug, repeatable")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--timeout-s", type=int, default=None, help="hard runtime cap passed to kaggle")
    a = p.parse_args()

    code = Path(a.code).resolve()
    if not code.exists():
        raise SystemExit(f"code file not found: {code}")

    user = _cli.username()
    slug = f"{user}/{a.name}"
    if a.internet and not a.no_gpu:
        raise SystemExit("REFUSED: --internet is for CPU kernels only")
    md = build_metadata(slug, a.title or a.name, code.name, not a.no_gpu, a.dataset, a.accelerator, a.internet)

    stage = Path(__file__).resolve().parents[1] / "runs" / "_push" / a.name
    stage.mkdir(parents=True, exist_ok=True)
    (stage / code.name).write_bytes(code.read_bytes())
    (stage / "kernel-metadata.json").write_text(json.dumps(md, indent=2), encoding="utf-8")

    print(f"staged {slug} -> {stage}")
    print(f"  accelerator={md.get('accelerator', 'none')} enable_gpu={md['enable_gpu']} private={md['is_private']}")
    if a.dry_run:
        print("dry-run: not pushing")
        return 0

    import preflight
    # CPU kernels (--no-gpu) may run beside a GPU kernel; the one-at-a-time guard protects GPU sessions only.
    if md["enable_gpu"] and not preflight.clear_to_push(user):
        raise SystemExit("REFUSED: a kernel is already queued or running. See kaggle/preflight.py")

    args = ["kernels", "push", "-p", str(stage)]
    if md["enable_gpu"]:
        # Pass the accelerator on the COMMAND LINE. The metadata field alone may be ignored by the
        # CLI, which would make the T4 enforcement cosmetic and silently fall back to P100.
        args += ["--accelerator", ALLOWED_ACCELERATOR]
    if a.timeout_s:
        args += ["-t", str(a.timeout_s)]
    cp = _cli.run(*args)
    print(cp.stdout.strip())
    print(f"pushed. poll with: python kaggle/poll.py --name {a.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
