#!/usr/bin/env bash
set -euo pipefail

cd /workspace/linkedin-mcp-server

# Idempotency guard
if grep -qF "Always verify scraping bugs end-to-end against live LinkedIn, not just code anal" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -129,6 +129,31 @@ All scraping tools return: `{url, sections: {name: raw_text}}`. When unknown sec
 - Types: feat, fix, docs, style, refactor, test, chore, perf, ci
 - Keep subject <50 chars, imperative mood
 
+## Verifying Bug Reports
+
+Always verify scraping bugs end-to-end against live LinkedIn, not just code analysis. Assume a valid login profile already exists at `~/.linkedin-mcp/profile/`. Start the server with HTTP transport in one terminal (this process is long-running and will block the shell), then in a second terminal call the tool via curl:
+
+```bash
+# Start server
+uv run -m linkedin_mcp_server --transport streamable-http --log-level DEBUG
+
+# Initialize MCP session (grab Mcp-Session-Id from response headers)
+curl -s -D /tmp/mcp-headers -X POST http://127.0.0.1:8000/mcp \
+  -H "Content-Type: application/json" \
+  -H "Accept: application/json, text/event-stream" \
+  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
+
+# Extract the session ID from saved headers
+SESSION_ID=$(grep -i 'Mcp-Session-Id' /tmp/mcp-headers | awk '{print $2}' | tr -d '\r')
+
+# Call a tool (use Mcp-Session-Id from previous response)
+curl -s -X POST http://127.0.0.1:8000/mcp \
+  -H "Content-Type: application/json" \
+  -H "Accept: application/json, text/event-stream" \
+  -H "Mcp-Session-Id: $SESSION_ID" \
+  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"get_person_profile","arguments":{"linkedin_username":"williamhgates","sections":"posts"}}}'
+```
+
 ## Important Development Notes
 
 ### Development Workflow
PATCH

echo "Gold patch applied."
