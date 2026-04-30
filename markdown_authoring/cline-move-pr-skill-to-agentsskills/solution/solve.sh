#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cline

# Idempotency guard
if grep -qF "description: Create a GitHub pull request following project conventions. Use whe" ".agents/skills/create-pull-request/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/create-pull-request/SKILL.md b/.agents/skills/create-pull-request/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: create-pull-request
-description: Create a GitHub pull request following project conventions. Use when the user asks to create a PR, submit changes for review, or open a pull request. Handles commit analysis, branch management, and PR creation using the gh CLI tool.
+description: Create a GitHub pull request following project conventions. Use when the user asks to create a PR, submit changes for review, or open a pull request. Handles commit analysis, branch management, PR template usage, and PR creation using the gh CLI tool.
 ---
 
 # Create Pull Request
PATCH

echo "Gold patch applied."
