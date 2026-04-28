#!/usr/bin/env bash
set -euo pipefail

cd /workspace/scriptcat

# Idempotency guard
if grep -qF "- The user interface supports multiple languages, with English set as the defaul" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -139,3 +139,8 @@ pnpm run coverage      # Generate coverage reports
 - Tests co-located with source files (`.test.ts` suffix)
 - Template files use `.tpl` extension for build-time processing
 - Configuration files use factory pattern for environment-specific setup
+
+## Language
+- The code is developed and maintained by developers based in Mainland China.
+- Comments should preferably be written in Simplified Chinese.
+- The user interface supports multiple languages, with English set as the default for global users.
PATCH

echo "Gold patch applied."
