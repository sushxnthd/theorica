#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('result',type=Path);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 r=json.loads(a.result.read_text()); c=r['counts']
 expected_priors=sum(3**n for n in range(3,8))
 expected_uniform=sum(n-1 for n in range(3,8))
 checks={
  'terminal_pass':r['status']=='PASS' and not r['failures'],
  'all_prior_vectors':c['prior_vectors']==expected_priors,
  'all_uniform_separations':c['uniform_separations']==expected_uniform,
  'substantial_frontier_enumeration':c['frontier_cases']>80000,
  'substantial_subset_enumeration':c['deterministic_subset_checks']>100000,
  'randomized_lp_controls':c['randomized_lp_cases']==sum(4*n for n in range(3,8)),
  'witnesses_preserved':len(r['witnesses'])==8,
 }
 out={'schema':'theorica.robust-provenance-query-frontier.audit.v1','checks':checks,'passed':sum(checks.values()),'total':len(checks),'status':'PASS' if all(checks.values()) else 'FAIL'}
 a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out,indent=2,sort_keys=True))
 if out['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
