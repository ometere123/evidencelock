from __future__ import annotations

import hashlib
import json
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "contracts/evidence_vault.py", "contracts/claim_court.py", "reference/model.py",
    "app/page.tsx", "app/capture/page.tsx", "app/register/page.tsx",
    "app/claims/page.tsx", "app/claims/[id]/page.tsx", "app/registry/page.tsx",
    "app/audit/page.tsx", "lib/wallet/provider.tsx", "docs/REVIEWER_5X5X5.md",
    "docs/LIVE_TEST_PLAN.md", "EVIDENCELOCK_CODEX_MASTER_HANDOFF.txt",
    "scripts/deploy.py", "scripts/verify_deployment.py", "scripts/live.py",
    "scripts/check_records.py", "scripts/network_guard.py", "scripts/fee_profile.py",
    "tests/integration/test_deployment.py", "tests/integration/test_live_record.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    problems: list[str] = []
    for rel in REQUIRED:
        if not (ROOT / rel).exists():
            problems.append(f"missing {rel}")

    for rel in ["contracts/evidence_vault.py", "contracts/claim_court.py", "reference/model.py"]:
        try:
            py_compile.compile(str(ROOT / rel), doraise=True)
        except Exception as exc:
            problems.append(f"compile {rel}: {exc}")

    vault = (ROOT / "contracts/evidence_vault.py").read_text(encoding="utf-8")
    court = (ROOT / "contracts/claim_court.py").read_text(encoding="utf-8")
    joined = vault + "\n" + court
    checks = {
        "chain lock 61999 in vault": "CHAIN_ID = 61999" in vault,
        "chain lock 61999 in court": "CHAIN_ID = 61999" in court,
        "no creator official domains": "official_domains" not in joined.lower(),
        "no creator regulator domains": "regulator_domains" not in joined.lower(),
        "court has no web nondeterminism": "gl.nondet.web" not in court,
        "vault stores content hash": "content_sha256" in vault,
        "vault stores snapshot hash": "snapshot_sha256" in vault,
        "finalized settlement": 'emit(on="finalized").settle' in court,
        "no Next API routes": not (ROOT / "app/api").exists(),
        "CLI pinned": '"genlayer": "0.39.1"' in (ROOT / "package.json").read_text(encoding="utf-8"),
        "deploy waits FINALIZED": "status='FINALIZED'" in (ROOT / "scripts/deploy.py").read_text(encoding="utf-8"),
        "deploy checks execution": "execution(r" in (ROOT / "scripts/deploy.py").read_text(encoding="utf-8") or "execution(receipt" in (ROOT / "scripts/deploy.py").read_text(encoding="utf-8"),
        "integration tests executable": (ROOT / "tests/integration/test_deployment.py").exists(),
        "live runner executable": (ROOT / "scripts/live.py").exists(),
    }
    for label, ok in checks.items():
        if not ok:
            problems.append(label)

    manifest = {
        "contracts": {
            "evidence_vault.py": sha(ROOT / "contracts/evidence_vault.py"),
            "claim_court.py": sha(ROOT / "contracts/claim_court.py"),
        },
        "network": {"chain_id": 61999, "rpc": "https://studio.genlayer.com/api"},
        "status": "PASS" if not problems else "FAIL",
        "problems": problems,
    }
    (ROOT / "BUILD_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
