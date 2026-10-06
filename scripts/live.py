#!/usr/bin/env python3
"""Drive a fresh EVIDENCELOCK 61999 lifecycle and persist machine-readable proof.

Required inputs are real public HTTPS URLs. Use --confirmed-url, --refuted-url,
--conflict-url and --insufficient-url. The first URL should be a controlled
fixture if you want the strongest immutability proof: capture version A, mutate
the live page, then pass --mutation-check-url to prove the vault body/hash stay A.
"""
from __future__ import annotations
import argparse,json,os,pathlib,sys,time,urllib.request,hashlib
from genlayer_py import create_account,create_client
from genlayer_py.chains import studionet
from genlayer_py.types.transactions import TransactionHashVariant
ROOT=pathlib.Path(__file__).resolve().parents[1]; DEP=ROOT/'docs'/'deployment.json'; OUT=ROOT/'records'/'live_run.json'
sys.path.insert(0,str(ROOT/'scripts')); import transport  # noqa:F401,E402

def check(x,m):
    if not x: raise RuntimeError(m)
def account(role):
    """Load a funded test wallet; never fabricate unfunded lifecycle actors."""
    key = os.environ.get('GENLAYER_' + role + '_PRIVATE_KEY', '').strip()
    if not key:
        raise RuntimeError('missing GENLAYER_' + role + '_PRIVATE_KEY')
    return create_account(account_private_key=key.removeprefix('0x'))
def execution(r): return (((r.get('consensus_data') or {}).get('leader_receipt') or [{}])[0]).get('execution_result')
def write(client,address,fn,args=None,value=None,target='ACCEPTED'):
    kw={'address':address,'function_name':fn,'args':args or []};
    if value is not None: kw['value']=value
    tx=client.write_contract(**kw); rec=client.wait_for_transaction_receipt(transaction_hash=tx,status=target,interval=4000,retries=240)
    return str(tx),rec
def read(client,address,fn,args=None,final=False):
    return client.read_contract(address=address,function_name=fn,args=args or [],transaction_hash_variant=(TransactionHashVariant.LATEST_FINAL if final else TransactionHashVariant.LATEST_NONFINAL))
def latest_id(client,address,method): return read(client,address,method,[0,1])['items'][0]
def live_hash(url):
    with urllib.request.urlopen(url,timeout=30) as r: return hashlib.sha256(r.read()).hexdigest()
def main():
    p=argparse.ArgumentParser();
    for n in ['confirmed','refuted','conflict','insufficient']: p.add_argument(f'--{n}-url',required=True)
    p.add_argument('--mutation-check-url',''); p.add_argument('--bounty-wei',type=int,default=1)
    a=p.parse_args(); check(DEP.exists(),'deploy first')
    dep=json.loads(DEP.read_text()); vault=dep['vault']['address']; court=dep['court']['address']
    creator=create_client(chain=studionet,account=account('CREATOR')); submitter=create_client(chain=studionet,account=account('SUBMITTER')); reader=create_client(chain=studionet,account=account('READER')); depositor=create_client(chain=studionet,account=account('DEPOSITOR'))
    record={'network':'GenLayer Studionet','chain_id':61999,'vault':vault,'court':court,'started_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'transactions':[],'claims':{},'immutability_proof':{},'finality_proof':{}}
    cases=[('confirmed',a.confirmed_url,'PUBLIC_ANNOUNCEMENT','CONFIRMED'),('refuted',a.refuted_url,'PUBLIC_ANNOUNCEMENT','REFUTED'),('conflict',a.confirmlict_url if False else a.conflict_url,'EVENT_OCCURRED','CONFLICTED'),('insufficient',a.insufficient_url,'ENTITY_STATUS','INSUFFICIENT')]
    now='2026-10-06T12:00:00Z'; start='2026-01-01T00:00:00Z'; end='2030-01-01T00:00:00Z'
    first_snapshot=None
    for label,url,kind,expected in cases:
        tx,r=write(submitter,vault,'capture_snapshot',['evidencelock-live','EvidenceLock Live Subject',kind,url]); check(execution(r)=='SUCCESS',f'{label} capture failed'); record['transactions'].append({'step':f'{label}:capture','tx':tx,'status':r.get('status_name'),'execution':execution(r)})
        snap=latest_id(reader,vault,'list_snapshots'); sid=snap['snapshot_id']; first_snapshot=first_snapshot or read(reader,vault,'get_snapshot',[sid])
        tx,r=write(creator,court,'register_claim',[kind,'evidencelock-live','EvidenceLock Live Subject','target assertion',now,start,end]); check(execution(r)=='SUCCESS',f'{label} register failed'); claim=latest_id(reader,court,'list_claims'); cid=claim['claim_id']; record['transactions'].append({'step':f'{label}:register','tx':tx})
        tx,r=write(submitter,court,'attach_snapshot',[cid,sid]); check(execution(r)=='SUCCESS',f'{label} attach failed'); record['transactions'].append({'step':f'{label}:attach','tx':tx})
        if label=='confirmed':
            tx,r=write(depositor,court,'fund_bounty',[cid],value=a.bounty_wei); check(execution(r)=='SUCCESS','bounty funding failed'); record['transactions'].append({'step':'bounty:fund','tx':tx})
        tx,r=write(reader,court,'adjudicate',[cid]); check(execution(r)=='SUCCESS',f'{label} adjudication failed'); adj=read(reader,court,'get_claim_adjudication',[cid]); record['transactions'].append({'step':f'{label}:adjudicate','tx':tx,'status':r.get('status_name'),'execution':execution(r)})
        record['claims'][label]={'claim_id':cid,'snapshot_id':sid,'verdict':adj.get('verdict'),'expected':expected,'adjudication':adj}
    # Live pages are inherently semantic; assert exact expected values only after the operator intentionally selected fixtures.
    for label,c in record['claims'].items(): check(c['verdict']==c['expected'],f"{label}: expected {c['expected']} got {c['verdict']}")
    confirmed=record['claims']['confirmed']['claim_id']; nonfinal=read(reader,court,'get_claim',[confirmed],final=False)
    record['finality_proof']['accepted_status']=nonfinal.get('status'); record['finality_proof']['accepted_before_finalized']=nonfinal.get('status') in ('ACCEPTED','SETTLED')
    # Wait on the adjudication transaction itself to FINALIZED; finalized child settlement may then execute.
    atx=[x['tx'] for x in record['transactions'] if x['step']=='confirmed:adjudicate'][0]
    fin=reader.wait_for_transaction_receipt(transaction_hash=atx,status='FINALIZED',interval=4000,retries=240); record['finality_proof']['adjudication_finalized_status']=fin.get('status_name') or str(fin.get('status'))
    time.sleep(5); final_claim=read(reader,court,'get_claim',[confirmed],final=False); record['finality_proof']['post_finality_claim_status']=final_claim.get('status')
    try:
        tx,r=write(reader,court,'settle',[confirmed]); rejected=execution(r)!='SUCCESS'
    except Exception: rejected=True
    record['finality_proof']['second_settlement_rejected']=rejected
    if a.mutation_check_url and first_snapshot:
        current=live_hash(a.mutation_check_url); again=read(reader,vault,'get_snapshot',[first_snapshot['snapshot_id']]);
        record['immutability_proof']={'snapshot_id':first_snapshot['snapshot_id'],'stored_content_sha256':first_snapshot['content_sha256'],'stored_content_sha256_after_mutation':again['content_sha256'],'current_live_raw_sha256':current,'snapshot_body_unchanged':again['body']==first_snapshot['body'] and again['content_sha256']==first_snapshot['content_sha256']}
    else: record['immutability_proof']={'snapshot_body_unchanged':False,'note':'rerun with --mutation-check-url against a controlled page after changing it'}
    record['custody']=read(reader,court,'get_custody'); check(record['custody']['balanced'] is True,'custody imbalance')
    record['finished_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()); OUT.parent.mkdir(exist_ok=True); OUT.write_text(json.dumps(record,indent=2)+'\n'); print(OUT); return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as e: print('LIVE RUN FAILED:',e,flush=True); raise
