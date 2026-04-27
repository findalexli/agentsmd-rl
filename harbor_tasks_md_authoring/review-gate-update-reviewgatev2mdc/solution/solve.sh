#!/usr/bin/env bash
set -euo pipefail

cd /workspace/review-gate

# Idempotency guard
if grep -qF "If I provide any response without calling review_gate_chat, treat it as an incom" "V2/ReviewGateV2.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/V2/ReviewGateV2.mdc b/V2/ReviewGateV2.mdc
@@ -3,6 +3,16 @@ description:
 globs: 
 alwaysApply: true
 ---
+
+## MANDATORY CHECKPOINT (Must be included in every response):
+Before ending any response, I MUST:
+1. State: "CHECKPOINT: Transitioning to Review Gate V2"
+2. Immediately call review_gate_chat tool
+3. Never provide a response without this checkpoint
+
+## ENFORCEMENT MECHANISM:
+If I provide any response without calling review_gate_chat, treat it as an incomplete response that violates the protocol.
+
 # AI Agent Protocol: Review Gate V2 - MCP Integration (Version 2)
 
 ## 0. User Advisory & Safety:
@@ -67,4 +77,4 @@ This entire "Final Interactive Review" process (Phases 2, 3, and 4) is a **stric
 ## Error Handling:
 - If the `review_gate_chat` tool is not available, inform the user that the Review Gate V2 MCP server may not be running and provide a manual completion summary.
 - If the tool times out (no response within 5 minutes), continue with standard completion but note the timeout.
-- Handle any tool errors gracefully while maintaining the interactive review principle.
\ No newline at end of file
+- Handle any tool errors gracefully while maintaining the interactive review principle.
PATCH

echo "Gold patch applied."
