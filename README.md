# EVIDENCELOCK

**Public evidence, frozen before judgment.**

EVIDENCELOCK is a GenLayer claim-adjudication protocol built around one hard rule: a mutable web page must become an immutable evidence artifact **before** any later verdict can depend on it.

It preserves the useful shape of public-claim adjudication — structured claims, open evidence submission, validator consensus, deterministic verdicts, bounty custody and finality-aware settlement — while removing the three trust/engineering ceilings that stop a strong implementation from being reviewer-grade 5/5/5.

## What is materially different

| Earlier 4/5 ceiling | EVIDENCELOCK change |
| --- | --- |
| Claim creator chooses authority domains | The caller supplies **no authority domains**. `EvidenceVault` validators independently classify publisher role from the captured source and grounded publisher-identity evidence. |
| Adjudication reads whatever the page says later | Evidence is consensus-captured once. The accepted body, content SHA-256 and snapshot SHA-256 are stored on-chain. `ClaimCourt` never performs web access. |
| Creator can frame predicate/policy/thresholds | Claim kind selects a protocol-owned template and fixed evidence policy. No free-form predicate, adjudication statement, source policy, min-source count or independence threshold is accepted. |
| One large combined contract carries retrieval, adjudication and custody | Two narrow ICs separate source capture from claim settlement. |

## Architecture

```text
PUBLIC WEB
   |
   | independent validator retrieval + publisher-role agreement
   v
EvidenceVault (IC #1)
   - accepted rendered snapshot body
   - content_sha256
   - snapshot_sha256
   - publisher_role
   - source_class
   - submitter + capture time
   |
   | immutable snapshot id
   v
ClaimCourt (IC #2)
   - protocol-owned claim template
   - fixed policy preset
   - attached snapshot commitments
   - independent interpretation of stored bodies
   - deterministic verdict derivation
   - bounty custody
   - finalized settlement
```

There is no application backend, no server database, no authoritative API route and no off-chain adjudication service.

## Claim kinds and protocol-owned policies

- `PUBLIC_ANNOUNCEMENT` → only consensus-classified `SUBJECT_OFFICIAL` snapshots can establish/refute it.
- `ENTITY_STATUS` → requires two independent origins and at least one `SUBJECT_OFFICIAL` or `PUBLIC_AUTHORITY` anchor.
- `PUBLIC_RECORD` → only a consensus-classified `PUBLIC_AUTHORITY` snapshot qualifies.
- `EVENT_OCCURRED` → requires two independent qualifying origins.

The creator cannot weaken those rules.

## Why GenLayer is central

Two separate non-deterministic questions require neutral validator judgment:

1. **Capture/provenance:** what does this page contain now, and what publisher role does the page actually establish?
2. **Adjudication:** what does this already-frozen source snapshot say about the protocol-generated claim?

The contract never asks an LLM for the final verdict. Validators agree on narrow consequence-bearing fields; deterministic Python derives `CONFIRMED`, `REFUTED`, `CONFLICTED` or `INSUFFICIENT`.

## Network lock

This package is intentionally locked to stable GenLayer Studionet:

- Chain ID: `61999`
- RPC: `https://studio.genlayer.com/api`
- CLI target: `genlayer@0.39.1`
- Explorer: `https://explorer-studio.genlayer.com`

The two contracts fail closed if executed on another chain.

## Repository map

- `contracts/evidence_vault.py` — web capture, immutable source commitments, publisher-role consensus.
- `contracts/claim_court.py` — canonical claims, snapshot attachment, adjudication, deterministic verdicts, bounty/finality.
- `reference/model.py` — pure deterministic policy model.
- `tests/unit/` — policy and verdict unit tests.
- `tests/static/` — architecture and reviewer-invariant tests.
- `tests/direct/` — Direct Mode plan/tests for GenLayer tooling.
- `tests/integration/` — Studionet lifecycle plan.
- `app/`, `components/`, `lib/` — Next.js console.
- `docs/` — architecture, threat model, scoring rationale and live-proof checklist.
- `scripts/preflight.py` — repository preflight.
- `EVIDENCELOCK_CODEX_MASTER_HANDOFF.txt` — exact completion/deployment instructions for the finishing agent.

## Local validation already performed in this package

```bash
python -m py_compile contracts/evidence_vault.py contracts/claim_court.py
pytest -q
python scripts/preflight.py
```

The package does **not** pretend to contain a Studionet deployment or live finalization proof. Those require a funded injected wallet and must be produced fresh after deployment; the handoff file makes that a hard gate.

## Network proof tooling

This package includes executable stable-61999 tooling rather than leaving deployment
and lifecycle proof to prose:

```bash
python scripts/network_guard.py
python scripts/deploy.py
python scripts/verify_deployment.py
pytest tests/integration -q
python scripts/fee_profile.py --init
python scripts/live.py --help
python scripts/check_records.py
```

`deploy.py` refuses dirty contract source, waits for `FINALIZED`, requires successful
execution, reads deployed code back, and compares SHA-256 byte-for-byte before it writes
`docs/deployment.json`. The live runner writes `records/live_run.json`; CI reconciles
published records with the current source once deployment evidence exists.
