#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bashkit

# Idempotency guard
if grep -qF "- When asked to create separate PRs, follow that instruction\u2014do not bundle unrel" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -130,4 +130,7 @@ Squash and Merge. Use PR template if exists.
 
 **NEVER add links to Claude sessions in PR body.**
 
+- Prefer small, shippable PRs. Split large changes into independent, reviewable units.
+- When asked to create separate PRs, follow that instruction—do not bundle unrelated changes.
+
 See `CONTRIBUTING.md` for details.
PATCH

echo "Gold patch applied."
