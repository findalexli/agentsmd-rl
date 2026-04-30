#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "- The monorepo structure allows independent versioning while maintaining shared " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -108,4 +108,7 @@ Each component uses:
 - Each component in `src/` is a separate Composer package with its own dependencies
 - Use `@dev` versions for internal component dependencies during development
 - Components follow Symfony coding standards and use `@Symfony` PHP CS Fixer rules
-- The monorepo structure allows independent versioning while maintaining shared development workflow
\ No newline at end of file
+- The monorepo structure allows independent versioning while maintaining shared development workflow
+- Do not use void return type for testcase methods
+- Always run PHP-CS-Fixer to ensure proper code style
+- Always add a newline at the end of the file
\ No newline at end of file
PATCH

echo "Gold patch applied."
