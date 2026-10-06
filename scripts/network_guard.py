#!/usr/bin/env python3
"""Fail closed unless the selected RPC is stable Studionet chain 61999."""
import argparse, json, urllib.request

RPC = "https://studio.genlayer.com/api"
EXPECTED = 61999

def rpc(method, params=None):
    payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params or []}).encode()
    req = urllib.request.Request(RPC, data=payload, headers={"content-type":"application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def parse_chain(value):
    if isinstance(value, int): return value
    s = str(value)
    return int(s, 16) if s.startswith("0x") else int(s)

def main():
    p=argparse.ArgumentParser(); p.add_argument('--json',action='store_true'); a=p.parse_args()
    result = rpc('eth_chainId').get('result')
    chain = parse_chain(result)
    out={"rpc":RPC,"expected_chain_id":EXPECTED,"reported_chain_id":chain,"ok":chain==EXPECTED}
    print(json.dumps(out,indent=2) if a.json else f"Studionet guard: RPC {RPC} reports chain {chain} ({'PASS' if chain==EXPECTED else 'FAIL'})")
    return 0 if chain==EXPECTED else 1
if __name__=='__main__': raise SystemExit(main())
