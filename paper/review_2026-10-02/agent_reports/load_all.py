"""Light loader: per-window preds + pre-update accuracy for k10 splits and folds. Read-only."""
import glob, json, re, os, pickle
import numpy as np, yaml
from pathlib import Path
ROOT = Path(r"C:\Users\Rafi\Desktop\claude research")
A = ROOT/"results"/"artifacts"
FILE2TASK = {"01":"A1->A3","02":"A1->A2","10":"A3->A1","12":"A3->A2","20":"A2->A1","21":"A2->A3"}
PRE = re.compile(r"批次:[·\s]*0/[·\s]*\d+;\s*总正确率:\s*([0-9.]+)%")

def pre_update(logdir):
    out = {}
    for f, t in FILE2TASK.items():
        p = Path(logdir)/f"adapt_{f}.log"
        if not p.exists(): continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        m = PRE.search(txt)
        if m: out[t] = float(m.group(1))
    return out

def preds(logdir):
    out = {}
    for f, t in FILE2TASK.items():
        p = Path(logdir)/f"pred_{f}.npz"
        if not p.exists(): continue
        d = np.load(p)
        out[t] = dict(pred=d["prob"].argmax(1), label=d["label"], rec=d["record_id"].astype(str))
    return out

def arm(result_json):
    d = json.load(open(result_json, encoding="utf-8"))
    logdir = Path(result_json).parent/("logs_" + Path(result_json).stem[len("result_"):])
    return dict(adapted=d["adapted"], pre=pre_update(logdir), preds=preds(logdir), path=str(result_json))

def main():
    D = {"k10":{}, "fold":{}, "shot_k10":{}}
    for p in glob.glob(str(A/"physgate-run-k10-*"/"k10"/"S*"/"result_PU_M1_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("smoke") or len(d["adapted"]) < 6: continue
        key = (d["src_fold"], d["tgt_fold"], d.get("gate") or "none")
        D["k10"][key] = arm(p)
    for p in glob.glob(str(A/"physgate-shot-k10-*"/"shot_k10"/"S*"/"result_PU_M1_*.json")):
        d = json.load(open(p, encoding="utf-8"))
        D["shot_k10"][(d["src_fold"], d["tgt_fold"])] = arm(p)
    for job in ("m1-fa","m1-fb","m2-fa","m2-fb"):
        for p in glob.glob(str(A/f"physgate-{job}"/"*"/"result_*.json")):
            D["fold"][(job, Path(p).stem)] = arm(p)
    for job in glob.glob(str(A/"physgate-m2seed-*"))+glob.glob(str(A/"physgate-m2rep-*")):
        for p in glob.glob(job+"/**/result_*.json", recursive=True):
            D["fold"][(Path(job).name, Path(p).stem)] = arm(p)
    for p in glob.glob(str(A/"physgate-shot-f*"/"**"/"result_*.json"), recursive=True):
        D["fold"][(Path(p).parts[-3] if 'shot' in Path(p).parts[-3] else Path(p).parts[-2], Path(p).stem)] = arm(p)
    pickle.dump(D, open("all.pkl","wb"))
    print({k: len(v) for k, v in D.items()})
    for k in sorted(D["fold"]): print(k, len(D["fold"][k]["pre"]), len(D["fold"][k]["preds"]))
main()
