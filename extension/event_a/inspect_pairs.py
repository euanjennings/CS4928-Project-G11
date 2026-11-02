"""Export positional examples from saved stages; no new clustering occurs."""
import argparse
import csv
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--run-dir',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();root=Path(a.run_dir)
    result=json.loads((root/'result.json').read_text())
    pairs={13:[(11,15),(18,23)],3490:[(37,38),(37,41),(30,32)]}
    rows=[]
    for case in result['cases']:
        with (root/str(case['id'])/'members.csv').open() as f: members={int(r['index']):r for r in csv.DictReader(f)}
        for left,right in pairs[case['id']]:
            for stage,groups in case['stages'].items():
                rows.append({'case':case['id'],'left':left,'left_name':members[left]['name'],'left_removed':members[left]['removed'],
                             'right':right,'right_name':members[right]['name'],'right_removed':members[right]['removed'],
                             'stage':stage,'same_group':any(left in g and right in g for g in groups)})
    with open(a.out,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n');w.writeheader();w.writerows(rows)

if __name__=='__main__':main()
