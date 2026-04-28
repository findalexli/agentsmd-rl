#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcpspy

# Idempotency guard
if grep -qF "Use the .worktrees/ directory to keep things organized in terms of permissions:" ".claude/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -140,3 +140,19 @@ HF_TOKEN=hf_xxx HF_MODEL=meta-llama/Llama-Prompt-Guard-2-86M make test-integrati
 - Integration tests use build tag `//go:build integration`
 - Default model is `protectai/deberta-v3-base-prompt-injection-v2` (non-gated)
 - Unit tests run without API calls via mock HTTP server
+
+## Git Worktrees for Parallel Claude Sessions
+
+Use worktrees to run multiple Claude sessions on separate feature branches.
+Use the .worktrees/ directory to keep things organized in terms of permissions:
+
+```bash
+# Create worktree with new branch
+git worktree add .worktrees/MCPSpy-<feature> -b feat/<feature-name>
+
+# Work in the new directory
+cd .worktrees/MCPSpy-<feature> && claude
+
+# Cleanup after merge
+git worktree remove .worktrees/MCPSpy-<feature>
+```
PATCH

echo "Gold patch applied."
