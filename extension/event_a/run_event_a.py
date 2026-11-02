"""Execute Event A with the M2 algorithms and supplied similarity cache.
Run serially from one checkout: upstream MoJo uses shared temporary RSF files.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / 'upstream/Implementation/experienments'
HERE = Path(__file__).resolve().parent

def stamp():
    return datetime.now(timezone.utc).isoformat()

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True)+'\n', encoding='utf-8')

def verify_inputs():
    manifest = json.loads((HERE/'input_manifest.json').read_text())
    for name, expected in manifest['sha256'].items():
        actual = hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError('Frozen input changed: '+name)
    return manifest

def groups(obj):
    return sorted([sorted(int(m.get_index()) for m in g.get_members()) for g in obj.groups])

def environment():
    spec = importlib.util.spec_from_file_location('m2_runner', ROOT/'repro/run_repro.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.environment()

def score(obj, dest):
    dest.mkdir()
    scores = {}
    for metric in ('overall','method','field'):
        value = obj.get_field_mojofm() if metric == 'field' else obj.get_mojofm(field=metric=='overall')
        shutil.copyfile(EXP/'group.rsf', dest/(metric+'_predicted.rsf'))
        shutil.copyfile(EXP/'example.rsf', dest/(metric+'_reference.rsf'))
        raw = float(subprocess.check_output(['java','mojo.MoJo','group.rsf','example.rsf','-fm'], cwd=EXP, text=True).strip())
        if abs(value-max(0,(raw-50)/50)) > 1e-12:
            raise RuntimeError('MoJo score mismatch')
        scores[metric] = {'reported':float(value), 'raw_percent':raw}
    return scores

def run(out, seed=2026, diagnostic=None):
    if sys.flags.optimize:
        raise RuntimeError('Do not use Python -O: upstream relies on assertions')
    out = Path(out).resolve()
    manifest = verify_inputs()
    out.mkdir(parents=True, exist_ok=False)
    record = {'status':'running','provenance':'Event A execution using the M2 method and supplied cache',
              'started_utc':stamp(),'seed':seed,'diagnostic':diagnostic,
              'environment':environment(),'input_manifest':manifest,'cases':[]}
    save(out/'result.json', record)
    os.chdir(EXP)
    if str(EXP) not in sys.path: sys.path.insert(0,str(EXP))
    import matplotlib
    matplotlib.use('Agg')
    from god_class import DictHandler
    from cluster import ClusterSeparate
    from baseline1 import Baseline1
    random.seed(seed)
    cases = DictHandler(str(HERE/'cases.csv')).get_classes()
    if [c.get_index() for c in cases] != [13,3490]: raise RuntimeError('Case order changed')
    for c in cases:
        dest = out/str(c.get_index())
        dest.mkdir()
        # Same call order as the original M2 runner.
        b = Baseline1(c)
        b.original_graph_to_chain()
        b.original_chain_to_groups()
        b.handel_fields()
        s = ClusterSeparate(c, model_name='sentence-transformers/all-mpnet-base-v2', cache_path='cache_time_all-mpnet-base-v2.json')
        audit = None
        if diagnostic == 'no-method-position': s.set_use_similarity({'PS':0,'MS':1,'CS':1})
        if diagnostic == 'recompute-ms':
            import numpy as np
            original = np.array(s.MS)
            recomputed = np.array(s.get_MS())
            delta = np.abs(original-recomputed)
            audit = {'unequal_unordered_pairs':int(np.sum(np.triu(delta>1e-8,1))),
                     'total_unordered_pairs':int(len(delta)*(len(delta)-1)//2),
                     'max_absolute_difference':float(delta.max()),
                     'cached_MS':original.tolist(),'recomputed_MS':recomputed.tolist()}
            s.MS = recomputed.tolist()
        stages = {}
        for step in ('separate_to_group','split_group_by_position','merge_adjacent_single_method','merge_separate_group','handle_fields'):
            getattr(s,step)()
            stages[step] = groups(s)
        row = {'id':c.get_index(),'name':c.get_name(),'data_file':str(Path(c.data_path).name),
               'baseline_groups':groups(b),'classsplitter_groups':groups(s),'stages':stages,
               'baseline':score(b,dest/'baseline'),'classsplitter':score(s,dest/'classsplitter')}
        if audit: save(dest/'cache_audit.json',audit)
        c.data_frame.to_csv(dest/'members.csv',index=False,lineterminator='\n')
        save(dest/'partitions.json', {k:v for k,v in row.items() if k.endswith('groups') or k=='stages'})
        record['cases'].append(row)
        print(seed,diagnostic,c.get_index(),row['classsplitter']['overall'],row['baseline']['overall'],flush=True)
    record['means'] = {tool:{metric:sum(c[tool][metric]['reported'] for c in record['cases'])/2 for metric in ('overall','method','field')} for tool in ('baseline','classsplitter')}
    record['gap'] = record['means']['classsplitter']['overall']-record['means']['baseline']['overall']
    verify_inputs()
    record.update(status='completed',completed_utc=stamp())
    save(out/'result.json',record)
    return record

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out-dir',required=True)
    p.add_argument('--seed',type=int,default=2026)
    p.add_argument('--diagnostic',choices=['no-method-position','recompute-ms'])
    a=p.parse_args()
    run(a.out_dir,a.seed,a.diagnostic)

if __name__=='__main__': main()
