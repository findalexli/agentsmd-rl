#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jentic-mini

# Idempotency guard
if grep -qF "See @AGENTS.md for the agent-facing runtime guide (search, inspect, execute work" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -6,6 +6,8 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 Jentic Mini is the open-source, self-hosted implementation of the Jentic API. It gives AI agents a local execution layer: search APIs via BM25, broker authenticated requests (credential injection without exposing secrets to the agent), enforce access policies, and observe execution traces. Built with FastAPI + SQLite + Fernet encryption.
 
+See @AGENTS.md for the agent-facing runtime guide (search, inspect, execute workflow; endpoint reference; credential-injection contract from the agent's perspective). Keep the overlapping sections in both files (Jentic Mini overview, credential-injection flow, capability ID format, `X-Jentic-API-Key` header) in sync when changing either.
+
 ## Development Setup
 
 See @DEVELOPMENT.md for prerequisites, installation, and running the server.
PATCH

echo "Gold patch applied."
