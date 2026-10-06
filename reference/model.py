"""Pure deterministic reference model for EVIDENCELOCK policy and verdict logic.

This file is intentionally GenLayer-free so mutation/unit tests can exercise the
same policy semantics without a VM.
"""

from dataclasses import dataclass
from typing import Iterable

PUBLIC_ANNOUNCEMENT = "PUBLIC_ANNOUNCEMENT"
ENTITY_STATUS = "ENTITY_STATUS"
EVENT_OCCURRED = "EVENT_OCCURRED"
PUBLIC_RECORD = "PUBLIC_RECORD"

SUBJECT_OFFICIAL = "SUBJECT_OFFICIAL"
PUBLIC_AUTHORITY = "PUBLIC_AUTHORITY"
INDEPENDENT_REPORTER = "INDEPENDENT_REPORTER"
PRIMARY_OTHER = "PRIMARY_OTHER"
UNKNOWN = "UNKNOWN"

SUPPORTS = "SUPPORTS"
CONTRADICTS = "CONTRADICTS"
SILENT = "SILENT"

CONFIRMED = "CONFIRMED"
REFUTED = "REFUTED"
CONFLICTED = "CONFLICTED"
INSUFFICIENT = "INSUFFICIENT"


@dataclass(frozen=True)
class Evidence:
    host: str
    publisher_role: str
    position: str
    timely: bool = True


def policy(kind: str) -> dict:
    if kind == PUBLIC_ANNOUNCEMENT:
        return dict(name="SUBJECT_SELF_PUBLICATION", min_support=1,
                    min_independent=1, required_any={SUBJECT_OFFICIAL},
                    qualifying={SUBJECT_OFFICIAL})
    if kind == ENTITY_STATUS:
        return dict(name="STATUS_WITH_INDEPENDENT_CHECK", min_support=2,
                    min_independent=2,
                    required_any={SUBJECT_OFFICIAL, PUBLIC_AUTHORITY},
                    qualifying={SUBJECT_OFFICIAL, PUBLIC_AUTHORITY,
                                INDEPENDENT_REPORTER, PRIMARY_OTHER})
    if kind == PUBLIC_RECORD:
        return dict(name="PUBLIC_AUTHORITY_RECORD", min_support=1,
                    min_independent=1, required_any={PUBLIC_AUTHORITY},
                    qualifying={PUBLIC_AUTHORITY})
    if kind == EVENT_OCCURRED:
        return dict(name="MULTI_ORIGIN_EVENT", min_support=2,
                    min_independent=2, required_any=set(),
                    qualifying={SUBJECT_OFFICIAL, PUBLIC_AUTHORITY,
                                INDEPENDENT_REPORTER, PRIMARY_OTHER})
    raise ValueError("unsupported claim kind")


def statement(kind: str, subject: str, value: str, relevant_time: str) -> str:
    if kind == PUBLIC_ANNOUNCEMENT:
        return f"Did {subject} publicly announce '{value}' on or before {relevant_time}?"
    if kind == ENTITY_STATUS:
        return f"Was the public status of {subject} '{value}' at {relevant_time}?"
    if kind == PUBLIC_RECORD:
        return f"Did a public-authority record establish '{value}' for {subject} by {relevant_time}?"
    if kind == EVENT_OCCURRED:
        return f"Did '{value}' involving {subject} occur on or before {relevant_time}?"
    raise ValueError("unsupported claim kind")


def _qualified(items: Iterable[Evidence], p: dict):
    return [x for x in items if x.timely and x.publisher_role in p["qualifying"]
            and x.position in {SUPPORTS, CONTRADICTS}]


def _meets_floor(items: list[Evidence], p: dict) -> bool:
    hosts = {x.host for x in items}
    role_ok = not p["required_any"] or any(x.publisher_role in p["required_any"] for x in items)
    return len(items) >= p["min_support"] and len(hosts) >= p["min_independent"] and role_ok


def derive(kind: str, evidence: Iterable[Evidence]) -> dict:
    p = policy(kind)
    q = _qualified(evidence, p)
    supporting = [x for x in q if x.position == SUPPORTS]
    contradicting = [x for x in q if x.position == CONTRADICTS]
    if supporting and contradicting:
        verdict = CONFLICTED
    elif _meets_floor(supporting, p):
        verdict = CONFIRMED
    elif not supporting and _meets_floor(contradicting, p):
        verdict = REFUTED
    else:
        verdict = INSUFFICIENT
    return {
        "verdict": verdict,
        "supporting": len(supporting),
        "contradicting": len(contradicting),
        "independent_supporting": len({x.host for x in supporting}),
        "policy": p["name"],
    }
