#!/usr/bin/env bash
set -euo pipefail

cd /workspace/chrome-devtools-mcp

# Idempotency guard
if grep -qF "All tools in `chrome-devtools-mcp` are annotated with `readOnlyHint: true` (for " "skills/troubleshooting/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/troubleshooting/SKILL.md b/skills/troubleshooting/SKILL.md
@@ -41,6 +41,12 @@ If the server starts successfully but `list_pages` returns an empty list or crea
 - **Check for flag typos:** For example, `--autoBronnect` instead of `--autoConnect`.
 - **Verify the configuration:** Ensure the arguments match the expected flags exactly.
 
+#### Symptom: Missing Tools / Only 9 tools available
+
+If the server starts successfully but only a limited subset of tools (like `list_pages`, `get_console_message`, `lighthouse_audit`, `take_memory_snapshot`) are available, this is likely because the MCP client is enforcing a **read-only mode**.
+
+All tools in `chrome-devtools-mcp` are annotated with `readOnlyHint: true` (for safe, non-modifying tools) or `readOnlyHint: false` (for tools that modify browser state, like `emulate`, `click`, `navigate_page`). To access the full suite of tools, the user must disable read-only mode in their MCP client (e.g., by exiting "Plan Mode" in Gemini CLI or adjusting their client's tool safety settings).
+
 #### Other Common Errors
 
 Identify other error messages from the failed tool call or the MCP initialization logs:
PATCH

echo "Gold patch applied."
