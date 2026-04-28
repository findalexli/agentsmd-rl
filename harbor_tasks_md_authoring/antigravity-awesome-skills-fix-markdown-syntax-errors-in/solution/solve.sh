#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "description: |" "skills/shopify-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/shopify-development/SKILL.md b/skills/shopify-development/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: shopify-development
-description: "|"
+description: |
   Build Shopify apps, extensions, themes using GraphQL Admin API, Shopify CLI, Polaris UI, and Liquid.
   TRIGGER: "shopify", "shopify app", "checkout extension", "admin extension", "POS extension",
   "shopify theme", "liquid template", "polaris", "shopify graphql", "shopify webhook",
PATCH

echo "Gold patch applied."
