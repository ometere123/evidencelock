import { z } from "zod";

const num = z.union([z.number(), z.string()]).transform(Number);

export const claimSchema = z.object({
  claim_id: z.string(), creator: z.string(), claim_kind: z.string(),
  subject_key: z.string(), subject_label: z.string(), asserted_value: z.string(),
  statement: z.string(), relevant_time: z.string(), observation_start: z.string(),
  observation_end: z.string(), policy_name: z.string(), min_support: num,
  min_independent: num, status: z.string(), verdict: z.string(), result: z.string(),
  created_at: z.string(), adjudicated_at: z.string(), settled_at: z.string(),
  adjudication_id: z.string(), evidence_ids: z.array(z.string()), evidence_count: num,
  bounty_deposited: z.string(), bounty_depositor: z.string(), supersedes: z.string(),
  superseded_by: z.string(),
});
export type Claim = z.infer<typeof claimSchema>;

export const snapshotListItemSchema = z.object({
  snapshot_id: z.string(), subject_label: z.string(), claim_kind: z.string(),
  source_url: z.string(), source_host: z.string(), captured_at: z.string(),
  status: z.string(), publisher_role: z.string(), source_class: z.string(),
  content_sha256: z.string(), snapshot_sha256: z.string(), submitter: z.string(),
});
export type SnapshotListItem = z.infer<typeof snapshotListItemSchema>;

export const evidenceSchema = z.object({
  evidence_id: z.string(), snapshot_id: z.string(), submitter: z.string(),
  source_url: z.string(), source_host: z.string(), snapshot_sha256: z.string(),
  content_sha256: z.string(), publisher_role: z.string(), source_class: z.string(),
  captured_at: z.string(), position: z.string(), role: z.string(), event_time: z.string(),
  quote: z.string(), note: z.string(),
});
export type EvidenceRef = z.infer<typeof evidenceSchema>;

export const claimsPageSchema = z.object({ items: z.array(claimSchema), total: num, offset: num, limit: num });
export const snapshotsPageSchema = z.object({ items: z.array(snapshotListItemSchema), total: num, offset: num, limit: num });
export const claimEvidenceSchema = z.object({ claim_id: z.string(), items: z.array(evidenceSchema), total: num });
