import pickle, json, numpy as np, yaml, collections
from pathlib import Path
from scipy.stats import wilcoxon, spearmanr, rankdata
from scipy.stats import t as tdist
ROOT = Path(r"C:\Users\Rafi\Desktop\claude research")
D = pickle.load(open("all.pkl", "rb")); K, F = D["k10"], D["fold"]
T = ["A1->A3", "A1->A2", "A3->A1", "A3->A2", "A2->A1", "A2->A3"]
SPL = [f"S{i:02d}" for i in range(10)]
cfg = yaml.safe_load(open(ROOT / "configs" / "splits_k10.yaml", encoding="utf-8"))["splits"]
NAMES = {0: "N", 1: "I", 2: "O"}
bear = lambda r: r.split("_")[3]


def purity(a, tasks=T):
    P = collections.defaultdict(list); L = {}
    for t in tasks:
        p = a["preds"][t]; bb = np.array([bear(r) for r in p["rec"]])
        for b in np.unique(bb):
            m = bb == b
            P[b].append(p["pred"][m]); L[b] = int(p["label"][m][0])
    out = {}
    for b, v in P.items():
        v = np.concatenate(v); c = np.bincount(v, minlength=3)
        out[b] = (c.max() / c.sum(), NAMES[int(c.argmax())], NAMES[L[b]], (v == L[b]).mean())
    return out


def per_task_purity(a):
    vals = []
    for t in T:
        p = a["preds"][t]; bb = np.array([bear(r) for r in p["rec"]])
        for b in np.unique(bb):
            m = bb == b; c = np.bincount(p["pred"][m], minlength=3)
            vals.append(c.max() / c.sum())
    return np.array(vals)


print("=== Q6 purity, ten splits (pooled over the six tasks of the split), SDALR ungated")
allc, alll = [], []
for s in SPL:
    for arm, key in (("clean", (s, s + "c", "none")), ("leaky", (s, s, "none"))):
        pu = purity(K[key]); v = np.array([x[0] for x in pu.values()])
        (allc if arm == "clean" else alll).extend(v)
        if arm == "clean":
            print(f"{s} clean: min {v.min():.3f} median {np.median(v):.3f}  n>=0.99: {(v >= 0.99).sum()}/{len(v)}  "
                  + " ".join(f"{b}:{x[0]:.2f}{x[1]}" for b, x in sorted(pu.items())))
    ptp = per_task_purity(K[(s, s + "c", "none")])
    print(f"      per-task-per-bearing purity clean: min {ptp.min():.3f} median {np.median(ptp):.3f}, share>=0.99 {np.mean(ptp >= 0.99):.2f}")
allc, alll = np.array(allc), np.array(alll)
print(f"ALL clean bearing-split pairs: n={len(allc)} median {np.median(allc):.3f} min {allc.min():.3f} share>=0.9995 {np.mean(allc >= 0.9995):.2f} share>=0.99 {np.mean(allc >= 0.99):.2f} share>=0.9 {np.mean(allc >= 0.9):.2f}")
print(f"ALL leaky bearing-split pairs: n={len(alll)} median {np.median(alll):.3f} min {alll.min():.3f} share>=0.99 {np.mean(alll >= 0.99):.2f}")
for tag, key in (("fold B dir (m2-fb ungated, src B tgt A)", ("m2-fb", "result_PU_M1_final_checkpoint_FBtoA_s2024")),
                 ("fold A dir (m2-fa ungated, src A tgt B)", ("m2-fa", "result_PU_M1_final_checkpoint_FAtoB_s2024")),
                 ("fold B dir PCV gate", ("m2-fb", "result_PU_M1_final_checkpoint_FBtoA_gatepcv_s2024")),
                 ("fold A dir PCV gate", ("m2-fa", "result_PU_M1_final_checkpoint_FAtoB_gatepcv_s2024"))):
    pu = purity(F[key])
    print(tag, " ".join(f"{b}:{x[0]:.3f}({x[1]}, true {x[2]})" for b, x in sorted(pu.items())))
a = F[("m2-fb", "result_PU_M1_final_checkpoint_FBtoA_gatepcv_s2024")]; b0 = F[("m2-fb", "result_PU_M1_final_checkpoint_FBtoA_s2024")]
print("fold B dir per-task ungated -> pcv:", [(t, b0["adapted"][t], a["adapted"][t]) for t in T])

print("\n=== Q8 within-bearing: accuracy when seen (leaky arm, bearing in source) vs unseen (clean arm)")
acc = collections.defaultdict(lambda: {"seen": [], "unseen": []})
for s in SPL:
    for arm, key in (("seen", (s, s, "none")), ("unseen", (s, s + "c", "none"))):
        a = K[key]
        for t in T:
            p = a["preds"][t]; bb = np.array([bear(r) for r in p["rec"]])
            for b in np.unique(bb):
                m = bb == b
                acc[b][arm].append((s, t, (p["pred"][m] == p["label"][m]).mean() * 100))
rows = []
for b in sorted(acc):
    se = np.mean([x[2] for x in acc[b]["seen"]]) if acc[b]["seen"] else np.nan
    un = np.mean([x[2] for x in acc[b]["unseen"]]) if acc[b]["unseen"] else np.nan
    ns = len({x[0] for x in acc[b]["seen"]}); nu = len({x[0] for x in acc[b]["unseen"]})
    rows.append((b, se, un, se - un, ns, nu))
    print(f"{b}: seen {se:6.2f} (in {ns} splits)  unseen {un:6.2f} (in {nu} splits)  diff {se - un:+6.2f}")
rows = [r for r in rows if np.isfinite(r[3])]
d = np.array([r[3] for r in rows])
print(f"median within-bearing diff {np.median(d):.2f} pp over {len(d)} bearings (mean {d.mean():.2f}); positive {int((d > 0).sum())}/{len(d)}; Wilcoxon one-sided p={wilcoxon(d, alternative='greater').pvalue:.2e}")
for cls in ("K0", "KA", "KI"):
    dd = np.array([r[3] for r in rows if r[0].startswith(cls)])
    print(f"  class {cls}: median {np.median(dd):.2f} n={len(dd)} values {np.round(dd, 1).tolist()}")

print("\n=== Q9 gate spillover: ten splits, clean arm, PCV-gated vs ungated, split by gate verdict of the window's record")
g = json.load(open(ROOT / "results" / "m2" / "gate_verdicts.json", encoding="utf-8"))["pcv"]
GR = ("cert", "uncov_faulty", "uncov_healthy")


def spill(u, gt):
    acc_ = {k: [0, 0, 0] for k in GR}
    for t in T:
        for j, a in ((1, u), (2, gt)):
            p = a["preds"][t]; v = np.array([g[r] for r in p["rec"]]); lab = p["label"]
            grp = np.where(v != "normal", "cert", np.where(lab == 0, "uncov_healthy", "uncov_faulty"))
            for k in acc_:
                m = grp == k
                if j == 1: acc_[k][0] += m.sum()
                acc_[k][j] += (p["pred"][m] == lab[m]).sum()
    return acc_


res = []
for s in SPL:
    acc_ = spill(K[(s, s + "c", "none")], K[(s, s + "c", "pcv")])
    r = {k: (v[0], 100 * v[1] / max(v[0], 1), 100 * v[2] / max(v[0], 1)) for k, v in acc_.items()}
    N = sum(v[0] for v in acc_.values())
    tot_u = sum(v[1] for v in acc_.values()) / N * 100; tot_g = sum(v[2] for v in acc_.values()) / N * 100
    res.append((s, r, tot_u, tot_g, N))
    print(f"{s}: total {tot_u:.2f}->{tot_g:.2f} ({tot_g - tot_u:+.2f}) | " + " | ".join(f"{k} n={v[0]} {v[1]:.1f}->{v[2]:.1f} ({v[2] - v[1]:+.1f})" for k, v in r.items()))
for k in GR:
    dd = np.array([x[1][k][2] - x[1][k][1] for x in res if x[1][k][0] > 0])
    print(f"  {k}: median within-group gain {np.median(dd):+.2f} pp, mean {dd.mean():+.2f}, positive {int((dd > 0).sum())}/{len(dd)}")
contrib = collections.defaultdict(list)
for s, r, tu, tg, N in res:
    for k, v in r.items(): contrib[k].append(v[0] * (v[2] - v[1]) / N)
for k, v in contrib.items():
    print(f"  contribution to split gain from {k}: median {np.median(v):+.2f} pp, mean {np.mean(v):+.2f}, per split {np.round(v, 2).tolist()}")
tot = sum(np.sum(v) for v in contrib.values())
print("  share of summed gain from uncovered windows:", round((np.sum(contrib['uncov_faulty']) + np.sum(contrib['uncov_healthy'])) / tot, 3))
print("  folds (gating job):")
for f, o in (("a", "B"), ("b", "A")):
    F_ = f.upper()
    acc_ = spill(F[(f"m2-f{f}", f"result_PU_M1_final_checkpoint_F{F_}to{o}_s2024")], F[(f"m2-f{f}", f"result_PU_M1_final_checkpoint_F{F_}to{o}_gatepcv_s2024")])
    print(f"   fold {F_}: " + " | ".join(f"{k} n={v[0]} {100 * v[1] / max(v[0], 1):.1f}->{100 * v[2] / max(v[0], 1):.1f}" for k, v in acc_.items()))

print("\n=== Q5 label-free coverage vs gain")
c98 = json.load(open(ROOT / "results" / "c98" / "c98_coverage.json"))["pcv_class"]
mean = lambda a: np.mean([a["adapted"][t] for t in T])
gain = {s: mean(K[(s, s + "c", "pcv")]) - mean(K[(s, s + "c", "none")]) for s in SPL}
head = {s: mean(K[(s, s + "c", "oracle")]) - mean(K[(s, s + "c", "none")]) for s in SPL}
cf = [c98[s]["spoke_share_faulty"] for s in SPL]; ca = [c98[s]["spoke_share"] for s in SPL]
gg = [gain[s] for s in SPL]; hh = [head[s] for s in SPL]
print(" faulty-denominator:", spearmanr(cf, gg))
print(" all-records (label-free):", spearmanr(ca, gg))
print(" records/faulty/spoke per split:", [(s, c98[s]["records"], c98[s]["faulty_records"], c98[s]["spoke"], round(c98[s]['spoke_share_faulty']*c98[s]['faulty_records'])) for s in SPL])


def partial(x, y, z):
    rx, ry, rz = (rankdata(v) for v in (x, y, z))
    ex = rx - np.polyval(np.polyfit(rz, rx, 1), rz); ey = ry - np.polyval(np.polyfit(rz, ry, 1), rz)
    return spearmanr(ex, ey), np.corrcoef(ex, ey)[0, 1]


print(" gain~headroom", spearmanr(hh, gg)); print(" cov~headroom", spearmanr(cf, hh))
print(" partial gain~cov|head (spearman of residuals; pearson of residuals):", partial(cf, gg, hh))
print(" partial gain~head|cov:", partial(hh, gg, cf))
r = lambda a, b: spearmanr(a, b)[0]


def pform(x, y, z):
    return (r(x, y) - r(x, z) * r(y, z)) / np.sqrt((1 - r(x, z) ** 2) * (1 - r(y, z) ** 2))


for nm, (x, y, z) in {"gain~cov|head": (cf, gg, hh), "gain~head|cov": (hh, gg, cf)}.items():
    pr = pform(x, y, z); n = 10; tt = pr * np.sqrt((n - 3) / (1 - pr ** 2)); p = 2 * tdist.sf(abs(tt), n - 3)
    print(f" textbook partial Spearman {nm}: {pr:.3f}, p(df=7) = {p:.2g}")
# leave-one-out robustness of rho
loo = [spearmanr(np.delete(cf, i), np.delete(gg, i))[0] for i in range(10)]
print(" leave-one-split-out rho range:", round(min(loo), 3), round(max(loo), 3))
# Pearson
print(" pearson cov-gain", np.corrcoef(cf, gg)[0, 1])
