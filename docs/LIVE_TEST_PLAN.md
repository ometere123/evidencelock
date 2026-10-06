# Live test plan

All evidence must be generated from a fresh Studionet 61999 deployment.

1. Verify repository-local CLI is `0.39.1` and `genlayer network info` reports chain `61999`.
2. Deploy `EvidenceVault`; record address, deploy tx, source SHA-256 and finalized status.
3. Deploy `ClaimCourt(vault_address)`; record the same evidence.
4. Capture at least four public pages covering:
   - subject-official classification,
   - public-authority classification,
   - independent reporter,
   - prompt-injection-like document content.
5. Register one claim for each claim kind.
6. Attach snapshots and prove mismatched subject/kind/window snapshots fail.
7. Adjudicate cases reaching `CONFIRMED`, `REFUTED`, `CONFLICTED` and `INSUFFICIENT`.
8. Fund a bounty from an account different from the creator.
9. Use non-creator qualifying evidence so a contributor is the payout target.
10. Show adjudication accepted while bounty remains held.
11. Wait for protocol finalization and prove the finalized settlement message pays exactly once.
12. Re-run settlement and prove it fails.
13. Verify `get_custody().balanced == true` throughout.
14. Reload the frontend from scratch and recover all state only from chain reads.
15. Capture explorer links, transaction hashes and screenshots/video for submission evidence.

## Executable runner

The plan is backed by `scripts/live.py`; it is no longer documentation-only. Run
`python scripts/live.py --help` for required URLs. For the strongest proof, use a
controlled HTTPS page for the confirmed case, capture version A, change the public
page to materially different version B, then run with `--mutation-check-url` so the
record proves the vault body/hash remain version A while the live page differs.
