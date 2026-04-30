#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ouroboros

# Idempotency guard
if grep -qF "1. Run `claude plugin marketplace update ouroboros` via Bash (refresh marketplac" "skills/interview/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/interview/SKILL.md b/skills/interview/SKILL.md
@@ -45,13 +45,14 @@ Compare the result with the current version in `.claude-plugin/plugin.json`.
   }
   ```
   - If "Update now":
-    1. Run `claude plugin update ouroboros` via Bash (update plugin/skills). If this fails, inform the user and stop — do NOT proceed to step 2.
-    2. Detect the user's Python package manager and upgrade the MCP server:
+    1. Run `claude plugin marketplace update ouroboros` via Bash (refresh marketplace index). If this fails, tell the user "⚠️ Marketplace refresh failed, continuing…" and proceed.
+    2. Run `claude plugin update ouroboros@ouroboros` via Bash (update plugin/skills). If this fails, inform the user and stop — do NOT proceed to step 3.
+    3. Detect the user's Python package manager and upgrade the MCP server:
        - Check which tool installed `ouroboros-ai` by running these in order:
          - `uv tool list 2>/dev/null | grep "^ouroboros-ai "` → if found, use `uv tool upgrade ouroboros-ai`
          - `pipx list 2>/dev/null | grep "^  ouroboros-ai "` → if found, use `pipx upgrade ouroboros-ai`
          - Otherwise, print: "Also upgrade the MCP server: `pip install --upgrade ouroboros-ai`" (do NOT run pip automatically)
-    3. Tell the user: "Updated! Restart Claude Code to apply, then run `ooo interview` again."
+    4. Tell the user: "Updated! Restart Claude Code to apply, then run `ooo interview` again."
   - If "Skip": proceed immediately.
 - If versions match, the check fails (network error, timeout, rate limit 403/429), or parsing fails/returns empty: **silently skip** and proceed.
 
PATCH

echo "Gold patch applied."
