#!/usr/bin/env bash
set -euo pipefail

cd /workspace/kilo

# Idempotency guard
if grep -qF "- You may be running in a git worktree. All changes must be made in your current" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,6 +6,7 @@ Kilo CLI is an open source AI coding agent that generates code from natural lang
 - The default branch in this repo is `dev`.
 - Local `main` ref may not exist; use `dev` or `origin/dev` for diffs.
 - Prefer automation: execute requested actions without confirmation unless blocked by missing info or safety/irreversibility.
+- You may be running in a git worktree. All changes must be made in your current working directory — never modify files in the main repo checkout.
 
 ## Build and Dev
 
PATCH

echo "Gold patch applied."
