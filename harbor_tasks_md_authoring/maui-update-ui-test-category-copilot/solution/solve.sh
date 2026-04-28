#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotency guard
if grep -qF "- There should be only one `[Category]` attribute per test, pick the most approp" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -153,6 +153,7 @@ public class IssueXXXXX : _IssuesUITest
 - Compile both the HostApp project and TestCases.Shared.Tests project to ensure no build errors
 - Verify AutomationId references match between XAML and test code
 - Ensure tests follow the established naming and inheritance patterns
+- There should be only one `[Category]` attribute per test, pick the most appropriate one
 
 IMPORTANT NOTE: When a new UI test category is added to `UITestCategories.cs`, we need to also update the `ui-tests.yml` to include this new category. Make sure to detect this in your reviews.
 
PATCH

echo "Gold patch applied."
