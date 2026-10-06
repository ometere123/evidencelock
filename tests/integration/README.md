# Studionet integration requirements

The final repository must add executable integration tests against the fresh deployed addresses and keep the evidence they produce.

Required cases:

- both deployed contract sources match repository SHA-256;
- EvidenceVault protocol reports chain 61999;
- ClaimCourt points to the exact deployed vault;
- snapshot capture persists body/content hash/snapshot hash;
- creator cannot supply authority fields because no method accepts them;
- mismatched subject key, claim kind and capture window all reject on attach;
- one lifecycle each for CONFIRMED / REFUTED / CONFLICTED / INSUFFICIENT;
- bounty balance invariant before and after settlement;
- accepted adjudication does not equal finalized settlement;
- finalized settlement pays exactly once;
- reload reads final state without any backend/indexer.
