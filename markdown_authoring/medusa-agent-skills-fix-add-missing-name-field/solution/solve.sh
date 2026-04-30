#!/usr/bin/env bash
set -euo pipefail

cd /workspace/medusa-agent-skills

# Idempotency guard
if grep -qF "name: db-generate" "plugins/medusa-dev/skills/db-generate/SKILL.md" && grep -qF "name: db-migrate" "plugins/medusa-dev/skills/db-migrate/SKILL.md" && grep -qF "name: new-user" "plugins/medusa-dev/skills/new-user/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/medusa-dev/skills/db-generate/SKILL.md b/plugins/medusa-dev/skills/db-generate/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: db-generate
 description: Generate database migrations for a Medusa module
 argument-hint: <module-name>
 allowed-tools: Bash(npx medusa db:generate:*)
diff --git a/plugins/medusa-dev/skills/db-migrate/SKILL.md b/plugins/medusa-dev/skills/db-migrate/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: db-migrate
 description: Run database migrations in Medusa
 allowed-tools: Bash(npx medusa db:migrate:*)
 ---
diff --git a/plugins/medusa-dev/skills/new-user/SKILL.md b/plugins/medusa-dev/skills/new-user/SKILL.md
@@ -1,4 +1,5 @@
 ---
+name: new-user
 description: Create an admin user in Medusa
 argument-hint: <email> <password>
 allowed-tools: Bash(npx medusa user:*)
PATCH

echo "Gold patch applied."
