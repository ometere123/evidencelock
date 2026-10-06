import { z } from "zod";

const address = z.string().regex(/^0x[0-9a-fA-F]{40}$/);
const schema = z.object({
  chainId: z.coerce.number().int().positive(),
  vault: address,
  court: address,
});

const raw = {
  chainId: process.env.NEXT_PUBLIC_CHAIN_ID,
  vault: process.env.NEXT_PUBLIC_EVIDENCE_VAULT,
  court: process.env.NEXT_PUBLIC_CLAIM_COURT,
};

export const envResult = schema.safeParse(raw);
export const CHAIN_ID = 61999;
export const NETWORK_NAME = "GenLayer Studionet";
export const EXPLORER = "https://explorer-studio.genlayer.com";

export function env() {
  if (!envResult.success) throw new Error("Missing or invalid EVIDENCELOCK deployment configuration");
  if (envResult.data.chainId !== CHAIN_ID) throw new Error("EVIDENCELOCK frontend is locked to chain 61999");
  return envResult.data;
}

export const explorerTx = (hash: string) => `${EXPLORER}/tx/${hash}`;
export const explorerAddress = (value: string) => `${EXPLORER}/address/${value}`;
