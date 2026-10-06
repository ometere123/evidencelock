import { createClient } from "genlayer-js";
import { studionet } from "genlayer-js/chains";
import { env } from "./env";

export function readClient() {
  const cfg = env();
  return createClient({ chain: { ...studionet, id: cfg.chainId } });
}

export function walletClient(address: string, provider: unknown) {
  const cfg = env();
  return createClient({
    chain: { ...studionet, id: cfg.chainId },
    account: address as `0x${string}`,
    provider,
  } as never);
}

export async function readContract<T>(which: "vault" | "court", functionName: string, args: unknown[] = []) {
  const cfg = env();
  const client = readClient();
  return await client.readContract({
    address: cfg[which] as `0x${string}`,
    functionName,
    args: args as never,
    transactionHashVariant: "latest-final" as never,
  }) as T;
}

export async function writeContract(
  which: "vault" | "court",
  address: string,
  provider: unknown,
  functionName: string,
  args: unknown[] = [],
  value?: bigint,
) {
  const cfg = env();
  const client = walletClient(address, provider);
  const call = {
    address: cfg[which] as `0x${string}`,
    functionName,
    args: args as never,
    ...(value !== undefined ? { value } : {}),
  };
  return await client.writeContract({
    ...call,
    // genlayer-js 1.1.8 signs the contract call itself and requires an explicit
    // value (zero for non-payable calls); it has no fee-distribution API.
    value: value ?? 0n,
  } as never);
}
