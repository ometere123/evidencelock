import Link from "next/link";
import { WalletButton } from "./wallet-button";
export function Nav() {
  return <header className="nav"><Link className="brand" href="/">EVIDENCELOCK<span>↗</span></Link><nav>
    <Link href="/capture">Capture</Link><Link href="/register">Register</Link><Link href="/claims">Claims</Link><Link href="/registry">Registry</Link><Link href="/audit">Audit</Link>
  </nav><WalletButton /></header>;
}
