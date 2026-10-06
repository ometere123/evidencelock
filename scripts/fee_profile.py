#!/usr/bin/env python3
"""Create/validate the fee-profile worklist used before final live proof.

The exact estimator API can change independently of contract logic, so this script
stores the representative transaction matrix and refuses a final profile missing
any critical path. The finishing agent should populate estimated/observed fields
using the installed stable 61999 SDK/CLI and commit the result.
"""
import argparse,json,pathlib,time
ROOT=pathlib.Path(__file__).resolve().parents[1]; OUT=ROOT/'records'/'fee-profile.json'
PATHS=['deploy_evidence_vault','deploy_claim_court','capture_snapshot','register_claim','attach_snapshot','fund_bounty','adjudicate','finalized_settle','recover_bounty']
def main():
 p=argparse.ArgumentParser(); p.add_argument('--init',action='store_true'); p.add_argument('--check',action='store_true'); a=p.parse_args()
 if a.init or not OUT.exists():
  OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps({'network':61999,'generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'paths':{x:{'estimated':None,'observed':None,'tx':''} for x in PATHS}},indent=2)+'\n'); print(OUT); return 0
 d=json.loads(OUT.read_text()); missing=[x for x in PATHS if x not in d.get('paths',{})]
 incomplete=[x for x,v in d.get('paths',{}).items() if x in PATHS and v.get('estimated') is None]
 if missing: print('missing fee paths:',', '.join(missing)); return 1
 if a.check and incomplete: print('fee profile incomplete:',', '.join(incomplete)); return 1
 print('fee profile structure PASS' if not incomplete else 'fee profile initialized; populate before submission'); return 0
if __name__=='__main__': raise SystemExit(main())
