#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xarray

# Idempotency guard
if grep -qF "- When creating commits, always include a co-authorship trailer:" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -28,3 +28,5 @@ uv run dmypy run  # Type checking with mypy
   explicitly instructed
 - Never post "update" messages, progress reports, or explanatory comments on
   GitHub issues/PRs unless specifically instructed
+- When creating commits, always include a co-authorship trailer:
+  `Co-authored-by: Claude <claude@anthropic.com>`
PATCH

echo "Gold patch applied."
