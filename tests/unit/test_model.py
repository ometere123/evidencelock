import pytest

from reference.model import (
    CONFIRMED, CONFLICTED, CONTRADICTS, ENTITY_STATUS, EVENT_OCCURRED,
    Evidence, INDEPENDENT_REPORTER, INSUFFICIENT, PRIMARY_OTHER,
    PUBLIC_ANNOUNCEMENT, PUBLIC_AUTHORITY, PUBLIC_RECORD, REFUTED, SILENT,
    SUBJECT_OFFICIAL, SUPPORTS, UNKNOWN, derive, policy, statement,
)

T = "2026-10-06T12:00:00Z"


def e(host, role, position, timely=True):
    return Evidence(host=host, publisher_role=role, position=position, timely=timely)


def test_claim_templates_are_protocol_owned():
    assert statement(PUBLIC_ANNOUNCEMENT, "Acme", "launch", T) == \
        "Did Acme publicly announce 'launch' on or before 2026-10-06T12:00:00Z?"
    assert "public status" in statement(ENTITY_STATUS, "Acme", "operational", T)
    assert "public-authority record" in statement(PUBLIC_RECORD, "Acme", "licensed", T)
    assert "occur" in statement(EVENT_OCCURRED, "Acme", "incident", T)


def test_announcement_requires_subject_official():
    assert derive(PUBLIC_ANNOUNCEMENT, [e("news.test", INDEPENDENT_REPORTER, SUPPORTS)])["verdict"] == INSUFFICIENT
    assert derive(PUBLIC_ANNOUNCEMENT, [e("acme.test", SUBJECT_OFFICIAL, SUPPORTS)])["verdict"] == CONFIRMED


def test_announcement_can_be_refuted_only_by_same_quality_floor():
    assert derive(PUBLIC_ANNOUNCEMENT, [e("news.test", INDEPENDENT_REPORTER, CONTRADICTS)])["verdict"] == INSUFFICIENT
    assert derive(PUBLIC_ANNOUNCEMENT, [e("acme.test", SUBJECT_OFFICIAL, CONTRADICTS)])["verdict"] == REFUTED


def test_entity_status_requires_two_origins_and_authoritative_anchor():
    one = [e("acme.test", SUBJECT_OFFICIAL, SUPPORTS)]
    assert derive(ENTITY_STATUS, one)["verdict"] == INSUFFICIENT
    two_same_host = one + [e("acme.test", INDEPENDENT_REPORTER, SUPPORTS)]
    assert derive(ENTITY_STATUS, two_same_host)["verdict"] == INSUFFICIENT
    two = one + [e("wire.test", INDEPENDENT_REPORTER, SUPPORTS)]
    assert derive(ENTITY_STATUS, two)["verdict"] == CONFIRMED


def test_entity_status_two_reporters_without_anchor_is_insufficient():
    items = [e("a.test", INDEPENDENT_REPORTER, SUPPORTS), e("b.test", PRIMARY_OTHER, SUPPORTS)]
    assert derive(ENTITY_STATUS, items)["verdict"] == INSUFFICIENT


def test_public_record_requires_public_authority():
    assert derive(PUBLIC_RECORD, [e("acme.test", SUBJECT_OFFICIAL, SUPPORTS)])["verdict"] == INSUFFICIENT
    assert derive(PUBLIC_RECORD, [e("reg.test", PUBLIC_AUTHORITY, SUPPORTS)])["verdict"] == CONFIRMED


def test_event_requires_two_independent_origins():
    assert derive(EVENT_OCCURRED, [e("a.test", PRIMARY_OTHER, SUPPORTS)])["verdict"] == INSUFFICIENT
    items = [e("a.test", PRIMARY_OTHER, SUPPORTS), e("b.test", INDEPENDENT_REPORTER, SUPPORTS)]
    assert derive(EVENT_OCCURRED, items)["verdict"] == CONFIRMED


def test_conflict_is_not_silently_ranked_away():
    items = [e("acme.test", SUBJECT_OFFICIAL, SUPPORTS), e("reg.test", PUBLIC_AUTHORITY, CONTRADICTS)]
    assert derive(ENTITY_STATUS, items)["verdict"] == CONFLICTED


def test_silent_never_counts():
    items = [e("a.test", PRIMARY_OTHER, SILENT), e("b.test", INDEPENDENT_REPORTER, SILENT)]
    assert derive(EVENT_OCCURRED, items)["verdict"] == INSUFFICIENT


def test_untimely_never_counts():
    items = [e("a.test", PRIMARY_OTHER, SUPPORTS, timely=False), e("b.test", INDEPENDENT_REPORTER, SUPPORTS)]
    assert derive(EVENT_OCCURRED, items)["verdict"] == INSUFFICIENT


def test_unknown_publisher_never_qualifies():
    items = [e("a.test", UNKNOWN, SUPPORTS), e("b.test", UNKNOWN, SUPPORTS)]
    assert derive(EVENT_OCCURRED, items)["verdict"] == INSUFFICIENT


def test_refutation_uses_same_thresholds_as_confirmation():
    one = [e("a.test", PRIMARY_OTHER, CONTRADICTS)]
    assert derive(EVENT_OCCURRED, one)["verdict"] == INSUFFICIENT
    two = one + [e("b.test", INDEPENDENT_REPORTER, CONTRADICTS)]
    assert derive(EVENT_OCCURRED, two)["verdict"] == REFUTED


def test_policy_names_are_frozen_by_kind():
    assert policy(PUBLIC_ANNOUNCEMENT)["name"] == "SUBJECT_SELF_PUBLICATION"
    assert policy(ENTITY_STATUS)["name"] == "STATUS_WITH_INDEPENDENT_CHECK"
    assert policy(PUBLIC_RECORD)["name"] == "PUBLIC_AUTHORITY_RECORD"
    assert policy(EVENT_OCCURRED)["name"] == "MULTI_ORIGIN_EVENT"


def test_invalid_kind_refused():
    with pytest.raises(ValueError):
        policy("CREATOR_MADE_THIS_UP")
