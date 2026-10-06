def test_registration_exposes_protocol_owned_policy(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    # A syntactically valid vault address is enough for registration-only paths.
    court = direct_deploy("contracts/claim_court.py", ["0x1111111111111111111111111111111111111111"])
    cid = court.register_claim(
        "PUBLIC_ANNOUNCEMENT", "acme", "Acme", "launch completed",
        "2026-10-06T12:00:00Z", "2026-10-06T10:00:00Z", "2026-10-07T10:00:00Z",
    )
    claim = court.get_claim(cid)
    assert claim["policy_name"] == "SUBJECT_SELF_PUBLICATION"
    assert claim["min_support"] == 1
    assert "publicly announce" in claim["statement"]


def test_protocol_is_hard_locked_to_61999(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    court = direct_deploy("contracts/claim_court.py", ["0x1111111111111111111111111111111111111111"])
    assert court.get_protocol()["chain_id"] == 61999
