#!/usr/bin/env bash
set -euo pipefail

cd /workspace/parcels

# Idempotency guard
if grep -qF "- **NEVER impersonate the user on GitHub**, always sign off with something like" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,10 @@
+## GitHub Interaction Guidelines
+
+- **NEVER impersonate the user on GitHub**, always sign off with something like
+  "[This is Claude Code on behalf of Jane Doe]"
+- Never create issues nor pull requests on the GitHub repository unless
+  explicitly instructed
+- Never post "update" messages, progress reports, or explanatory comments on
+  GitHub issues/PRs unless specifically instructed
+- When creating commits, always include a co-authorship trailer:
+  `Co-authored-by: Claude <noreply@anthropic.com>`
PATCH

echo "Gold patch applied."
