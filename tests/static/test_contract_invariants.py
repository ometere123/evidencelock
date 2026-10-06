from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = (ROOT / "contracts" / "evidence_vault.py").read_text(encoding="utf-8")
COURT = (ROOT / "contracts" / "claim_court.py").read_text(encoding="utf-8")


def test_no_creator_supplied_authority_domains_exist():
    joined = (VAULT + COURT).lower()
    assert "official_domains" not in joined
    assert "regulator_domains" not in joined


def test_register_claim_has_no_freeform_predicate_or_statement_parameter():
    signature = COURT.split("def register_claim", 1)[1].split(") -> str:", 1)[0]
    assert "predicate" not in signature
    assert "statement" not in signature
    assert "source_policy" not in signature
    assert "min_sources" not in signature
    assert "min_independent" not in signature


def test_adjudicator_never_fetches_live_web():
    adjudication_half = COURT.split("def _read_snapshot", 1)[1]
    assert "gl.nondet.web" not in adjudication_half


def test_only_vault_fetches_web():
    assert "gl.nondet.web" in VAULT
    assert "gl.nondet.web" not in COURT


def test_snapshot_stores_body_and_hashes():
    assert "content_sha256" in VAULT
    assert "snapshot_sha256" in VAULT
    assert "body: str" in VAULT


def test_chain_is_hard_locked_to_studionet():
    assert "CHAIN_ID = 61999" in VAULT
    assert "CHAIN_ID = 61999" in COURT
    assert "chain_id" in VAULT
    assert "chain_id" in COURT


def test_finalized_message_drives_settlement():
    assert 'emit(on="finalized").settle' in COURT


def test_payout_zeroes_ledger_before_transfer():
    section = COURT.split("def _release", 1)[1].split("@gl.public.write", 1)[0]
    assert section.index("claim.bounty_deposited = u256(0)") < section.index("emit_transfer")


def test_validator_reexecutes_capture_and_adjudication():
    assert "mine = leader_fn()" in VAULT
    assert "mine = leader_fn()" in COURT


def test_authority_is_validator_resolved():
    assert "publisher_role" in VAULT
    assert "The caller is not allowed to tell you who is authoritative" in VAULT


def test_claim_statement_is_generated_in_contract():
    assert "def _statement" in COURT
    assert "statement=_statement" in COURT
