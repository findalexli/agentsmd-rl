#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotency guard
if grep -qF "Do not flag issues that are caught by our automated CI/CD pipeline (linting, tes" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -0,0 +1,16 @@
+# Code Review Instructions
+
+## Priority
+Only comment on issues that affect correctness, security, or performance.
+Do NOT comment on: style preferences, minor naming conventions, formatting, or
+issues already enforced by our linter/CI pipeline.
+
+## Confidence threshold
+Only leave a comment when you have HIGH CONFIDENCE (>80%) that a real problem exists.
+Do not flag potential issues speculatively.
+
+## Severity filter
+Skip LOW severity issues entirely. Focus on HIGH and CRITICAL issues only.
+
+## CI context
+Do not flag issues that are caught by our automated CI/CD pipeline (linting, tests, type checks).
PATCH

echo "Gold patch applied."
