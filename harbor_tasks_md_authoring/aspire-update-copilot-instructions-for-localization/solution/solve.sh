#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aspire

# Idempotency guard
if grep -qF "* Files matching the pattern `*/localize/templatestrings.*.json` are localizatio" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -194,6 +194,8 @@ The `*.Designer.cs` files are in the repo, but are intended to match same named
 * Code blocks should be formatted with triple backticks (```) and include the language identifier for syntax highlighting.
 * JSON code blocks should be indented properly.
 
+## Localization files
+* Files matching the pattern `*/localize/templatestrings.*.json` are localization files. Do not translate their content. It is done by a dedicated workflow.
 ## Trust These Instructions
 
 These instructions are comprehensive and tested. Only search for additional information if:
PATCH

echo "Gold patch applied."
