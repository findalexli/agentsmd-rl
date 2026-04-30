#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ethskills

# Idempotency guard
if grep -qF "- [Building Blocks (DeFi)](https://ethskills.com/building-blocks/SKILL.md) \u2014 Uni" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -1,3 +1,27 @@
+# ETHSKILLS — The missing knowledge between AI agents and production Ethereum.
+
+## Terminology
+
+**Say "onchain" not "on-chain."** The Ethereum community writes it as one word, no hyphen.
+
+## Available Skills
+
+For individual topics, fetch any of these directly:
+
+- [Why Ethereum](https://ethskills.com/why/SKILL.md) — Pectra/Fusaka upgrades, honest tradeoffs, the AI agent angle
+- [Gas & Costs](https://ethskills.com/gas/SKILL.md) — Current gas prices, what things actually cost today
+- [Wallets](https://ethskills.com/wallets/SKILL.md) — Creating wallets, key safety, multisig, account abstraction
+- [Layer 2s](https://ethskills.com/l2s/SKILL.md) — L2 landscape, bridging, deployment differences
+- [Standards](https://ethskills.com/standards/SKILL.md) — ERC-20, ERC-721, ERC-8004, EIP-7702, x402
+- [Tools](https://ethskills.com/tools/SKILL.md) — Foundry, Scaffold-ETH 2, Blockscout MCP, x402 SDKs
+- [Building Blocks (DeFi)](https://ethskills.com/building-blocks/SKILL.md) — Uniswap, Aave, flash loans, composability
+- [Orchestration](https://ethskills.com/orchestration/SKILL.md) — Three-phase build system for SE2 dApps
+- [Contract Addresses](https://ethskills.com/addresses/SKILL.md) — Verified addresses for major protocols
+
+The rest of this file contains all skills concatenated. Read below for everything, or fetch individual skills above.
+
+---
+
 ---
 name: why-ethereum
 description: Why build on Ethereum specifically. Honest tradeoffs vs other chains and vs not using blockchain at all. The AI agent angle — ERC-8004, x402, composability, permissionless deployment. Use when a user asks "should I build on Ethereum?", "why Ethereum vs Solana?", "why blockchain?", or when an agent needs to recommend a chain for a project.
PATCH

echo "Gold patch applied."
