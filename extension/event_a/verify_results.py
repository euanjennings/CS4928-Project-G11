"""Verify package bytes and, optionally, scores from a fresh Event A run."""
import argparse
import hashlib
import json
from pathlib import Path
from run_event_a import ROOT, verify_inputs
from run_validation import compare_reference, signature

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run',type=Path)
    a=p.parse_args()
    manifest=verify_inputs()
    evidence=json.loads((ROOT/'results/event_a/evidence_sha256.json').read_text())
    for name,digest in evidence.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Evidence changed: '+name)
    print('PASS:',len(manifest['sha256']),'frozen input hashes;',len(evidence),'package file hashes')
    if a.run:
        r=json.loads((a.run/'result.json').read_text())
        if r.get('status')!='completed' or r.get('seed')!=2026 or r.get('diagnostic') is not None:
            raise RuntimeError('Expected a completed primary seed-2026 run')
        compare_reference(r)
        saved=json.loads((ROOT/'results/event_a/primary/result.json').read_text())
        if signature(saved)!=signature(r): raise RuntimeError('Scores or final partitions differ')
        print('PASS: all 12 reported scores, 12 raw percentages and four final partitions match')

if __name__=='__main__':main()
