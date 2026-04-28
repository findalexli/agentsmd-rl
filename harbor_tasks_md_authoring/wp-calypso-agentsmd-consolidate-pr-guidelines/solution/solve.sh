#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wp-calypso

# Idempotency guard
if grep -qF ".claude/rules/pr.md" ".claude/rules/pr.md" && grep -qF "- Include all checklist items from .github/PULL_REQUEST_TEMPLATE.md. Only mark i" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/pr.md b/.claude/rules/pr.md
@@ -1,17 +0,0 @@
-# Creating Pull Requests
-
-Create PRs as draft. Follow the template in @.github/PULL_REQUEST_TEMPLATE.md.
-
-## Branch Naming
-
-Follow the branch naming conventions in @docs/git-workflow.md.
-
-## PR Description Guidelines
-
-- Use Linear issue IDs (e.g., `LIN-123`) instead of full Linear URLs
-- Avoid mentioning people's names in the PR description
-- Do not link to wordpress.com URLs
-
-## Pre-merge Checklist
-
-Include all checklist items from @.github/PULL_REQUEST_TEMPLATE.md. Only mark items as completed (`[x]`) if they actually apply; leave inapplicable items unchecked (`[ ]`).
diff --git a/AGENTS.md b/AGENTS.md
@@ -22,3 +22,13 @@
 - `yarn install`
 - `yarn start` to start the dev server.
 - `yarn start-dashboard` to start the dev server for the Dashboard client only.
+
+## Creating Pull Requests
+
+- Create PRs as draft. Follow the template in .github/PULL_REQUEST_TEMPLATE.md.
+- Follow the branch naming conventions in docs/git-workflow.md.
+- In the PR description:
+  - Use Linear issue IDs (e.g., `LIN-123`) instead of full Linear URLs.
+  - Avoid mentioning people's names.
+  - Do not link to wordpress.com URLs.
+  - Include all checklist items from .github/PULL_REQUEST_TEMPLATE.md. Only mark items as completed (`[x]`) if they actually apply; leave inapplicable items unchecked (`[ ]`).
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,5 +1 @@
 @AGENTS.md
-
-## Creating PRs
-
-Follow the rules in @.claude/rules/pr.md for the best practices in creating PRs.
PATCH

echo "Gold patch applied."
