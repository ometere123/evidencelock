import json,pathlib,pytest
ROOT=pathlib.Path(__file__).resolve().parents[2]; LIVE=ROOT/'records'/'live_run.json'
pytestmark=pytest.mark.skipif(not LIVE.exists(),reason='run scripts/live.py first')

def test_live_record_proves_required_outcomes():
    d=json.loads(LIVE.read_text())
    assert d['chain_id']==61999
    verdicts={x['verdict'] for x in d.get('claims',{}).values()}
    assert {'CONFIRMED','REFUTED','CONFLICTED','INSUFFICIENT'} <= verdicts
    assert d.get('custody',{}).get('balanced') is True
    assert d.get('immutability_proof',{}).get('snapshot_body_unchanged') is True
    assert d.get('finality_proof',{}).get('accepted_before_finalized') is True
    assert d.get('finality_proof',{}).get('second_settlement_rejected') is True
