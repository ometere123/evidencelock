const rows=[
 ["Authority domains","Not accepted","Publisher role comes from capture consensus."],
 ["Free-form predicate","Not accepted","Claim kind selects a canonical contract template."],
 ["Source policy","Not accepted","Policy is fixed by claim kind."],
 ["Evidence thresholds","Not accepted","Minimum support and independence are protocol constants."],
 ["Live page during adjudication","Impossible by architecture","ClaimCourt contains no gl.nondet.web call."],
 ["Stored snapshot body","Required","Exact accepted bytes and SHA-256 commitments are retained."],
 ["Verdict from LLM","No","LLM/validators classify narrow readings; deterministic code derives verdict."],
 ["Settlement before finality","No","Bounty settlement is scheduled on finalized."],
];
export default function Audit(){return <section className="stack"><div><p className="eyebrow">Reviewer surface</p><h1>Audit.</h1><p className="lede">The trust boundary should be visible without reading 1,600 lines of one contract.</p></div><div className="table"><div className="row header"><span>Control</span><span>Caller power</span><span>Protocol rule</span><span>Result</span></div>{rows.map(([a,b,c])=><div className="row" key={a}><b>{a}</b><span>{b}</span><span>{c}</span><span>✓</span></div>)}</div><div className="panel acid"><h2>5/5/5 is a proof target, not a label.</h2><p>Fresh Direct Mode, GenVM lint, Studionet deployment, finalized lifecycle evidence and browser proof are still required before submission. This repository refuses to fake those artifacts.</p></div></section>}
