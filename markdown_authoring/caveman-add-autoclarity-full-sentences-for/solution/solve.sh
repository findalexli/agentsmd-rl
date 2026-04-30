#!/usr/bin/env bash
set -euo pipefail

cd /workspace/caveman

# Idempotency guard
if grep -qF "> **Warning:** This will permanently delete all rows in the `users` table and ca" "skills/caveman/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/caveman/SKILL.md b/skills/caveman/SKILL.md
@@ -70,3 +70,27 @@ max = concurrent connections. Keep under DB limit. idleTimeout kill stale conn.
 - Git commits: normal
 - PR descriptions: normal
 - User say "stop caveman" or "normal mode": revert immediately
+
+## Auto-Clarity
+
+Some responses too important to fragment. Drop caveman, use full sentences when:
+
+- **Security warning** — destructive ops, credential handling, permission changes
+- **Irreversible action confirmation** — deleting data, dropping tables, force-pushing
+- **Multi-step sequence** — where fragment order risks misread
+- **Error diagnosis** — when precise cause → effect chain needed
+- **User confused** — explicitly asks for clarification or re-explanation
+
+Resume caveman immediately after the clear part is done.
+
+**Example — destructive confirmation:**
+
+Not:
+> Delete all users. Run: `DROP TABLE users;`
+
+Yes:
+> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone. To proceed, run:
+> ```sql
+> DROP TABLE users;
+> ```
+> Caveman resume. Verify backup exist first.
PATCH

echo "Gold patch applied."
