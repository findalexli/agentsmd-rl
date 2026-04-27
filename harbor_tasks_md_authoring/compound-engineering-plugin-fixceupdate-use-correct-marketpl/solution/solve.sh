#!/usr/bin/env bash
set -euo pipefail

cd /workspace/compound-engineering-plugin

# Idempotency guard
if grep -qF "!`gh release list --repo EveryInc/compound-engineering-plugin --limit 30 --json " "plugins/compound-engineering/skills/ce-update/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/compound-engineering/skills/ce-update/SKILL.md b/plugins/compound-engineering/skills/ce-update/SKILL.md
@@ -28,10 +28,10 @@ below handles those cases.
 !`echo "${CLAUDE_PLUGIN_ROOT}" 2>/dev/null || echo '__CE_UPDATE_ROOT_FAILED__'`
 
 **Latest released version:**
-!`gh release list --repo Everyinc/compound-engineering-plugin --limit 30 --json tagName --jq '[.[] | select(.tagName | startswith("compound-engineering-v"))][0].tagName | sub("compound-engineering-v";"")' 2>/dev/null || echo '__CE_UPDATE_VERSION_FAILED__'`
+!`gh release list --repo EveryInc/compound-engineering-plugin --limit 30 --json tagName --jq '[.[] | select(.tagName | startswith("compound-engineering-v"))][0].tagName | sub("compound-engineering-v";"")' 2>/dev/null || echo '__CE_UPDATE_VERSION_FAILED__'`
 
 **Cached version folder(s):**
-!`ls "${CLAUDE_PLUGIN_ROOT}/cache/every-marketplace/compound-engineering/" 2>/dev/null || echo '__CE_UPDATE_CACHE_FAILED__'`
+!`ls "${CLAUDE_PLUGIN_ROOT}/cache/compound-engineering-plugin/compound-engineering/" 2>/dev/null || echo '__CE_UPDATE_CACHE_FAILED__'`
 
 ## Decision logic
 
@@ -61,7 +61,7 @@ construct the delete path.
 
 **Clear the stale cache:**
 ```bash
-rm -rf "<plugin-root-path>/cache/every-marketplace/compound-engineering"
+rm -rf "<plugin-root-path>/cache/compound-engineering-plugin/compound-engineering"
 ```
 
 Tell the user:
PATCH

echo "Gold patch applied."
