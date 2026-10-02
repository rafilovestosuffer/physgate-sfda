import sys, time
sys.path.insert(0, r'C:/Users/Rafi/Desktop/claude research/physics')
import numpy as np, ses, gate
from scipy.ndimage import median_filter
from scipy.signal import lfilter
from scipy.stats import gamma as G, f as F
LN2=np.log(2.0); fs=12000.0; N=int(fs*3.0)

def floor_med(S,f,bw):
    df=f[1]-f[0]; w=max(3,int(round(bw/df))|1)
    return np.maximum(median_filter(S,size=w,mode='nearest')/LN2,1e-300)

def test_gamma(S,s2,idx,alpha):
    n=idx.size; return np.sum(S[idx]/s2[idx]) > G.ppf(1-alpha,a=n)

def test_cacfar(S,f,idx,alpha,guard_hz=2.0,ref_hz=25.0):
    """Cell-averaging CFAR. Reference = bins within ref_hz of any test bin, excluding test bins
    and +/-guard. Under H0 with locally constant sigma2: (mean_test/mean_ref) ~ F(2n, 2m). EXACT."""
    df=f[1]-f[0]; g=int(round(guard_hz/df)); r=int(round(ref_hz/df))
    mask=np.zeros(S.size,bool)
    lo=np.clip(idx-r,0,S.size-1); hi=np.clip(idx+r,0,S.size-1)
    for a,b in zip(lo,hi): mask[a:b+1]=True
    for a,b in zip(np.clip(idx-g,0,None),np.clip(idx+g,None,S.size-1)): mask[a:b+1]=False
    ref=np.nonzero(mask)[0]; n=idx.size; m=ref.size
    stat=S[idx].mean()/S[ref].mean()
    return stat > F.ppf(1-alpha,2*n,2*m)

def contiguous_family(m_idx, n, rng):
    """Realistic geometry: n bins in ~5 contiguous clusters (harmonic windows), not scattered."""
    k=5; per=max(1,n//k); out=[]
    starts=rng.choice(m_idx[:-per-1], size=k, replace=False)
    for s in starts: out.extend(range(s, s+per))
    return np.unique(np.asarray(out[:n]))

def run(colored, trials, seed):
    rng=np.random.default_rng(seed)
    cfgs=['gamma+med50','gamma+med15','cacfar ref25 g2','cacfar ref50 g2']
    NB=(20,45,95); AL=(0.10,0.05,0.01)
    hits={(c,n,a):0 for c in cfgs for n in NB for a in AL}
    for t in range(trials):
        x=rng.standard_normal(N)
        if colored: x=lfilter([1.0],[1.0,-0.7,0.25],x)
        f,S=ses.squared_envelope_spectrum(x,fs,band=(2000,5000))
        m=np.nonzero((f>=10)&(f<=600))[0]
        s50=floor_med(S,f,50); s15=floor_med(S,f,15)
        for n in NB:
            idx=contiguous_family(m,n,rng)
            for a in AL:
                hits[('gamma+med50',n,a)]+=test_gamma(S,s50,idx,a)
                hits[('gamma+med15',n,a)]+=test_gamma(S,s15,idx,a)
                hits[('cacfar ref25 g2',n,a)]+=test_cacfar(S,f,idx,a,2.0,25.0)
                hits[('cacfar ref50 g2',n,a)]+=test_cacfar(S,f,idx,a,2.0,50.0)
    print(f"--- {'COLOURED AR(2)' if colored else 'WHITE'}  trials={trials}  MC SE @a=.05: {(0.05*0.95/trials)**0.5:.3f}")
    for c in cfgs:
        print(f"  {c:18s} " + "  ".join(f"a={a:.2f}[" + " ".join(f"{n}:{hits[(c,n,a)]/trials:.3f}" for n in NB) + "]" for a in AL))
    sys.stdout.flush()

t0=time.time()
print("nominal: a=0.10 -> 0.100, a=0.05 -> 0.050, a=0.01 -> 0.010"); sys.stdout.flush()
run(False, 1500, 101)
run(True, 1500, 202)
print(f"done in {time.time()-t0:.0f}s")
