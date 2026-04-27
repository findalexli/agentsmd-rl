#!/usr/bin/env bash
set -euo pipefail

cd /workspace/awesome-copilot

# Idempotency guard
if grep -qF "author_url: 'https://github.com/utkarsh232005'" "skills/gsap-framer-scroll-animation/SKILL.md" && grep -qF "author_url: 'https://github.com/utkarsh232005'" "skills/premium-frontend-ui/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/gsap-framer-scroll-animation/SKILL.md b/skills/gsap-framer-scroll-animation/SKILL.md
@@ -11,6 +11,9 @@ description: >-
   "parallax effect", "sticky section", "scroll progress bar", or "entrance animation".
   Also triggers for Copilot prompt patterns for GSAP or Framer Motion code generation.
   Pairs with the premium-frontend-ui skill for creative philosophy and design-level polish.
+metadata:
+  author: 'Utkarsh Patrikar'
+  author_url: 'https://github.com/utkarsh232005'
 ---
 
 # GSAP & Framer Motion — Scroll Animations Skill
@@ -145,3 +148,4 @@ tl.from('.title', { opacity: 0, y: 60 }).from('.img', { scale: 0.85 });
 | Skill | Relationship |
 |---|---|
 | **premium-frontend-ui** | Creative philosophy, design principles, and aesthetic guidelines — defines *when* and *why* to animate |
+
diff --git a/skills/premium-frontend-ui/SKILL.md b/skills/premium-frontend-ui/SKILL.md
@@ -1,6 +1,9 @@
 ---
 name: premium-frontend-ui
 description: 'A comprehensive guide for GitHub Copilot to craft immersive, high-performance web experiences with advanced motion, typography, and architectural craftsmanship.'
+metadata:
+  author: 'Utkarsh Patrikar'
+  author_url: 'https://github.com/utkarsh232005'
 ---
 
 # Immersive Frontend UI Craftsmanship
PATCH

echo "Gold patch applied."
