"use client";
import { Chip, Hash } from "@/components/status";
import { readContract } from "@/lib/genlayer/client";
import { useAsync } from "@/lib/genlayer/hooks";
import { snapshotsPageSchema } from "@/lib/genlayer/types";
export default function Registry(){const q=useAsync(async()=>snapshotsPageSchema.parse(await readContract("vault","list_snapshots",[0,50])),[]);return <section className="stack"><div><p className="eyebrow">EvidenceVault</p><h1>Registry.</h1><p className="lede">Every row is an immutable consensus-captured source artifact, not a live URL preview.</p></div>{q.error&&<p className="notice error">{q.error}</p>}<div className="table"><div className="row header"><span>Snapshot</span><span>Publisher role</span><span>Captured</span><span>Hash</span></div>{q.data?.items.map(s=><div className="row" key={s.snapshot_id}><span><b>{s.snapshot_id}</b><br/><span className="muted">{s.source_host}</span></span><span><Chip value={s.publisher_role}/></span><span>{s.captured_at}</span><span><Hash value={s.snapshot_sha256}/></span></div>)}</div></section>}
