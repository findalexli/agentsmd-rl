#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nanoclaw

# Idempotency guard
if grep -qF "Check that `config.hasCredentials` is `true` or `connection` is not null. The re" ".claude/skills/add-gmail/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/add-gmail/SKILL.md b/.claude/skills/add-gmail/SKILL.md
@@ -85,11 +85,27 @@ All tests must pass (including the new Gmail tests) and build must be clean befo
 ls -la ~/.gmail-mcp/ 2>/dev/null || echo "No Gmail config found"
 ```
 
-If `credentials.json` already exists, skip to "Build and restart" below.
+If `credentials.json` already exists with real tokens (not `onecli-managed` values), skip to "Build and restart" below.
 
 ### GCP Project Setup
 
-Tell the user:
+Check if OneCLI is configured:
+
+```bash
+grep -q 'ONECLI_URL=.' .env 2>/dev/null && echo "onecli" || echo "manual"
+```
+
+**If OneCLI:** Tell the user to open `${ONECLI_URL}/connections?connect=gmail` to set up their Gmail connection. The dashboard walks them through creating a Google Cloud OAuth app and authorizing it. Ask them to let you know when done.
+
+Once the user confirms, run:
+
+```bash
+onecli apps get --provider gmail
+```
+
+Check that `config.hasCredentials` is `true` or `connection` is not null. The response `hint` field has instructions and a docs URL for what stub credential files to create under `~/.gmail-mcp/`. Follow the hint — never overwrite existing files that don't contain `onecli-managed` values.
+
+**If manual:** Tell the user:
 
 > I need you to set up Google Cloud OAuth credentials:
 >
PATCH

echo "Gold patch applied."
