#!/usr/bin/env bash
set -euo pipefail

cd /workspace/evolver

# Idempotency guard
if grep -qF "> **DO NOT manually construct HTTP requests for the A2A protocol** (doing so oft" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -198,6 +198,15 @@ Evolver communicates with these external services. All are authenticated and doc
 | `api.github.com/repos/*/issues` | `GITHUB_TOKEN` (Bearer) | Auto-create failure reports (sanitized via `redactString()`) | No |
 | `{MEMORY_GRAPH_REMOTE_URL}/*` | `MEMORY_GRAPH_REMOTE_KEY` | Remote knowledge graph sync | No |
 
+> **🤖 AI Agent Usage Tip (A2A Protocol Encapsulation):**
+> Evolver provides a highly complete encapsulation of the EvoMap A2A protocol. Almost every endpoint in `{A2A_HUB_URL}/a2a/*` has a robust, production-ready wrapper method.
+> **DO NOT manually construct HTTP requests for the A2A protocol** (doing so often leads to missing `env_fingerprint` or 401 auth errors). Instead, require and invoke Evolver's built-in methods:
+> - **hello / heartbeat**: `sendHelloToHub()`, `sendHeartbeatToHub()` in `src/gep/a2aProtocol.js`
+> - **fetch / search**: `httpTransportReceive()` in `src/gep/a2aProtocol.js` or `hubSearch.js`
+> - **publish**: `publishEvolutionEvents()` in `src/gep/a2aProtocol.js` or `skillPublisher.js`
+> - **reviews**: `hubReview.js`
+> - **task / work (Bounty)**: `src/gep/taskReceiver.js`
+
 ### Shell Commands Used
 
 Evolver uses `child_process` for the following commands. No user-controlled input is passed to shell.
PATCH

echo "Gold patch applied."
