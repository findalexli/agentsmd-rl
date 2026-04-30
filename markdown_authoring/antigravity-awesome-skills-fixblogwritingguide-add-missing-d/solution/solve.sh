#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "date_added: '2026-03-06'" "skills/blog-writing-guide/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/blog-writing-guide/SKILL.md b/skills/blog-writing-guide/SKILL.md
@@ -3,6 +3,7 @@ name: blog-writing-guide
 description: "This skill enforces Sentry's blog writing standards across every post — whether you're helping an engineer write their first blog post or a marketer draft a product announcement."
 risk: unknown
 source: community
+date_added: '2026-03-06'
 ---
 
 # Sentry Blog Writing Skill
PATCH

echo "Gold patch applied."
