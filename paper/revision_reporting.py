"""Reporting-only corrections from retained artifacts; never trains or changes original results."""
from pathlib import Path
import csv,hashlib,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from rev6_load import boot_median_ci,sign_flip_p
OUT=ROOT/'results/reporting_2026_10_09'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 paths=['results/c112/c112_result.json','results/c110/c110_result.json','results/c109/c109_intervals.json','runners/shot_patch.py','third_party/SDALR/tools.py']
 sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
 kin=json.loads((ROOT/paths[0]).read_text());r=[kin['per_split'][f'S{i:02d}'] for i in range(10)]
 gaps=np.array([v['leaky']-v['clean_balanced'] for v in r])
 div=json.loads((ROOT/paths[1]).read_text())
 fa=json.loads((ROOT/paths[2]).read_text())['healthy_false_acceptance']
 out={'status':'post-hoc reporting only; no new runs or training','date':'2026-10-09','source_sha256':sources,
 'kinematic_original':kin['summary'],'kinematic_balanced':{'mean_leaky':float(np.mean([v['leaky'] for v in r])),'mean_clean':float(np.mean([v['clean_balanced'] for v in r])),'median_clean':float(np.median([v['clean_balanced'] for v in r])),'median_gap':float(np.median(gaps)),'ci95_conditional':boot_median_ci(gaps),'nominal_sign_flip_p':sign_flip_p(gaps,'greater'),'positive':int((gaps>0).sum()),'rows':[{'split':f'S{i:02d}','leaky_balanced':v['leaky'],'clean_balanced':v['clean_balanced'],'gap':float(gaps[i])} for i,v in enumerate(r)]},
 'diversity_training_windows':{str(n):{'median':float(np.median(v)),'min':int(np.min(v)),'max':int(np.max(v))} for n in range(1,5) for v in [[c['n_train'] for x in div['rows'] if x['n']==n for c in x['per_condition'].values()]]},
 'diversity_monte_carlo':{'draws':100000,'exceedances':0,'original_p':div['summary']['p_one_sided'],'corrected_p':1/100001,'interpretation':'nominal exploratory sign-flip result, conditional on its assumptions'},
 'healthy_false_acceptance':fa,
 'shot_status':{'status':'WITHDRAWN as evidence about SHOT','reason':'obtain_label returns predictions in shuffled loader traversal order, while training indexes them by dataset sample index; no index restoration occurs. Original artifacts retained; no corrected run exists.'}}
 assert div['summary']['p_one_sided']==0
 (OUT/'reporting_corrections.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 # Explicit reporting lineage, not new experimental runs; original ledgers are untouched.
 fields=next(csv.reader((ROOT/'results/ledger/rafiurrahman01.csv').open(encoding='utf-8')))
 with (ROOT/'results/ledger/reporting_2026_10_09.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for row in out['kinematic_balanced']['rows']:
   w.writerow(dict(run_id='reporting-20261009-C112-'+row['split'],runner_id='reporting-only',task=row['split'],method='RF kinematic balanced accuracy reaggregation',rung='post-hoc reporting',split_type='bearing-disjoint',label_space='L3',track='reporting',acc=row['clean_balanced'],gpu_hours=0,artifact_path='results/reporting_2026_10_09/reporting_corrections.json',notes='No model fit or new experiment; derived from retained results/c112/c112_result.json; SHA256 '+sources[paths[0]]))
  w.writerow(dict(run_id='reporting-20261009-C110',runner_id='reporting-only',task='summary',method='C110 reporting correction',rung='post-hoc reporting',track='reporting',gpu_hours=0,artifact_path='results/reporting_2026_10_09/reporting_corrections.json',notes='Existing training counts and plus-one p-value only; no new experiment; source SHA256 '+sources[paths[1]]))
 print(json.dumps(out['kinematic_balanced'],indent=2))
if __name__=='__main__':main()
