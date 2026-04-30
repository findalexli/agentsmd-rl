#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "- Use project specific exceptions instead of global exception classes like \\Runt" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -111,4 +111,10 @@ Each component uses:
 - The monorepo structure allows independent versioning while maintaining shared development workflow
 - Do not use void return type for testcase methods
 - Always run PHP-CS-Fixer to ensure proper code style
-- Always add a newline at the end of the file
\ No newline at end of file
+- Always add a newline at the end of the file
+- Prefer self::assert* oder $this->assert* in tests
+- Never add Claude as co-author in the commits
+- Add @author tags to newly introduced classes by the user
+- Prefer classic if statements over short-circuit evaluation when possible
+- Define array shapes for parameters and return types
+- Use project specific exceptions instead of global exception classes like \RuntimeException, \InvalidArgumentException etc.
\ No newline at end of file
PATCH

echo "Gold patch applied."
