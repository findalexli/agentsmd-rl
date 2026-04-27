#!/usr/bin/env bash
set -euo pipefail

cd /workspace/context-engineering-kit

# Idempotency guard
if grep -qF "Check whether codemap is installed by running `codemap -help`." "plugins/mcp/skills/setup-codemap-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/mcp/skills/setup-codemap-cli/SKILL.md b/plugins/mcp/skills/setup-codemap-cli/SKILL.md
@@ -35,7 +35,7 @@ Store the user's choice and use the appropriate paths in subsequent steps.
 
 ## 2. Check if Codemap is already installed
 
-Check whether codemap is installed by running `codemap --version` or `codemap --help`.
+Check whether codemap is installed by running `codemap -help`.
 
 If not installed, proceed with setup.
 
@@ -65,7 +65,6 @@ scoop install codemap
 After installation, verify codemap works:
 
 ```bash
-codemap --version
 codemap .
 ```
 
@@ -241,4 +240,4 @@ codemap --diff
     ]
   }
 }
-```
\ No newline at end of file
+```
PATCH

echo "Gold patch applied."
