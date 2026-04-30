#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai

# Idempotency guard
if grep -qF "- Prefer self::assert* over $this->assert* in tests" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -30,7 +30,7 @@ Each component has its own test suite. Run tests for specific components:
 # Platform component
 cd src/platform && vendor/bin/phpunit
 
-# Agent component  
+# Agent component
 cd src/agent && vendor/bin/phpunit
 
 # AI Bundle
@@ -111,10 +111,10 @@ Each component uses:
 - Do not use void return type for testcase methods
 - Always run PHP-CS-Fixer to ensure proper code style
 - Always add a newline at the end of the file
-- Prefer self::assert* oder $this->assert* in tests
+- Prefer self::assert* over $this->assert* in tests
 - Never add Claude as co-author in the commits
 - Add @author tags to newly introduced classes by the user
 - Prefer classic if statements over short-circuit evaluation when possible
 - Define array shapes for parameters and return types
 - Use project specific exceptions instead of global exception classes like \RuntimeException, \InvalidArgumentException etc.
-- NEVER mention Claude as co-author in commits
\ No newline at end of file
+- NEVER mention Claude as co-author in commits
PATCH

echo "Gold patch applied."
