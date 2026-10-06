"""Read-only Studionet verification against a completed deployment record.

Skipped before deployment; after docs/deployment.json exists these become real
network assertions and should be run with `pytest tests/integration -q`.
"""
import json,pathlib,pytest
ROOT=pathlib.Path(__file__).resolve().parents[2]; RECORD=ROOT/'docs'/'deployment.json'
pytestmark=pytest.mark.skipif(not RECORD.exists(),reason='deploy first: docs/deployment.json absent')

def _client():
    from genlayer_py import create_account,create_client
    from genlayer_py.chains import studionet
    return create_client(chain=studionet,account=create_account())

def test_protocols_are_chain_locked_and_wired():
    d=json.loads(RECORD.read_text()); c=_client()
    vp=c.read_contract(address=d['vault']['address'],function_name='get_protocol',args=[])
    cp=c.read_contract(address=d['court']['address'],function_name='get_protocol',args=[])
    assert int(vp['chain_id'])==61999==int(cp['chain_id'])
    assert cp['vault_address'].lower()==d['vault']['address'].lower()
    assert 'immutable' in vp['immutability'].lower()
    assert 'never the live page' in cp['evidence'].lower()

def test_custody_balances():
    d=json.loads(RECORD.read_text()); c=_client(); x=c.read_contract(address=d['court']['address'],function_name='get_custody',args=[])
    assert x['balanced'] is True
