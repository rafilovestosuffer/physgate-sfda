"""M0 runner: SDALR's released code, run UNMODIFIED except for three declared, auditable adapters.

  1. I/O adapter  -- `data_list.txt_loader` reads a window from our M0 .npz instead of a text file.
                     Numerical pipeline (z-score, augmentation, voting, losses) untouched.
  2. Plot stub    -- `plot_t_SNE.prepare_dicts/plot_test_target` become no-ops. They run AFTER the
                     reported accuracy is computed and only produce figures.
  3. Variant patch (ONLY for --variant final_checkpoint) -- the single line
                         if acc_t_te > acc_init:
                     becomes `if True:` so the checkpoint reloaded at the end is the final iterate
                     rather than the one with the best TARGET-LABEL accuracy (audit A1). The line must
                     occur exactly once, or the runner refuses to patch.

Each (source, target) pair runs in a FRESH model load: the released scripts adapt `source_networks`
in place, so `--t -1` would chain targets (audit A7). The released shell script avoids this by
launching one process per pair; we do the same by calling read_model per pair.

Usage:
  python runners/sdalr_runner.py --sdalr third_party/SDALR --m0 data/m0 --dataset JNU \
      --variant as_released --work runs/m0 [--pairs 0,1 1,0] [--seed 2024] [--smoke]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import runpy
import shutil
import sys
import time
from pathlib import Path

import numpy as np

CFG = {
    "PU": {"data_name": "PU_1d_8c_2048", "username": "NEW_PU", "class_num": 8,
           # CODE order (audit A3): index 1 = N15_M07_F10 (paper A3), index 2 = N15_M07_F04 (paper A2)
           "domains": ["N15_M01_F10", "N15_M07_F10", "N15_M07_F04"],
           "npz": {"N15_M01_F10": "PU_N15_M01_F10", "N15_M07_F10": "PU_N15_M07_F10",
                   "N15_M07_F04": "PU_N15_M07_F04"},
           "paper_label": {"N15_M01_F10": "A1", "N15_M07_F04": "A2", "N15_M07_F10": "A3"},
           "pretrain": "src_pretrain_RES_PU.py", "adapt": "tar_adaptation_RES_PU.py"},
    "JNU": {"data_name": "JNU_1d_2048_2000", "username": "NEW_JNU", "class_num": 4,
            "domains": ["600", "800", "1000"],
            "npz": {"600": "JNU_600rpm", "800": "JNU_800rpm", "1000": "JNU_1000rpm"},
            "paper_label": {"600": "B1", "800": "B2", "1000": "B3"},
            "pretrain": "src_pretrain_RES_JNU.py", "adapt": "tar_adaptation_RES_JNU.py"},
    # M1 (PROTOCOL C32): PU relabelled to L3, bearing folds from configs/splits.yaml. Same code order as PU.
    "PU_M1": {"data_name": "PU_M1_L3", "username": "NEW_PU", "class_num": 3,  # username must match the script default
              "domains": ["N15_M01_F10", "N15_M07_F10", "N15_M07_F04"],
              "npz_template": "PU_M1_fold{fold}_{dom}",
              "paper_label": {"N15_M01_F10": "A1", "N15_M07_F04": "A2", "N15_M07_F10": "A3"},
              "pretrain": "src_pretrain_RES_PU.py", "adapt": "tar_adaptation_RES_PU.py"},
    # C94: HUST bearing (Hanoi), L3, one physical bearing (type) per class per file; domains are the three loads.
    # Domain KEYS reuse the PU script's own names (the released PU scripts hard-code them); they map to HUST loads
    # N15_M01_F10 = 0 W (H1), N15_M07_F10 = 400 W (H3), N15_M07_F04 = 200 W (H2), keeping PU's code order.
    "HUST_M1": {"data_name": "HUST_M1_L3", "username": "NEW_PU", "class_num": 3,
                "domains": ["N15_M01_F10", "N15_M07_F10", "N15_M07_F04"],
                "npz_template": "HUST_M1_fold{fold}_{dom}",
                "paper_label": {"N15_M01_F10": "H1", "N15_M07_F04": "H2", "N15_M07_F10": "H3"},
                "pretrain": "src_pretrain_RES_PU.py", "adapt": "tar_adaptation_RES_PU.py"},
}
# SDALR's released hyperparameters (choose_s_t_*.sh). Paper states threshold 0.6; the script uses 0.4 (audit A4).
RELEASED = {"lr": "0.0005", "threshold": "0.4", "K": "0.6"}
SELECTION_LINE = "if acc_t_te > acc_init:"

_ARRAYS: dict[str, np.ndarray] = {}
_RECORDS: dict[str, np.ndarray] = {}       # stem -> per-window record_id (C81 gate join)
_GATE: dict = {"mode": "none", "verdicts": {}, "calls": [], "last_eval": None}
CLASS_INDEX = {"normal": 0, "inner_race": 1, "outer_race": 2}


def _npz_loader(path: str):
    """Replacement for data_list.txt_loader. Paths look like  npz|<stem>|<index>."""
    _, stem, idx = path.strip().split("|")
    return _ARRAYS[stem][int(idx)].astype(np.float64)


class Tee(io.TextIOBase):
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def prepare_code(sdalr: Path, work: Path, dataset: str, variant: str, bist: bool = False, probe: bool = False) -> Path:
    code = work / f"sdalr_{dataset}_{variant}{'_bist' if bist else ''}{'_probe' if probe else ''}"
    dataset = dataset.split("_bist")[0]
    if code.exists():
        shutil.rmtree(code)
    shutil.copytree(sdalr, code, ignore=shutil.ignore_patterns(".git", "fig", "weight", "DATA"))
    if bist or probe:                        # C86: bearing-identity-adversarial source training / identity probe
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import bist as _bist
        p = code / CFG[dataset]["pretrain"]
        src = p.read_text(encoding="utf-8")
        if bist:
            src = _bist.patch_source(src)
        p.write_text(_bist.patch_probe(src), encoding="utf-8")
        shutil.copy(Path(__file__).resolve().parent / "bist.py", code / "bist.py")
    if variant == "shot":                    # C85: SHOT losses on SDALR's backbone/data, last iterate
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import shot_patch
        p = code / CFG[dataset]["adapt"]
        p.write_text(shot_patch.patch(p.read_text(encoding="utf-8")), encoding="utf-8")
    if variant == "final_checkpoint":
        p = code / CFG[dataset]["adapt"]
        src = p.read_text(encoding="utf-8")
        n = src.count(SELECTION_LINE)
        if n != 1:
            raise SystemExit(f"REFUSED: expected exactly 1 occurrence of '{SELECTION_LINE}' in {p.name}, found {n}")
        p.write_text(src.replace(SELECTION_LINE, "if True:  # PATCHED final_checkpoint (was: acc_t_te > acc_init)"),
                     encoding="utf-8")
    return code


def prepare_data(m0: Path, code: Path, dataset: str, fold: str | None = None) -> Path:
    """Write SDALR label files for one data VIEW. For PU_M1 a view is one bearing fold."""
    cfg = CFG[dataset]
    root = code / ("DATA" if fold is None else f"DATA_fold{fold}")
    folder = root / cfg["data_name"]
    folder.mkdir(parents=True, exist_ok=True)
    for dom in cfg["domains"]:
        stem = cfg["npz"][dom] if fold is None else cfg["npz_template"].format(fold=fold, dom=dom)
        d = np.load(m0 / f"{stem}.npz", allow_pickle=False)
        _ARRAYS[stem] = d["X"]
        if "record_id" in d.files:
            _RECORDS[stem] = d["record_id"]
        if "bearing_id" in d.files:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import bist as _bist
            _bist.register(stem, d["bearing_id"], d["record_id"] if "record_id" in d.files else None, d["y"])
        lines = [f"npz|{stem}|{i} {int(y)}\n" for i, y in enumerate(d["y"])]
        (folder / f"{dom}_label.txt").write_text("".join(lines), encoding="utf-8")
    return root


def install_adapters(code: Path, smoke: bool) -> None:
    import locale, os
    if os.name == "nt":  # Windows only: SDALR formats dates with CJK characters; C locale cannot encode them
        locale.setlocale(locale.LC_ALL, ".UTF8")
    sys.path.insert(0, str(code))
    import torch
    if smoke:  # CPU-only smoke test: SDALR calls .cuda() unconditionally
        torch.Tensor.cuda = lambda self, *a, **k: self
        torch.nn.Module.cuda = lambda self, *a, **k: self
        _orig_load = torch.load
        torch.load = lambda *a, **k: _orig_load(*a, **{**k, "map_location": "cpu"})
    import data_list
    data_list.txt_loader = _npz_loader
    import numpy as _np
    import text, tools
    _orig_kk = text.kk

    def gated_kk(args, loader, result, networks, fea_bank, score_bank):
        """C81 hook: runs after tools.check_columns formed `result` (-1 = SDALR rejection)."""
        mode = _GATE["mode"]
        if mode != "none":
            result = _np.asarray(result).copy()
            before = result.copy()
            paths = [c[0] for c in loader.dataset.contents]
            truth = _np.asarray([int(c[1]) for c in loader.dataset.contents])
            recs = []
            for pth in paths:
                _, stem, idx = pth.strip().split("|")
                recs.append(str(_RECORDS[stem][int(idx)]))
            if mode == "oracle":
                keep = result == truth
            else:
                v = _np.asarray([CLASS_INDEX.get(_GATE["verdicts"].get(r, "normal"), 0) for r in recs])
                speaks = v > 0
                keep = ~speaks | (result == v)
            result[(~keep) & (result != -1)] = -1
            kept = before != -1
            _GATE["calls"].append({
                "sdalr_rejected": int((before == -1).sum()), "hook_rejected": int(((before != -1) & (result == -1)).sum()),
                "precision_before": float((before[kept] == truth[kept]).mean()) if kept.any() else None,
                "precision_after": float((result[result != -1] == truth[result != -1]).mean()) if (result != -1).any() else None,
                "n": int(result.size)})
            _GATE["last_masks"] = {"before": before, "after": result, "records": _np.asarray(recs), "truth": truth}
        return _orig_kk(args, loader, result, networks, fea_bank, score_bank)
    text.kk = gated_kk
    _orig_cal = tools.cal_acc

    def recording_cal_acc(loader, networks):
        import torch
        outs, idxs, labs = [], [], []
        with torch.no_grad():
            for data in loader:
                o = data[0].cuda()
                for net in networks:
                    o = net(o)
                outs.append(torch.softmax(o.float(), 1).cpu()); labs.append(data[1]); idxs.append(data[-1])
        I = torch.cat(idxs).numpy()
        recs = []
        for i in I:
            _, stem, j = loader.dataset.contents[int(i)][0].strip().split("|")
            recs.append(str(_RECORDS[stem][int(j)]) if stem in _RECORDS else "")
        _GATE["last_eval"] = {"prob": torch.cat(outs).numpy(), "index": I, "label": torch.cat(labs).numpy(),
                              "record_id": _np.asarray(recs)}
        return _orig_cal(loader, networks)
    tools.cal_acc = recording_cal_acc
    import plot_t_SNE
    plot_t_SNE.prepare_dicts = lambda *a, **k: ({}, {}, {}, {})
    plot_t_SNE.plot_test_target = lambda *a, **k: None


def run_script(code: Path, script: str, argv: list[str], log: Path) -> str:
    buf = io.StringIO()
    old_argv = sys.argv
    sys.argv = [script, *argv]
    t0 = time.time()
    with open(log, "w", encoding="utf-8") as fh, contextlib.redirect_stdout(Tee(sys.__stdout__, fh, buf)):
        try:
            runpy.run_path(str(code / script), run_name="__main__")
        finally:
            sys.argv = old_argv
    out = buf.getvalue()
    print(f"[{script} {' '.join(argv)}] {time.time() - t0:.0f}s", flush=True)
    return out


ADAPT_RE = re.compile(r"测试集任务:\s*\(B(\d)\)(\S+?)→\(B(\d)\)(\S+?);\s*总正确率\s*=\s*([\d.]+)%")
SRC_ONLY_RE = re.compile(r"任务:\s*\(B(\d)\)(\S+?)→\(B(\d)\)(\S+?),\s*正确率\s*=\s*([\d.]+)%")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sdalr", required=True)
    ap.add_argument("--m0", required=True)
    ap.add_argument("--dataset", choices=["PU", "JNU", "PU_M1", "HUST_M1"], required=True)
    def view(v):
        if not re.fullmatch(r"A|B|S\d\dc?|H\dc?", v):
            raise argparse.ArgumentTypeError(f"bad view {v}")
        return v
    ap.add_argument("--src-fold", type=view, default=None, help="PU_M1: source view (M1 fold A/B or C88 split Sxx)")
    ap.add_argument("--tgt-fold", type=view, default=None, help="PU_M1: target view (A/B, Sxx leaky, Sxxc clean)")
    ap.add_argument("--variant", choices=["as_released", "final_checkpoint", "shot"], required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--pairs", nargs="*", default=None, help="code-index pairs like 0,1 (default all 6)")
    ap.add_argument("--seed", type=int, default=2024)
    ap.add_argument("--smoke", action="store_true", help="CPU, tiny: --num 8 per class, 1 epoch")
    ap.add_argument("--skip-pretrain", action="store_true")
    ap.add_argument("--threshold", default=RELEASED["threshold"], help="reliability threshold (script 0.4, paper 0.6; audit A4)")
    ap.add_argument("--gate", choices=["none", "c30", "v2", "pcv", "eagle", "oracle"], default="none", help="C81 arm")
    ap.add_argument("--gate-verdicts", default=None, help="json record_id -> class, per gate (C81)")
    ap.add_argument("--bist", action="store_true", help="C87 BIST-W class-conditional bearing adversary in source training")
    ap.add_argument("--probe", action="store_true", help="C87 N1 bearing-ID probes (all-bearing and within-class) on the source model")
    ap.add_argument("--pretrain-only", action="store_true", help="stop after source training (N1 probe runs)")
    a = ap.parse_args()

    cfg = CFG[a.dataset]
    work = Path(a.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    m1 = a.dataset in ("PU_M1", "HUST_M1")
    if m1 and (a.src_fold is None or a.tgt_fold is None):
        raise SystemExit(f"{a.dataset} requires --src-fold and --tgt-fold")
    tag = f"_F{a.src_fold}to{a.tgt_fold}" if m1 else ""
    hp = dict(RELEASED, threshold=str(a.threshold))
    if hp["threshold"] != RELEASED["threshold"]:
        tag += f"_thr{hp['threshold']}"
    if a.gate != "none":
        tag += f"_gate{a.gate}"
    code = prepare_code(Path(a.sdalr).resolve(), work, a.dataset + tag, a.variant, a.bist, a.probe) if not m1 else         prepare_code(Path(a.sdalr).resolve(), work, "PU", a.variant, a.bist, a.probe)
    if m1:
        src_view = prepare_data(Path(a.m0).resolve(), code, a.dataset, a.src_fold)
        tgt_view = prepare_data(Path(a.m0).resolve(), code, a.dataset, a.tgt_fold)
    else:
        src_view = tgt_view = prepare_data(Path(a.m0).resolve(), code, a.dataset)
    install_adapters(code, a.smoke)
    _GATE["mode"] = a.gate
    if a.gate not in ("none", "oracle"):
        _GATE["verdicts"] = json.loads(Path(a.gate_verdicts).read_text(encoding="utf-8"))[a.gate]

    import os
    os.chdir(code)
    # ONE source model per (dataset, seed), shared by both variants, so the as_released vs
    # final_checkpoint gap isolates model selection and is not confounded by source-training noise.
    # For PU_M1 the source model depends only on the SOURCE fold, so leaky (F->F) and clean (F->F') targets
    # adapt the identical source model -- the paired design of C32.
    src_tag = f"_F{a.src_fold}" if m1 else ""
    if a.bist:
        src_tag += "_bist"; tag += "_bist"
    src_root = work / f"weight_src_{a.dataset}{src_tag}_s{a.seed}"
    tgt_root = work / f"weight_{a.dataset}_{a.variant}{tag}_s{a.seed}"
    cls = ["--class_num", str(cfg["class_num"]), "--data_name", cfg["data_name"]]
    base_src = ["--folder_root", str(src_view), "--seed", str(a.seed)] + cls
    base_tgt = ["--folder_root", str(tgt_view), "--seed", str(a.seed)] + cls
    small = ["--num", "40", "--max_epoch", "2"] if a.smoke else []  # >= 4 iters so max_iter // interval > 0
    logs = work / f"logs_{a.dataset}_{a.variant}{tag}_s{a.seed}"
    logs.mkdir(exist_ok=True)
    outp = work / f"result_{a.dataset}_{a.variant}{tag}_s{a.seed}{'_smoke' if a.smoke else ''}.json"

    result = {"dataset": a.dataset, "variant": a.variant, "seed": a.seed, "smoke": a.smoke,
              "src_fold": a.src_fold, "tgt_fold": a.tgt_fold,
              "leaky": (a.src_fold == a.tgt_fold) if m1 else True,
              "hyperparameters": hp,
              "adapters": ["npz_io", "tsne_stub"] + (["final_checkpoint_patch"] if a.variant == "final_checkpoint" else []) + (["shot_patch"] if a.variant == "shot" else []),
              "source_only": {}, "adapted": {}, "seconds": {}}
    if outp.exists():
        result.update({k: v for k, v in json.loads(outp.read_text(encoding="utf-8")).items() if k in ("source_only", "adapted", "seconds")})

    def flush():
        outp.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    src_dir = src_root / cfg["username"] / "Source-源域"
    if not a.skip_pretrain and not src_dir.exists():
        t0 = time.time()
        out = run_script(code, cfg["pretrain"], base_src + ["--output", str(src_root)] + small, logs / "pretrain.log")
        for m in SRC_ONLY_RE.finditer(out):
            s_dom, t_dom = m.group(2), m.group(4)
            key = f"{cfg['paper_label'].get(s_dom, s_dom)}->{cfg['paper_label'].get(t_dom, t_dom)}"
            result["source_only"][key] = float(m.group(5))
        result["seconds"]["pretrain"] = round(time.time() - t0)
        if a.bist or a.probe:
            import bist as _bist
            result["bist"] = {"enabled": a.bist, "log": _bist.STATE["log"], "probes": _bist.STATE.get("probes", [])}
        flush()
    if not src_dir.exists():
        raise SystemExit(f"no source model at {src_dir}; run without --skip-pretrain first")
    if a.pretrain_only:
        flush()
        print("pretrain-only: stopping after source training", flush=True)
        return 0
    dst = tgt_root / cfg["username"] / "Source-源域"
    if not dst.exists():
        shutil.copytree(src_dir, dst)

    pairs = [tuple(map(int, p.split(","))) for p in a.pairs] if a.pairs else         [(s, t) for s in range(3) for t in range(3) if s != t]
    for s, t in pairs:
        pair_key = f"{cfg['paper_label'][cfg['domains'][s]]}->{cfg['paper_label'][cfg['domains'][t]]}"
        if pair_key in result["adapted"]:
            print(f"skip {pair_key}: already done", flush=True)
            continue
        t0 = time.time()
        argv = base_tgt + ["--output", str(tgt_root)] + small + ["--s", str(s), "--t", str(t),
               "--lr", RELEASED["lr"], "--threshold", hp["threshold"], "--K", hp["K"]]
        out = run_script(code, cfg["adapt"], argv, logs / f"adapt_{s}{t}.log")
        hits = ADAPT_RE.findall(out)
        if not hits:
            raise RuntimeError(f"no final accuracy parsed for pair {s},{t}; see {logs / f'adapt_{s}{t}.log'}")
        _, s_dom, _, t_dom, acc = hits[-1]
        key = f"{cfg['paper_label'].get(s_dom, s_dom)}->{cfg['paper_label'].get(t_dom, t_dom)}"
        assert key == pair_key, f"parsed {key} but ran {pair_key}"
        result["adapted"][key] = float(acc)
        ev = _GATE.get("last_eval")
        if ev is not None:
            np.savez_compressed(logs / f"pred_{s}{t}.npz", prob=ev["prob"], index=ev["index"], label=ev["label"],
                                record_id=ev["record_id"],
                                hook_calls=json.dumps(_GATE["calls"]),
                                **({f"mask_{k}": v for k, v in _GATE["last_masks"].items()} if "last_masks" in _GATE else {}))
            result.setdefault("gate_log", {})[key] = _GATE["calls"]
        _GATE["calls"] = []; _GATE.pop("last_masks", None); _GATE["last_eval"] = None
        result["gate"] = a.gate
        result["seconds"][key] = round(time.time() - t0)
        flush()   # incremental: a killed session keeps every finished task

    flush()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
