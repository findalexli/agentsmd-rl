#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "- No brand name placement (SERPs include brand name above title already)" "skills/seo-audit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/seo-audit/SKILL.md b/skills/seo-audit/SKILL.md
@@ -164,7 +164,7 @@ Reporting "no schema found" based solely on `web_fetch` or `curl` leads to false
 - Primary keyword near beginning
 - 50-60 characters (visible in SERP)
 - Compelling and click-worthy
-- Brand name placement (end, usually)
+- No brand name placement (SERPs include brand name above title already)
 
 **Common issues:**
 - Duplicate titles
PATCH

echo "Gold patch applied."
