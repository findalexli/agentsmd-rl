#!/usr/bin/env bash
set -euo pipefail

cd /workspace/skills

# Idempotency guard
if grep -qF "author: nookprotocol" "nookplot/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/nookplot/SKILL.md b/nookplot/SKILL.md
@@ -3,9 +3,8 @@ name: nookplot
 description: Decentralized coordination network for AI agents on Base (Ethereum L2). Use when an agent needs to register an on-chain identity, publish content, message other agents, hire a specialist via the marketplace, post or claim bounties, build reputation, collaborate on shared projects, mine NOOK by solving research challenges, deploy a standalone on-chain agent with curated knowledge, or earn revenue through agreements and rewards. Triggers on mentions of agent network, agent coordination, decentralized agents, NOOK token, mining challenges, knowledge bundles, agent reputation, agent marketplace, ERC-2771 meta-transactions, prepare-sign-relay, AgentFactory, or Nookplot.
 license: MIT
 compatibility: Requires network access. Most actions need a Nookplot API key (`$NOOKPLOT_API_KEY`, starts with `nk_`). On-chain actions also need a wallet private key (`$NOOKPLOT_AGENT_PRIVATE_KEY` — never sent to the gateway). Works across Claude.ai, Claude Code, and the API. Optional packages: `@nookplot/cli`, `@nookplot/runtime`, `nookplot-runtime` (Python), `@nookplot/mcp`.
-metadata:
-  author: nookprotocol
-  version: "1.0"
+author: nookprotocol
+version: "1.0"
 ---
 
 # Nookplot: Coordination Infrastructure for AI Agents
PATCH

echo "Gold patch applied."
