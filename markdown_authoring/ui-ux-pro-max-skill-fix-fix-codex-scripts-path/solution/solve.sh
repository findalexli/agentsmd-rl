#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ui-ux-pro-max-skill

# Idempotency guard
if grep -qF "python3 .codex/skills/ui-ux-pro-max/scripts/search.py \"<keyword>\" --domain <doma" ".codex/skills/ui-ux-pro-max/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.codex/skills/ui-ux-pro-max/SKILL.md b/.codex/skills/ui-ux-pro-max/SKILL.md
@@ -51,7 +51,7 @@ Extract key information from user request:
 Use `search.py` multiple times to gather comprehensive information. Search until you have enough context.
 
 ```bash
-python3 .codex/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
 ```
 
 **Recommended search order:**
@@ -70,7 +70,7 @@ python3 .codex/scripts/search.py "<keyword>" --domain <domain> [-n <max_results>
 If user doesn't specify a stack, **default to `html-tailwind`**.
 
 ```bash
-python3 .codex/scripts/search.py "<keyword>" --stack html-tailwind
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "<keyword>" --stack html-tailwind
 ```
 
 Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`
@@ -116,26 +116,26 @@ Available stacks: `html-tailwind`, `react`, `nextjs`, `vue`, `svelte`, `swiftui`
 
 ```bash
 # 1. Search product type
-python3 .codex/scripts/search.py "beauty spa wellness service" --domain product
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness service" --domain product
 
 # 2. Search style (based on industry: beauty, elegant)
-python3 .codex/scripts/search.py "elegant minimal soft" --domain style
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "elegant minimal soft" --domain style
 
 # 3. Search typography
-python3 .codex/scripts/search.py "elegant luxury" --domain typography
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "elegant luxury" --domain typography
 
 # 4. Search color palette
-python3 .codex/scripts/search.py "beauty spa wellness" --domain color
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "beauty spa wellness" --domain color
 
 # 5. Search landing page structure
-python3 .codex/scripts/search.py "hero-centric social-proof" --domain landing
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "hero-centric social-proof" --domain landing
 
 # 6. Search UX guidelines
-python3 .codex/scripts/search.py "animation" --domain ux
-python3 .codex/scripts/search.py "accessibility" --domain ux
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "animation" --domain ux
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "accessibility" --domain ux
 
 # 7. Search stack guidelines (default: html-tailwind)
-python3 .codex/scripts/search.py "layout responsive" --stack html-tailwind
+python3 .codex/skills/ui-ux-pro-max/scripts/search.py "layout responsive" --stack html-tailwind
 ```
 
 **Then:** Synthesize all search results and implement the design.
PATCH

echo "Gold patch applied."
