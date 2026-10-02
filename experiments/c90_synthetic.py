"""C90 estimator recovery check on synthetic impulse trains (true slip 0.1-4 %, shaft harmonics added). Output: results/c90/c90_synthetic.txt."""
import sys, numpy as np
sys.path.insert(0,__import__('os').path.join(__import__('os').path.dirname(__file__))); import c90_slip as c
from kinematics import kinematics
fs=64000; n=249600; t=np.arange(n)/fs; fr=25.0
rng=np.random.default_rng(1)
for geom,fault in (("6203_PU_2905","outer_race"),("6203_PU_2905","inner_race"),("6203_PU_2855","outer_race")):
  k=kinematics(geom)
  for s in (0.001,0.01,0.0178,0.023,0.04):
    f=(k.BPFO*(1-s) if fault=="outer_race" else k.BPFI+s*k.BPFO)*fr
    x=0.3*rng.normal(size=n)+0.5*np.sin(2*np.pi*fr*t)+0.2*np.sin(2*np.pi*3*fr*t)
    T=np.cumsum(rng.normal(1/f, 0.005/f, size=int(4*f)+10)); T=T[T<n/fs]
    h=np.exp(-800*np.arange(200)/fs)*np.sin(2*np.pi*4000*np.arange(200)/fs)
    for ti in T:
      i=int(ti*fs); x[i:i+200]+=0.6*h[:max(0,min(200,n-i))]
    e=c.estimate(x,fs,fr*60,geom,fault,15000.0)
    print(geom,fault,'true %.4f'%s,'unmasked %.4f'%e['unmasked']['s_hat'],e['unmasked']['valid'],'masked %.4f'%e['masked']['s_hat'],e['masked']['valid'],'lock',e['unmasked']['in_lock'],e['masked']['in_lock'])
