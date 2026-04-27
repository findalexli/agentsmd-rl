#!/usr/bin/env bash
set -euo pipefail

cd /workspace/activepieces

# Idempotency guard
if grep -qF "- If the PR includes any contributions to pieces (integrations under `packages/p" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -38,6 +38,14 @@
 
 - Always prefix `git push` with `CLAUDE_PUSH=yes` to auto-approve the pre-push lint/test gate, e.g. `CLAUDE_PUSH=yes git push -u origin HEAD`.
 
+## Pull Requests
+
+- When creating a PR with `gh pr create`, always apply exactly one of these labels based on the nature of the change:
+  - **`feature`** — new functionality
+  - **`bug`** — bug fix
+  - **`skip-changelog`** — changes that should not appear in the changelog (docs, CI tweaks, internal refactors, etc.)
+- If the PR includes any contributions to pieces (integrations under `packages/pieces`), also add the **`pieces`** label (in addition to the primary label above).
+
 ## Database Migrations
 
 - Before creating or modifying a database migration, **always read the [Database Migrations Playbook](https://www.activepieces.com/docs/handbook/engineering/playbooks/database-migration#database-migrations)** first. Follow its instructions for generating and structuring migrations.
PATCH

echo "Gold patch applied."
