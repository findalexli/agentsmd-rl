#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "**Always quote URLs** - shell interprets `?` and `&` as special characters." "skills/firecrawl-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/firecrawl-cli/SKILL.md b/skills/firecrawl-cli/SKILL.md
@@ -95,6 +95,8 @@ Organize into subdirectories when it makes sense for the task:
 .firecrawl/news/2024-01/
 ```
 
+**Always quote URLs** - shell interprets `?` and `&` as special characters.
+
 ## Commands
 
 ### Search - Web search with optional scraping
PATCH

echo "Gold patch applied."
