#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotency guard
if grep -qF "IMPORTANT NOTE: When a new UI test category is added to `UITestCategories.cs`, w" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -154,6 +154,8 @@ public class IssueXXXXX : _IssuesUITest
 - Verify AutomationId references match between XAML and test code
 - Ensure tests follow the established naming and inheritance patterns
 
+IMPORTANT NOTE: When a new UI test category is added to `UITestCategories.cs`, we need to also update the `ui-tests.yml` to include this new category. Make sure to detect this in your reviews.
+
 ### Code Formatting
 
 Before committing any changes, format the codebase using the following command to ensure consistent code style:
PATCH

echo "Gold patch applied."
