"""Package the Event A experiment using repository-relative paths."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from run_event_a import ROOT,verify_inputs

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    a=p.parse_args();verify_inputs()
    evidence=ROOT/'results/event_a'
    validation=json.loads((evidence/'validation.json').read_text())
    if validation['m2_scores_compared']!=798 or validation['m2_max_absolute_difference']!=0 or validation['original_runner_event_a_scores_matched']!=12:
        raise RuntimeError('Numerical validation incomplete')
    names=[ROOT/'.gitattributes',ROOT/'EVENT_A.md']
    names += sorted(p for folder in [ROOT/'extension/event_a',evidence] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='evidence_sha256.json')
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in names}
    (evidence/'evidence_sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
    names.append(evidence/'evidence_sha256.json')
    dest=Path(a.out).resolve();dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in names:z.write(p,p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(dest) as z:
        if z.testzip() is not None:raise RuntimeError('ZIP CRC error')
        for name,expected in hashes.items():
            if hashlib.sha256(z.read(name)).hexdigest()!=expected:raise RuntimeError('ZIP content mismatch '+name)
    print(dest,len(names),'repository files',dest.stat().st_size,'bytes')

if __name__=='__main__':main()
