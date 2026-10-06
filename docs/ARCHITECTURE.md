# Architecture

## Security boundary

EVIDENCELOCK separates two facts that should never share one mutable web fetch.

### Phase A — evidence capture

`EvidenceVault.capture_snapshot(...)` receives only:

- a stable subject key,
- a human subject label,
- a fixed claim kind,
- an HTTPS URL.

It does **not** accept `official_domains`, `regulator_domains`, an authority label, a source class, or a verdict hint.

The leader retrieves the page and produces a bounded snapshot plus provenance classification. Validators retrieve the same URL independently. Consequence-bearing provenance fields must agree, privileged publisher roles require grounded identity evidence, and materially different page content is rejected. The accepted exact snapshot is stored with both `content_sha256` and a full `snapshot_sha256` commitment.

### Phase B — claim adjudication

`ClaimCourt` reads the attached snapshot from `EvidenceVault` by view call and verifies its stored commitment against the commitment recorded when it was attached. It then gives the **stored body** — not the URL — to the adjudication round.

No `gl.nondet.web.*` call exists anywhere in `claim_court.py`.

## Why two contracts

The split is deliberate audit-surface reduction:

- `EvidenceVault` owns external-world acquisition and immutable capture.
- `ClaimCourt` owns the claim/economic lifecycle.

A compromise or reasoning bug in one domain is easier to isolate and test. The court's money-moving code has no web retrieval logic at all.

## Claim framing

A caller chooses only a supported claim kind and structured values. The contract itself renders the canonical question. This removes a hidden prompt-control channel where two superficially identical claims could be adjudicated under materially different prose.

The policy preset is also selected by claim kind in contract code. The claimant cannot reduce evidence thresholds after choosing a convenient question.
