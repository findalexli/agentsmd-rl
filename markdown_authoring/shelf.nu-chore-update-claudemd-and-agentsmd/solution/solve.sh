#!/usr/bin/env bash
set -euo pipefail

cd /workspace/shelf.nu

# Idempotency guard
if grep -qF "- Always use Conventional Commits spec when making commits and opening PRs: http" "AGENTS.md" && grep -qF "- Always use Conventional Commits spec when making commits and opening PRs: http" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -48,6 +48,7 @@ This repository hosts **Shelf.nu**, an asset management platform built with Remi
 ## Git Practices
 
 - Commit after completing a coherent task using descriptive messages.
+- Always use Conventional Commits spec when making commits and opening PRs: https://www.conventionalcommits.org/en/v1.0.0/
 - Do **not** add "🤖 Generated with Claude Code" or similar co-authored trailers to commits.
 - Ensure the working tree is clean and applicable checks (including `npm run validate` for code changes) pass before requesting review.
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -148,7 +148,8 @@ Always run `npm run validate` before committing - this runs:
 
 ## Git and Version control
 
-- add and commit automatically whenever a task is finished\
+- add and commit automatically whenever a task is finished
+- Always use Conventional Commits spec when making commits and opening PRs: https://www.conventionalcommits.org/en/v1.0.0/
 - use descriptive commit messages that capture the full scope of the changes
 - dont add 🤖 Generated with [Claude Code](https://claude.ai code) & Co-Authored-By: Claude <noreply@anthropic.com>" because it clutters the commits
 
PATCH

echo "Gold patch applied."
