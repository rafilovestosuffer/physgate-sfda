"""Session-1 acceptance test 7. Must print Tesla T4 before ANYTHING else proceeds."""
import json, os, platform
out = {"device_name": None, "capability": None, "torch": None, "cuda": None, "python": platform.python_version()}
try:
    import torch
    out["torch"] = torch.__version__
    out["cuda"] = torch.version.cuda
    out["available"] = torch.cuda.is_available()
    if out["available"]:
        out["device_name"] = torch.cuda.get_device_name(0)
        out["capability"] = list(torch.cuda.get_device_capability(0))
        # The decisive check: P100 reports available=True then fails on the FIRST real op.
        x = torch.randn(256, 256, device="cuda")
        out["matmul_ok"] = bool(torch.isfinite((x @ x).sum()).item())
except Exception as e:  # noqa: BLE001
    out["error"] = f"{type(e).__name__}: {e}"
os.makedirs("/kaggle/working", exist_ok=True)
with open("/kaggle/working/hello_t4.json", "w") as fh:
    json.dump(out, fh, indent=2)
print(json.dumps(out, indent=2))
