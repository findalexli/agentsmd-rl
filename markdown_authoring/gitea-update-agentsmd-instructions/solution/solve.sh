#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gitea

# Idempotency guard
if grep -qF "- Always start issue and pull request comments with an authorship attribution" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,3 +6,5 @@
 - Before committing `go.mod` changes, run `make tidy`
 - Before committing new `.go` files, add the current year into the copyright header
 - Before committing any files, remove all trailing whitespace from source code lines
+- Never force-push to pull request branches
+- Always start issue and pull request comments with an authorship attribution
PATCH

echo "Gold patch applied."
