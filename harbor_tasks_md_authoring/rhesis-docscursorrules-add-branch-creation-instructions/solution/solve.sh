#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rhesis

# Idempotency guard
if grep -qF "When creating a new branch, always branch from the latest `main` to avoid confli" ".cursor/rules/pull-requests.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/pull-requests.mdc b/.cursor/rules/pull-requests.mdc
@@ -32,6 +32,20 @@ Pull request creation should be based on the GitHub CLI (`gh`) and follow best p
 gh pr create --title "Your PR Title" --body "Your PR Description" --base main
 ```
 
+## Branch Creation
+
+When creating a new branch, always branch from the latest `main` to avoid conflicts:
+
+```bash
+# Ensure you have the latest main
+git fetch origin
+git checkout main
+git pull origin main
+
+# Create your feature branch
+git checkout -b feature/your-feature-name
+```
+
 ## PR Title Guidelines
 
 ### Format
PATCH

echo "Gold patch applied."
