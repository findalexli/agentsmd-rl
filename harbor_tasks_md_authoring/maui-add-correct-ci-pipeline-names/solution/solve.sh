#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotency guard
if grep -qF "**\u26a0\ufe0f Old pipeline names** (e.g., `MAUI-UITests-public`, `MAUI-public`) are **out" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -90,6 +90,18 @@ Major test projects:
 
 Find all tests: `find . -name "*.UnitTests.csproj"`
 
+### CI Pipelines (Azure DevOps)
+
+When referencing or triggering CI pipelines, use these current pipeline names:
+
+| Pipeline | Name | Purpose |
+|----------|------|---------|
+| Overall CI | `maui-pr` | Full PR validation build |
+| Device Tests | `maui-pr-devicetests` | Helix-based device tests |
+| UI Tests | `maui-pr-uitests` | Appium-based UI tests |
+
+**⚠️ Old pipeline names** (e.g., `MAUI-UITests-public`, `MAUI-public`) are **outdated** and should NOT be used. Always use the names above.
+
 ### Code Formatting
 
 Always format code before committing:
PATCH

echo "Gold patch applied."
