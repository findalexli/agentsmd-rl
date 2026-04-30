#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cultivation-world-simulator

# Idempotency guard
if grep -qF "For bug fixes, ensure the test would have **failed before the fix** and **passes" ".claude/skills/test-validate/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/test-validate/SKILL.md b/.claude/skills/test-validate/SKILL.md
@@ -18,3 +18,16 @@ description: Run Python tests using the project venv
 # Run server (dev mode)
 .venv/bin/python src/server/main.py --dev
 ```
+
+## Test Coverage Guidelines
+
+After making code changes, consider whether tests are needed:
+
+| Change Type | Test Recommendation |
+|-------------|---------------------|
+| Bug fix | Add regression test to prevent recurrence |
+| New feature | Unit tests + integration test if affects multiple modules |
+| Refactor | Existing tests should pass; add tests if behavior changes |
+| Config/docs | Usually no tests needed |
+
+For bug fixes, ensure the test would have **failed before the fix** and **passes after**.
PATCH

echo "Gold patch applied."
