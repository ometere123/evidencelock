import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/nav";
import { WalletProvider } from "@/lib/wallet/provider";

export const metadata: Metadata = { title: "EVIDENCELOCK", description: "Public evidence, frozen before judgment." };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body><WalletProvider><Nav /><main>{children}</main><footer><span>EVIDENCELOCK / STUDIONET 61999</span><span>NO BACKEND · INJECTED WALLET ONLY</span></footer></WalletProvider></body></html>;
}
