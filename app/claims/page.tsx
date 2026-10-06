"use client";
import Link from "next/link";
import { Chip } from "@/components/status";
import { readContract } from "@/lib/genlayer/client";
import { useAsync } from "@/lib/genlayer/hooks";
import { claimsPageSchema } from "@/lib/genlayer/types";
export default function ClaimsPage(){
  const q=useAsync(async()=>claimsPageSchema.parse(await readContract("court","list_claims",[0,50])),[]);
  return <section className="stack"><div><p className="eyebrow">ClaimCourt</p><h1>Claims.</h1><p className="lede">Canonical questions with protocol-owned evidence policy.</p></div>{q.error&&<p className="notice error">{q.error}</p>}<div className="table"><div className="row header"><span>Claim</span><span>Policy</span><span>Status</span><span>Evidence</span></div>{q.data?.items.map(c=><Link className="row" key={c.claim_id} href={`/claims/${c.claim_id}`}><span><b>{c.subject_label}</b><br/><span className="muted">{c.claim_id}</span></span><span>{c.policy_name}</span><span><Chip value={c.verdict||c.status}/></span><span>{c.evidence_count}</span></Link>)}{!q.loading&&!q.data?.items.length&&<div className="row"><span>No claims yet.</span></div>}</div></section>
}
