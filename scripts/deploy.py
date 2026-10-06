#!/usr/bin/env python3
"""Deploy EvidenceVault then ClaimCourt to stable Studionet and prove exact source bytes.

Uses ``GENLAYER_DEPLOYER_PRIVATE_KEY`` when present, otherwise a gitignored
deployer key in .data/deployer.json. Refuses dirty contract files,
waits for FINALIZED, requires execution_result SUCCESS, verifies on-chain source
bytes, then writes docs/deployment.json and .env.local.
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, pathlib, subprocess, sys, time
from eth_account import Account
from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet

ROOT=pathlib.Path(__file__).resolve().parents[1]
VAULT=ROOT/'contracts'/'evidence_vault.py'; COURT=ROOT/'contracts'/'claim_court.py'
RECORD=ROOT/'docs'/'deployment.json'; KEY=ROOT/'.data'/'deployer.json'
EXPECTED_CHAIN=61999; EXPECTED_RPC='https://studio.genlayer.com/api'
RUNNER='py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6'
EXPLORER='https://explorer-studio.genlayer.com'
sys.path.insert(0,str(ROOT/'scripts')); import transport  # noqa:F401,E402

def say(x=''): print(x,flush=True)
def git(*a): return subprocess.run(['git',*a],cwd=ROOT,capture_output=True,text=True).stdout.strip()
def source_bytes(path): return path.read_bytes().replace(b'\r\n',b'\n')
def sha(b): return hashlib.sha256(b).hexdigest()
def account():
    supplied = os.environ.get('GENLAYER_DEPLOYER_PRIVATE_KEY', '').strip()
    if supplied:
        return create_account(account_private_key=supplied.removeprefix('0x'))
    KEY.parent.mkdir(parents=True,exist_ok=True)
    if KEY.exists():
        d=json.loads(KEY.read_text()); return create_account(account_private_key=d['private_key'])
    a=Account.create(); KEY.write_text(json.dumps({'private_key':a.key.hex(),'address':a.address},indent=2))
    return create_account(account_private_key=a.key.hex())
def onchain_bytes(client,address):
    x=client.provider.make_request('gen_getContractCode',[address]); raw=x.get('result',x) if isinstance(x,dict) else x; s=str(raw)
    return bytes.fromhex(s[2:]) if s.startswith('0x') else base64.b64decode(s)
def execution(receipt):
    leader=((receipt.get('consensus_data') or {}).get('leader_receipt') or [{}])[0]
    return leader.get('execution_result')
def address_of(receipt): return (receipt.get('data',{}) or {}).get('contract_address') or receipt.get('contract_address')
def schema_methods(client,address):
    x=client.provider.make_request('gen_getContractSchema',[address]); x=x.get('result',x) if isinstance(x,dict) else x
    return sorted((x or {}).get('methods',{}).keys())
def ensure_clean(path):
    rel=str(path.relative_to(ROOT)); dirty=git('status','--porcelain',rel)
    if dirty: raise SystemExit(f'{rel} is modified/uncommitted; commit exact deployable source first')
def ensure_source(path):
    b=source_bytes(path); text=b.decode();
    if RUNNER not in text.splitlines()[0]: raise SystemExit(f'{path.name}: unexpected GenVM runner pin')
    return b
def chain_guard(client):
    raw=client.provider.make_request('eth_chainId',[]); raw=raw.get('result',raw) if isinstance(raw,dict) else raw
    cid=int(str(raw),16) if str(raw).startswith('0x') else int(raw)
    if cid!=EXPECTED_CHAIN: raise SystemExit(f'RPC reports chain {cid}, expected {EXPECTED_CHAIN}')
    return cid
def deploy_one(client,label,path,args):
    b=ensure_source(path); digest=sha(b); say(f'{label}: sha256 {digest}')
    tx=client.deploy_contract(code=b.decode(),args=args); say(f'{label}: submitted {tx}')
    receipt=client.wait_for_transaction_receipt(transaction_hash=tx,status='FINALIZED',interval=4000,retries=240)
    exe=execution(receipt); addr=address_of(receipt)
    if exe!='SUCCESS' or not addr: raise SystemExit(f'{label}: finalized but execution={exe}; deployment not accepted')
    live=onchain_bytes(client,addr); live_sha=sha(live)
    if live_sha!=digest: raise SystemExit(f'{label}: on-chain source mismatch {live_sha} != {digest}')
    return {'contract':label,'address':addr,'deploy_tx':str(tx),'status':receipt.get('status_name') or str(receipt.get('status')),'execution':exe,'source':str(path.relative_to(ROOT)),'source_sha256':digest,'onchain_sha256':live_sha,'byte_identical':True,'methods':schema_methods(client,addr),'explorer':f'{EXPLORER}/address/{addr}'}
def verify_record(client,record):
    chain_guard(client)
    for key,path in [('vault',VAULT),('court',COURT)]:
        item=record[key]; digest=sha(source_bytes(path)); live=sha(onchain_bytes(client,item['address']))
        if digest!=item['source_sha256'] or live!=digest: raise SystemExit(f'{key}: source verification failed')
    proto=client.read_contract(address=record['court']['address'],function_name='get_protocol',args=[])
    if str(proto.get('vault_address','')).lower()!=record['vault']['address'].lower(): raise SystemExit('court points at the wrong vault')
    if int(proto.get('chain_id',0))!=EXPECTED_CHAIN: raise SystemExit('court protocol chain mismatch')
    say('deployment verification PASS')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--verify',action='store_true'); a=p.parse_args()
    client=create_client(chain=studionet,account=account()); cid=chain_guard(client)
    if a.verify:
        if not RECORD.exists(): raise SystemExit('docs/deployment.json does not exist')
        verify_record(client,json.loads(RECORD.read_text())); return 0
    ensure_clean(VAULT); ensure_clean(COURT)
    head=git('rev-parse','HEAD');
    if not head: raise SystemExit('repository must be committed before deployment')
    vault=deploy_one(client,'EvidenceVault',VAULT,[])
    court=deploy_one(client,'ClaimCourt',COURT,[vault['address']])
    record={'network':'GenLayer Studionet','chain_id':cid,'rpc':EXPECTED_RPC,'source_commit':head,'runner':RUNNER,'deployed_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'vault':vault,'court':court}
    RECORD.write_text(json.dumps(record,indent=2)+'\n')
    (ROOT/'.env.local').write_text(f'NEXT_PUBLIC_CHAIN_ID=61999\nNEXT_PUBLIC_EVIDENCE_VAULT={vault["address"]}\nNEXT_PUBLIC_CLAIM_COURT={court["address"]}\n')
    verify_record(client,record)
    say('wrote docs/deployment.json and .env.local'); return 0
if __name__=='__main__': raise SystemExit(main())
