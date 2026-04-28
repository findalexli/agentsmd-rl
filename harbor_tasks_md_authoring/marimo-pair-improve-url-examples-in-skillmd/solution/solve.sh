#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marimo-pair

# Idempotency guard
if grep -qF "| Execute code (by URL) | `bash scripts/execute-code.sh --url http://localhost:2" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -57,20 +57,17 @@ Two operations: **discover servers** and **execute code**.
 | Discover servers | `bash scripts/discover-servers.sh` | `list_sessions()` tool |
 | Execute code | `bash scripts/execute-code.sh -c "code"` | `execute_code(code=..., session_id=...)` tool |
 | Execute code (multiline) | `bash scripts/execute-code.sh <<'EOF'` | same |
-| Execute code (direct URL) | `bash scripts/execute-code.sh --url URL -c "code"` | same (with `url` param) |
-
-Scripts auto-discover sessions from the registry on disk. Use `--port` to
-target a specific server when multiple are running, `--session` to target a
-specific session when multiple notebooks are open on the same server, or
-`--url` to skip discovery entirely and hit a server URL directly (e.g.
-`--url http://localhost:2718`). `--url` is the only way to connect to
-remote servers since auto-discovery only reads the local registry. **Only
-use `--url` with trusted servers** — data is sent to the endpoint, so a
-malicious URL could exfiltrate notebook contents. Set the `MARIMO_TOKEN`
-env var to authenticate when the server has token auth enabled (`--token`
-flag also works but exposes the token in process listings). If the
-server was started with `--mcp`, you'll have MCP tools available as an
-alternative.
+| Execute code (by URL) | `bash scripts/execute-code.sh --url http://localhost:2718 -c "code"` | same (with `url` param) |
+
+Scripts auto-discover sessions from the local server registry. Use
+`--port` to target a specific server when multiple are running,
+`--session` to target a specific session when multiple notebooks are
+open on the same server, or `--url` to skip discovery and connect to a
+server by URL (e.g. `--url http://localhost:2718`). Set the
+`MARIMO_TOKEN` env var to authenticate when the server has token auth
+enabled (`--token` flag also works but exposes the token in process
+listings). If the server was started with `--mcp`, you'll have MCP tools
+available as an alternative.
 
 ### Discovery finds nothing but the user has a server running?
 
@@ -108,8 +105,8 @@ EOF
 # file
 bash scripts/execute-code.sh /tmp/code.py
 
-# direct URL (skips auto-discovery and works with remote servers)
-bash scripts/execute-code.sh --url http://localhost:2718 -c "1 + 1"
+# target a specific port (skips auto-selection when multiple servers run)
+bash scripts/execute-code.sh --port 2718 -c "1 + 1"
 ```
 
 ## Executing Code
PATCH

echo "Gold patch applied."
