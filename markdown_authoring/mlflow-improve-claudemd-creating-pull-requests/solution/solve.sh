#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mlflow

# Idempotency guard
if grep -qF "Follow [the PR template](./.github/pull_request_template.md) when creating pull " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -191,7 +191,7 @@ yarn --cwd mlflow/server/js check-all
 
 ### Creating Pull Requests
 
-Follow [the PR template](./.github/pull_request_template.md) when creating pull requests. The template will automatically appear when you create a PR on GitHub.
+Follow [the PR template](./.github/pull_request_template.md) when creating pull requests. Remove any unused checkboxes from the template to keep your PR clean and focused.
 
 ### Checking CI Status
 
PATCH

echo "Gold patch applied."
