"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { CHAIN_ID } from "@/lib/genlayer/env";

type Provider = { request(args: { method: string; params?: unknown[] | object }): Promise<unknown> };
type Announced = { info: { uuid: string; name: string }; provider: Provider };
type WalletState = {
  address: string; chainId: number; provider?: Provider; providers: Announced[];
  connect(uuid?: string): Promise<void>; disconnect(): void; switchNetwork(): Promise<void>;
};
const Ctx = createContext<WalletState | null>(null);

function parseChain(raw: unknown) { return typeof raw === "string" ? Number.parseInt(raw, 16) : Number(raw || 0); }

export function WalletProvider({ children }: { children: React.ReactNode }) {
  const [providers, setProviders] = useState<Announced[]>([]);
  const [provider, setProvider] = useState<Provider>();
  const [address, setAddress] = useState("");
  const [chainId, setChainId] = useState(0);

  useEffect(() => {
    const found = new Map<string, Announced>();
    const announce = (event: Event) => {
      const detail = (event as CustomEvent<Announced>).detail;
      if (!detail?.info?.uuid || !detail.provider) return;
      found.set(detail.info.uuid, detail); setProviders([...found.values()]);
    };
    window.addEventListener("eip6963:announceProvider", announce as EventListener);
    window.dispatchEvent(new Event("eip6963:requestProvider"));
    const fallback = (window as unknown as { ethereum?: Provider }).ethereum;
    if (fallback) {
      const item = { info: { uuid: "window.ethereum", name: "Injected wallet" }, provider: fallback };
      found.set(item.info.uuid, item); setProviders([...found.values()]);
    }
    return () => window.removeEventListener("eip6963:announceProvider", announce as EventListener);
  }, []);

  async function connect(uuid?: string) {
    const chosen = (uuid ? providers.find((p) => p.info.uuid === uuid) : providers[0])?.provider;
    if (!chosen) throw new Error("No injected EIP-1193 wallet found");
    const accounts = await chosen.request({ method: "eth_requestAccounts" }) as string[];
    const chain = await chosen.request({ method: "eth_chainId" });
    setProvider(chosen); setAddress(accounts?.[0] ?? ""); setChainId(parseChain(chain));
  }
  function disconnect() { setProvider(undefined); setAddress(""); setChainId(0); }
  async function switchNetwork() {
    if (!provider) return;
    await provider.request({ method: "wallet_switchEthereumChain", params: [{ chainId: `0x${CHAIN_ID.toString(16)}` }] });
    setChainId(CHAIN_ID);
  }
  const value = useMemo(() => ({ address, chainId, provider, providers, connect, disconnect, switchNetwork }),
    [address, chainId, provider, providers]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useWallet() {
  const value = useContext(Ctx); if (!value) throw new Error("WalletProvider missing"); return value;
}
