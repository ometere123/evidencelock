"use client";
import { useState } from "react";
import { CHAIN_ID } from "@/lib/genlayer/env";
import { useWallet } from "@/lib/wallet/provider";

export function WalletButton() {
  const wallet = useWallet();
  const [error, setError] = useState("");
  if (!wallet.address) return <button className="button" onClick={() => void wallet.connect().catch(e => setError(String(e)))}>{error ? "Retry wallet" : "Connect wallet"}</button>;
  if (wallet.chainId !== CHAIN_ID) return <button className="button danger" onClick={() => void wallet.switchNetwork().catch(e => setError(String(e)))}>Wrong network · switch to 61999</button>;
  return <button className="wallet" onClick={wallet.disconnect}>{wallet.address.slice(0, 6)}…{wallet.address.slice(-4)}</button>;
}
