#!/usr/bin/env bash
set -euo pipefail

cd /workspace/recce

# Idempotency guard
if grep -qF "**Commits:** Always use `--signoff` and include a `Co-Authored-By: Claude <norep" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -50,7 +50,7 @@ When asked to "publish ui" or "release ui package":
 
 ## Commit and PR Workflow
 
-**Commits:** Always use `--signoff` and include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
+**Commits:** Always use `--signoff` and include a `Co-Authored-By: Claude <noreply@anthropic.com>` trailer (version pin optional — if included, use the current model)
 
 **PRs:** Follow `.github/PULL_REQUEST_TEMPLATE.md`:
 - PR checklist (tests, DCO)
PATCH

echo "Gold patch applied."
