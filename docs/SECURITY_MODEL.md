# Security model

## Threats addressed

### Mutable source substitution

A page can change after submission. EVIDENCELOCK fixes this by consensus-capturing the accepted body at evidence time and adjudicating the stored body later.

### Creator-selected authority

A claimant cannot label a domain authoritative. Publisher role is part of the capture consensus result and privileged roles require grounded identity evidence from the captured page.

### Prompt framing

The caller never supplies the adjudication statement. `ClaimCourt` generates it from fixed templates.

### Asymmetric proof burden

Confirmation and refutation use the same quality floor. A weak contradictory blog cannot refute a claim that would require a public authority to confirm.

### Duplicate/echo sources

Independence is counted by distinct source host. Multiple URLs from one host do not satisfy an independence threshold.

### Prompt injection in evidence

Both capture and adjudication prompts state that document text is evidence, not instruction. Decisive claim readings require a quote grounded in the stored snapshot.

### Finality confusion

Adjudication records `ACCEPTED`. Bounty settlement is scheduled with `emit(on="finalized")`; the application is not allowed to declare protocol finality itself.

### Custody imbalance

The court tracks aggregate escrow and exposes `get_custody()`. The payout path zeroes the per-claim ledger before emitting value.

## What a finalized decision does not prove

It does not prove universal truth. It proves that the protocol-owned claim, attached immutable snapshots and fixed policy produced the recorded verdict under GenLayer consensus.

Publisher-role classification is itself a consensus judgment over public evidence. Reviewers should treat it as a stronger neutral mechanism than creator-supplied domains, not as a cryptographic DNS/PKI ownership proof.
