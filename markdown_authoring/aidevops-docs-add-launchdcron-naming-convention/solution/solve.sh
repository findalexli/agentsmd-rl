#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aidevops

# Idempotency guard
if grep -qF "When creating launchd plists or cron jobs, use the `aidevops` prefix so they're " ".agents/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/AGENTS.md b/.agents/AGENTS.md
@@ -213,4 +213,11 @@ Tree: `prompts/build.txt`. Agent tiers:
 
 Lifecycle: `tools/build-agent/build-agent.md`.
 
+## Scheduled Tasks (launchd/cron)
+
+When creating launchd plists or cron jobs, use the `aidevops` prefix so they're easy to find in System Settings > General > Login Items & Extensions:
+- **launchd label**: `sh.aidevops.<name>` (reverse domain, e.g., `sh.aidevops.session-miner-pulse`)
+- **plist filename**: `sh.aidevops.<name>.plist`
+- **cron comment**: `# aidevops: <description>`
+
 <!-- AI-CONTEXT-END -->
PATCH

echo "Gold patch applied."
