#!/usr/bin/env bash
set -euo pipefail

cd /workspace/liam

# Idempotency guard
if grep -qF "- **Let the code speak** \u2013 If you need a multi-paragraph comment, refactor until" "CLAUDE.md" && grep -qF "This file provides guidance to Claude Code (claude.ai/code) when working with da" "frontend/internal-packages/db/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -13,7 +13,7 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ### App-specific Commands
 
-````bash
+```bash
 # Run only the main web app (port 3001)
 pnpm --filter @liam-hq/app dev
 
@@ -22,10 +22,7 @@ pnpm --filter @liam-hq/agent fmt
 
 # Test
 pnpm --filter @liam-hq/agent test
-
-### Database Operations
-
-For database migration and type generation workflows, see @docs/migrationOpsContext.md.
+```
 
 ## Architecture
 
@@ -53,11 +50,13 @@ For database migration and type generation workflows, see @docs/migrationOpsCont
 
 Keep every implementation as small and obvious as possible.
 
+- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious
+- **Delete fearlessly, Git remembers** – Cut dead code, stale logic, and verbose history
+
 ### TypeScript Standards
 
 - Use runtime type validation with `valibot` for external data validation
 - Use early returns for readability
-- **Let the code speak** – If you need a multi-paragraph comment, refactor until intent is obvious
 
 ### Code Editing
 
@@ -75,7 +74,7 @@ function saveUser(data: UserData, userId?: string) {
 function saveUser(data: UserData, userId: string) {
   return db.save(userId, data); // Simple and clear
 }
-````
+```
 
 ### Component Patterns
 
diff --git a/frontend/internal-packages/db/CLAUDE.md b/frontend/internal-packages/db/CLAUDE.md
@@ -0,0 +1,7 @@
+# CLAUDE.md - Database Package
+
+This file provides guidance to Claude Code (claude.ai/code) when working with database operations.
+
+## Database Operations
+
+For database migration and type generation workflows, see @../../../docs/migrationOpsContext.md
PATCH

echo "Gold patch applied."
