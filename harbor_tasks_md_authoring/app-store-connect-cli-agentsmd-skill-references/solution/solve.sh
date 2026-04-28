#!/usr/bin/env bash
set -euo pipefail

cd /workspace/app-store-connect-cli

# Idempotency guard
if grep -qF ".agent/skills/asc-cli-usage/SKILL.md" ".agent/skills/asc-cli-usage/SKILL.md" && grep -qF "## References" "Agents.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agent/skills/asc-cli-usage/SKILL.md b/.agent/skills/asc-cli-usage/SKILL.md
@@ -31,10 +31,3 @@ Use this skill when you need to run or design `asc` commands for App Store Conne
 ## Timeouts
 - `ASC_TIMEOUT` / `ASC_TIMEOUT_SECONDS` control request timeouts.
 - `ASC_UPLOAD_TIMEOUT` / `ASC_UPLOAD_TIMEOUT_SECONDS` control upload timeouts.
-
-## References
-- `AGENTS.md`
-- `docs/TESTING.md`
-- `docs/GO_STANDARDS.md`
-- `docs/API_NOTES.md`
-- `CONTRIBUTING.md`
diff --git a/Agents.md b/Agents.md
@@ -52,7 +52,7 @@ API keys are generated at https://appstoreconnect.apple.com/access/integrations/
 | `ASC_UPLOAD_TIMEOUT` | Upload timeout (e.g., `60s`, `2m`) |
 | `ASC_UPLOAD_TIMEOUT_SECONDS` | Upload timeout in seconds (alternative) |
 
-## Further Reading
+## References
 
 Detailed guidance on specific topics (only read when needed):
 
PATCH

echo "Gold patch applied."
