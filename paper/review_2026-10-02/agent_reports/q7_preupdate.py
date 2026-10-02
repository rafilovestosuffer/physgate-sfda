import pickle, numpy as np
from scipy.stats import wilcoxon
D = pickle.load(open("all.pkl","rb"))
T = ["A1->A3","A1->A2","A3->A1","A3->A2","A2->A1","A2->A3"]
K, F = D["k10"], D["fold"]
m = lambda a, k: np.mean([a[k][t] for t in T])
print("== Pre-update identical across clean arms (none/pcv/oracle) within each split?")
bad = 0
for s in [f"S{i:02d}" for i in range(10)]:
    for t in T:
        vals = {g: K[(s, s+"c", g)]["pre"][t] for g in ("none","pcv","oracle")}
        if len(set(vals.values())) != 1: bad += 1; print("  mismatch", s, t, vals)
print("  mismatches:", bad)
print("\n== Ten splits: source-only (pre-update) vs adapted, SDALR final_checkpoint seed 2024")
print("split | pre_leaky pre_clean preD | adp_leaky adp_clean adpD | adpD-preD | clean adapt gain | leaky adapt gain")
rows = []
for s in [f"S{i:02d}" for i in range(10)]:
    L, C = K[(s, s, "none")], K[(s, s+"c", "none")]
    pl, pc, al, ac = m(L,"pre"), m(C,"pre"), m(L,"adapted"), m(C,"adapted")
    rows.append((pl, pc, al, ac))
    print(f"{s} | {pl:.2f} {pc:.2f} {pl-pc:.2f} | {al:.2f} {ac:.2f} {al-ac:.2f} | {(al-ac)-(pl-pc):+.2f} | {ac-pc:+.2f} | {al-pl:+.2f}")
r = np.array(rows); pre_d = r[:,0]-r[:,1]; adp_d = r[:,2]-r[:,3]; amp = adp_d-pre_d
print(f"median preD {np.median(pre_d):.2f}  median adpD {np.median(adp_d):.2f}  median (adpD-preD) {np.median(amp):+.2f}, positive {int((amp>0).sum())}/10, "
      f"two-sided Wilcoxon p={wilcoxon(adp_d, pre_d).pvalue:.4f}")
print(f"mean preD {pre_d.mean():.2f} mean adpD {adp_d.mean():.2f}; median clean adapt gain {np.median(r[:,3]-r[:,1]):+.2f} (pos {int(((r[:,3]-r[:,1])>0).sum())}/10); median leaky adapt gain {np.median(r[:,2]-r[:,0]):+.2f}")
print("\n== Folds (fold job physgate-m1-*), final_checkpoint and as_released")
for v in ("final_checkpoint","as_released"):
    for f, o in (("A","B"),("B","A")):
        L = F[(f"m1-f{f.lower()}", f"result_PU_M1_{v}_F{f}to{f}_s2024")]
        C = F[(f"m1-f{f.lower()}", f"result_PU_M1_{v}_F{f}to{o}_s2024")]
        pl, pc, al, ac = m(L,"pre"), m(C,"pre"), m(L,"adapted"), m(C,"adapted")
        print(f"{v} fold {f}: pre leaky {pl:.2f} clean {pc:.2f} preD {pl-pc:.2f} | adapted leaky {al:.2f} clean {ac:.2f} adpD {al-ac:.2f} | clean adapt gain {ac-pc:+.2f}")
        print("   per-task pre clean:", [C['pre'][t] for t in T], " adapted clean:", [C['adapted'][t] for t in T])
        print("   per-task pre leaky:", [L['pre'][t] for t in T], " adapted leaky:", [L['adapted'][t] for t in T])
print("\n== Fold job vs gating job: same source model? (pre-update clean accuracy)")
for f, o in (("A","B"),("B","A")):
    a = F[(f"m1-f{f.lower()}", f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024")]
    b = F[(f"m2-f{f.lower()}", f"result_PU_M1_final_checkpoint_F{f}to{o}_s2024")]
    print(f"fold {f}: m1 pre {[a['pre'][t] for t in T]}\n        m2 pre {[b['pre'][t] for t in T]}")
    print(f"        m1 adapted mean {m(a,'adapted'):.3f}  m2 adapted mean {m(b,'adapted'):.3f}")
print("\n== SHOT ten splits pre/adapted")
S = D["shot_k10"]; rr=[]
for s in [f"S{i:02d}" for i in range(10)]:
    L, C = S[(s,s)], S[(s,s+"c")]
    rr.append((m(L,"pre"), m(C,"pre"), m(L,"adapted"), m(C,"adapted")))
    print(s, " ".join(f"{x:.2f}" for x in rr[-1]), f"preD {rr[-1][0]-rr[-1][1]:.2f} adpD {rr[-1][2]-rr[-1][3]:.2f}")
rr=np.array(rr); print("SHOT median preD", round(np.median(rr[:,0]-rr[:,1]),2), "median adpD", round(np.median(rr[:,2]-rr[:,3]),2), "median diff", round(np.median((rr[:,2]-rr[:,3])-(rr[:,0]-rr[:,1])),2))
print("SHOT means: leaky", rr[:,2].mean().round(2), "clean", rr[:,3].mean().round(2))
