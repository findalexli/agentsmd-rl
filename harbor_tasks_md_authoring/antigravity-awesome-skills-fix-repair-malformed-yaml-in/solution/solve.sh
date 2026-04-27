#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "description: 'Draft cold emails, follow-ups, and proposal templates. Creates pri" "skills/sales-automator/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/sales-automator/SKILL.md b/skills/sales-automator/SKILL.md
@@ -1,12 +1,6 @@
 ---
 name: sales-automator
-description: 'Draft cold emails, follow-ups, and proposal templates. Creates
-
-  pricing pages, case studies, and sales scripts. Use PROACTIVELY for sales
-
-  outreach or lead nurturing.
-
-  '
+description: 'Draft cold emails, follow-ups, and proposal templates. Creates pricing pages, case studies, and sales scripts. Use PROACTIVELY for sales outreach or lead nurturing. '
 risk: unknown
 source: community
 date_added: '2026-02-27'
PATCH

echo "Gold patch applied."
