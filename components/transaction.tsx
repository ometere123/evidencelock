"use client";

import { explorerTx } from "@/lib/genlayer/env";

export function TransactionNotice({ label, hash }: { label: string; hash: string }) {
  return <p className="notice">{label}: <a href={explorerTx(hash)} target="_blank" rel="noreferrer"><code>{hash}</code> · View on Studionet explorer</a></p>;
}
