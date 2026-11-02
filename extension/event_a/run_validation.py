"""Run the Event A validation suite serially into a fresh output directory."""
import argparse
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from run_event_a import ROOT,HERE,run,save

def require(ok,message):
    if not ok: raise RuntimeError(message)

def compare_reference(result):
    old=json.loads((HERE/'reference_scores.json').read_text())
    count=0
    for case in result['cases']:
        for tool in ('classsplitter','baseline'):
            for metric,expected in zip(old['metric_order'],old['scores'][str(case['id'])][tool]):
                require(abs(case[tool][metric]['reported']-expected)<1e-10,'Reference score mismatch')
                count+=1
    return count

def signature(r):
    return [{k:c[k] for k in ('id','baseline','classsplitter','baseline_groups','classsplitter_groups')} for c in r['cases']]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',required=True)
    a=p.parse_args()
    out=Path(a.out_dir).resolve()
    if not out.is_relative_to(ROOT): raise RuntimeError('Full validation output must be inside the repository; use results/event_a_validation')
    out.mkdir(parents=True,exist_ok=False)
    primary=run(out/'primary',2026)
    v={'reference_scores_matched':compare_reference(primary)}
    repeat=run(out/'repeat_seed2026',2026)
    require(signature(primary)==signature(repeat),'Repeat mismatch')
    v['repeat_scores_and_partitions_match']=True
    seeds=[]
    for seed in range(30):
        r=run(out/'seeds'/str(seed),seed)
        seeds.append({'seed':seed,'classsplitter_mean':r['means']['classsplitter']['overall'],'baseline_mean':r['means']['baseline']['overall'],'gap':r['gap']})
    with (out/'seed_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=seeds[0],lineterminator='\n');w.writeheader();w.writerows(seeds)
    v['baseline_higher_mean_seeds']=sum(x['gap']<0 for x in seeds)
    v['seed_count']=30
    no_ps=run(out/'diagnostic_no_method_position',2026,'no-method-position')
    ms=run(out/'diagnostic_recomputed_ms',2026,'recompute-ms')
    v['diagnostic_no_method_position_cs_mean']=no_ps['means']['classsplitter']['overall']
    v['diagnostic_recomputed_ms_cs_mean']=ms['means']['classsplitter']['overall']
    with (out/'m2_replay.log').open('w') as log:
        subprocess.run([sys.executable,str(ROOT/'repro/run_repro.py'),'--seed','2026','--out',str(out/'m2_replay.csv')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    with (ROOT/'results/m2_repro_seed2026.csv').open() as f: old=list(csv.DictReader(f))
    with (out/'m2_replay.csv').open() as f: new=list(csv.DictReader(f))
    require(len(old)==len(new)==133,'M2 row count mismatch')
    deltas=[]
    for a,b in zip(old,new):
        require(a['index']==b['index'],'M2 case mismatch')
        deltas.extend(abs(float(a[k])-float(b[k])) for k in a if k.endswith('mojofm'))
    require(len(deltas)==798 and max(deltas)==0,'M2 scores differ')
    v['m2_scores_compared']=len(deltas);v['m2_max_absolute_difference']=max(deltas)
    # Execute the original M2 main, redirecting only its catalogue to the two held-out rows.
    from god_class import DictHandler
    original_init=DictHandler.__init__
    def redirected(self,path):
        return original_init(self,str(HERE/'cases.csv') if path=='GodClassRefactorDictionary.csv' else path)
    spec=importlib.util.spec_from_file_location('original_repro',ROOT/'repro/run_repro.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    DictHandler.__init__=redirected
    argv=sys.argv[:]
    try:
        sys.argv=['run_repro.py','--seed','2026','--out',str(out/'original_runner_event_a.csv')]
        mod.main()
    finally:
        DictHandler.__init__=original_init;sys.argv=argv
    with (out/'original_runner_event_a.csv').open() as f: rows=list(csv.DictReader(f))
    count=0
    for case,row in zip(primary['cases'],rows):
        require(int(row['index'])==case['id'],'Original runner case mismatch')
        for tool in ('baseline','classsplitter'):
            for metric,suffix in [('overall','mojofm'),('method','method_mojofm'),('field','field_mojofm')]:
                require(abs(float(row[tool+'_'+suffix])-case[tool][metric]['reported'])<1e-12,'Original runner score mismatch');count+=1
    v['original_runner_event_a_scores_matched']=count
    v['primary_means']=primary['means'];v['primary_gap']=primary['gap']
    save(out/'validation.json',v)
    print(json.dumps(v,indent=2),flush=True)

if __name__=='__main__':main()
