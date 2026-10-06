"""Direct Mode tests for the finishing environment.

These require `genlayer-test`; the package-generation environment intentionally
runs only the pure/static suites. The handoff makes passing these a deployment
gate.
"""


def test_capture_rejects_non_https(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    vault = direct_deploy("contracts/evidence_vault.py")
    with direct_vm.expect_revert("https URL"):
        vault.capture_snapshot("acme", "Acme", "PUBLIC_ANNOUNCEMENT", "http://example.com")


def test_capture_persists_immutable_commitment(direct_vm, direct_deploy, direct_alice):
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r"example\\.com", {"status": 200, "body": "<html><body>Acme official service announces launch is complete today.</body></html>"})
    direct_vm.mock_llm(r"verifying provenance", {
        "publisher_role": "SUBJECT_OFFICIAL", "publisher_label": "Acme",
        "source_class": "PRIMARY", "publication_time": "2026-10-06T12:00:00Z",
        "title": "Launch", "identity_quote": "Acme official service announces launch is complete",
    })
    direct_vm.mock_llm(r"Compare two independently", {"same_material_content": True})
    vault = direct_deploy("contracts/evidence_vault.py")
    sid = vault.capture_snapshot("acme", "Acme", "PUBLIC_ANNOUNCEMENT", "https://example.com")
    snap = vault.get_snapshot(sid)
    assert snap["snapshot_sha256"]
    assert snap["content_sha256"]
    assert snap["body"]
    assert snap["publisher_role"] == "SUBJECT_OFFICIAL"
