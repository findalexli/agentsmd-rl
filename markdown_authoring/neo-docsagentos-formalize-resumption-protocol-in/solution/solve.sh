#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "During continuous agent sessions, an agent can succumb to \"interruption amnesia." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -172,6 +172,13 @@ When you believe your codebase modifications are complete and ready for review,
 
 This skill governs branch generation, conventional commit standards, the critical "Stepping Back" reflection phase, and the state handoff endpoint sequence. Follow it exactly.
 
+## 8. The Resumption Protocol (Interruption Amnesia)
+
+During continuous agent sessions, an agent can succumb to "interruption amnesia." If the human commander injects a diagnostic sub-question or testing request (e.g., "test this A2A message" or "run this script") while the agent is midway through a ticket's lifecycle, the agent will typically resolve the sub-question and halt. It frequently drops the overarching "Definition of Done" (executing the `pull-request` skill) because its immediate context window was hijacked by the side-quest.
+
+**The Mandate:**
+If a user interrupts your ticket lifecycle for a diagnostic test, meta-request, or side-quest, you **MUST** explicitly resume the ticket lifecycle and check the PR Definition of Done immediately after the test concludes. Do not halt without asking yourself: *"Did the previous interruption distract me from opening the Pull Request?"*
+
 ## 9. Preventing Context Corruption (State Management)
 
 Working on the Neo platform requires long, complex sessions. To prevent your context window from becoming corrupted with multiple competing versions of the same file after several edits, you MUST adhere to this protocol:
PATCH

echo "Gold patch applied."
