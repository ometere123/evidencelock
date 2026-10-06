#!/usr/bin/env python3
"""Offline consistency check for deployment/live records and current sources."""
import hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sh(p): return hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
def main():
    problems=[]; dep=ROOT/'docs'/'deployment.json'; live=ROOT/'records'/'live_run.json'
    if not dep.exists(): print('SKIP: no docs/deployment.json yet'); return 0
    d=json.loads(dep.read_text())
    for key,path in [('vault',ROOT/'contracts'/'evidence_vault.py'),('court',ROOT/'contracts'/'claim_court.py')]:
        got=sh(path); rec=d[key].get('source_sha256','')
        if got!=rec: problems.append(f'{key} source changed: {got} != recorded {rec}')
        if d[key].get('onchain_sha256')!=got or not d[key].get('byte_identical'): problems.append(f'{key} record does not prove byte identity')
    if int(d.get('chain_id',0))!=61999: problems.append('deployment record is not chain 61999')
    if str(d['court'].get('address','')).lower()==str(d['vault'].get('address','')).lower(): problems.append('vault and court addresses are unexpectedly identical')
    if live.exists():
        l=json.loads(live.read_text())
        if l.get('court','').lower()!=d['court']['address'].lower(): problems.append('live run used a different court')
        if l.get('vault','').lower()!=d['vault']['address'].lower(): problems.append('live run used a different vault')
        if l.get('failed'): problems.append('live record reports failure')
    readme=(ROOT/'README.md').read_text()
    for addr in re.findall(r'0x[0-9a-fA-F]{40}',readme):
        if addr.lower() not in {d['court']['address'].lower(),d['vault']['address'].lower()}:
            problems.append(f'README contains stale/unrelated address {addr}')
    if problems:
        for x in problems: print('PROBLEM',x)
        return 1
    print('records reconcile with current contract sources and chain lock')
    return 0
if __name__=='__main__': raise SystemExit(main())
