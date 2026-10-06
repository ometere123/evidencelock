"use client";
import { useParams } from "next/navigation";
import { Chip, Hash } from "@/components/status";
import { readContract, writeContract } from "@/lib/genlayer/client";
import { useAsync } from "@/lib/genlayer/hooks";
import { claimEvidenceSchema, claimSchema } from "@/lib/genlayer/types";
import { useWallet } from "@/lib/wallet/provider";
import { CHAIN_ID } from "@/lib/genlayer/env";
import { useState } from "react";
import { TransactionNotice } from "@/components/transaction";

export default function ClaimPage(){
 const {id}=useParams<{id:string}>(); const wallet=useWallet(); const [snapshot,setSnapshot]=useState(""); const [msg,setMsg]=useState(""); const [tx,setTx]=useState("");
 const claim=useAsync(async()=>claimSchema.parse(await readContract("court","get_claim",[id])),[id]);
 const evidence=useAsync(async()=>claimEvidenceSchema.parse(await readContract("court","get_claim_evidence",[id])),[id]);
 async function write(fn:string,args:unknown[]){setTx("");if(!wallet.provider||!wallet.address||wallet.chainId!==CHAIN_ID){setMsg("Connect an injected wallet on chain 61999 first.");return;}try{const hash=String(await writeContract("court",wallet.address,wallet.provider,fn,args));setTx(hash);setMsg("Submitted to Studionet. ACCEPTED is not FINALIZED.");await Promise.all([claim.refresh(),evidence.refresh()]);}catch(e){setMsg(e instanceof Error?e.message:String(e));}}
 if(claim.loading)return <p>Reading claim…</p>; if(claim.error||!claim.data)return <p className="notice error">{claim.error||"Claim unavailable"}</p>; const c=claim.data;
 return <section className="stack"><div><p className="eyebrow">{c.claim_id} · {c.claim_kind}</p><h1>{c.subject_label}.</h1><p className="lede">{c.statement}</p><Chip value={c.verdict||c.status}/></div><div className="panel"><dl><div className="detail"><dt>Protocol policy</dt><dd>{c.policy_name} · support ≥ {c.min_support} · independent ≥ {c.min_independent}</dd></div><div className="detail"><dt>Relevant time</dt><dd>{c.relevant_time}</dd></div><div className="detail"><dt>Evidence window</dt><dd>{c.observation_start} → {c.observation_end}</dd></div><div className="detail"><dt>Bounty held</dt><dd>{c.bounty_deposited} wei</dd></div></dl></div>
 <div className="panel"><p className="kicker">Attach immutable evidence</p><div className="grid cols-2"><input value={snapshot} onChange={e=>setSnapshot(e.target.value)} placeholder="S-000001"/><button className="button" onClick={()=>void write("attach_snapshot",[id,snapshot])}>Attach snapshot</button></div></div>
 <div><div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}><h2>Evidence</h2><button className="button" onClick={()=>void write("adjudicate",[id])}>Adjudicate</button></div><div className="table"><div className="row header"><span>Snapshot</span><span>Publisher</span><span>Position</span><span>Commitment</span></div>{evidence.data?.items.map(x=><div className="row" key={x.evidence_id}><span>{x.snapshot_id}<br/><span className="muted">{x.source_host}</span></span><span><Chip value={x.publisher_role}/></span><span>{x.position||"—"}</span><span><Hash value={x.snapshot_sha256}/></span></div>)}</div></div>{tx?<TransactionNotice label="Transaction submitted" hash={tx}/>:msg&&<p className="notice">{msg}</p>}</section>;
}
