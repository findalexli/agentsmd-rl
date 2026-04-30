#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cli

# Idempotency guard
if grep -qF "Before pushing commits or otherwise sending code changes to any remote, run `mis" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -164,6 +164,10 @@ mise run test:ci  # Run all tests (unit + integration)
 
 Safety note: do not treat a clean `mise run lint` result as final unless it was run after the most recent `mise run fmt` pass.
 
+### Before Any Push Or Remote Code Update (REQUIRED)
+
+Before pushing commits or otherwise sending code changes to any remote, run `mise run lint` on the current tree and ensure it passes. If `mise run fmt` changed files, rerun `mise run lint` on the formatted tree before pushing.
+
 **Common CI failures from skipping this:**
 
 - `gofmt` formatting differences → run `mise run fmt`
PATCH

echo "Gold patch applied."
