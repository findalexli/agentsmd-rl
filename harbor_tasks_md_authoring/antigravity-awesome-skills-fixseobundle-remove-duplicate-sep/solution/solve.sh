#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "skills/schema-markup/SKILL.md" "skills/schema-markup/SKILL.md" && grep -qF "skills/seo-fundamentals/SKILL.md" "skills/seo-fundamentals/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/schema-markup/SKILL.md b/skills/schema-markup/SKILL.md
@@ -6,8 +6,6 @@ source: community
 date_added: '2026-02-27'
 ---
 
----
-
 # Schema Markup & Structured Data
 
 You are an expert in **structured data and schema markup** with a focus on
diff --git a/skills/seo-fundamentals/SKILL.md b/skills/seo-fundamentals/SKILL.md
@@ -6,8 +6,6 @@ source: community
 date_added: '2026-02-27'
 ---
 
----
-
 # SEO Fundamentals
 
 > **Foundational principles for sustainable search visibility.**
PATCH

echo "Gold patch applied."
