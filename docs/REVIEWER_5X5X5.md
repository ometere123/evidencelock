# Reviewer target: 5 / 5 / 5

This file is a design argument, not a claim that a reviewer must award a score.

## GenLayer fit — target 5

GenLayer is used twice where a single trusted operator would be structurally unacceptable:

1. independent source capture and publisher-role resolution;
2. independent semantic reading of immutable snapshots.

The result controls persistent public state and bounty settlement. No centralized AI or backend can substitute for validator consensus.

The prior creator trust dependency is narrowed: claim prose, source authority domains and evidence thresholds are no longer creator-controlled.

## Contract quality — target 5

- External web content is committed at evidence submission, not re-read during adjudication.
- The exact accepted body is retained and hash-committed.
- The adjudicator has no web access.
- Privileged publisher roles require grounded identity evidence.
- Claim templates and policy thresholds are protocol-owned.
- Validators rerun both capture and interpretation work.
- Only consequence-bearing fields determine agreement.
- Deterministic code derives verdicts.
- Confirmation and refutation have symmetric source-quality floors.
- Bounty settlement waits for protocol finalization.

## Engineering — target 5

The project is separated into two purpose-specific ICs with a pure reference model and architecture-invariant tests. CI is designed to run Python compile, policy/static tests, GenVM lint, Direct Mode, frontend typecheck/test/build and preflight.

A real 5 requires fresh deployment evidence. Before submission, produce:

- clean Studionet 61999 deployments for both contracts;
- source hashes and on-chain source verification;
- adversarial Direct Mode including leader/validator disagreement;
- live capture → attach → adjudicate → finalized payout lifecycle;
- wrong-network frontend hard gate;
- accepted-vs-finalized UI evidence;
- explorer links and fresh transaction hashes.
