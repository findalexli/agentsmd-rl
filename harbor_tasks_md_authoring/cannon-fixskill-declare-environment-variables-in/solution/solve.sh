#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cannon

# Idempotency guard
if grep -qF "| `CANNON_ETHERSCAN_API_KEY` | Etherscan API key for contract verification (`can" "packages/skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/skill/SKILL.md b/packages/skill/SKILL.md
@@ -65,6 +65,17 @@ forge --version && anvil --version
 cannon --version
 ```
 
+## Environment Variables
+
+Cannon CLI recognizes the following environment variables. All Cannon-specific environment variables use the `CANNON_` prefix.
+
+| Variable | Description |
+|----------|------------|
+| `CANNON_PRIVATE_KEY` | Private key for signing on-chain transactions (deploy, publish, register). Required for non-dry-run operations on real networks. |
+| `CANNON_RPC_URL` | Ethereum RPC endpoint URL for target chain. Required for non-local deployments and publish operations. |
+| `CANNON_ETHERSCAN_API_KEY` | Etherscan API key for contract verification (`cannon verify`). Required for verifying deployed contracts on Etherscan-supported chains. |
+| `CANNON_DIRECTORY` | Custom directory for Cannon package storage and build artifacts. Defaults to `~/.local/share/cannon/` if not set. |
+
 ## Quick Reference
 
 For complete CLI options, see [references/cli.md](references/cli.md).
PATCH

echo "Gold patch applied."
