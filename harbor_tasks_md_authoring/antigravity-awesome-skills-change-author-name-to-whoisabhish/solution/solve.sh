#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "author: Whoisabhishekadhikari" "skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md b/skills/wordpress-centric-high-seo-optimized-blogwriting-skill/SKILL.md
@@ -2,7 +2,7 @@
 name: wordpress-centric-high-seo-optimized-blogwriting-skill
 description: "Use this skill when the user asks to write a blog post, article, or SEO content. This applies a professional structure, truth boxes, click-bait-free accurate information, and outputs direct WordPress-ready content."
 version: 1.0.0
-author: user
+author: Whoisabhishekadhikari
 created: 2026-04-12
 category: content
 tags: [writing, blog, seo, content, wordpress]
PATCH

echo "Gold patch applied."
