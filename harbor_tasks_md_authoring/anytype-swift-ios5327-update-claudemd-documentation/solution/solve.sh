#!/usr/bin/env bash
set -euo pipefail

cd /workspace/anytype-swift

# Idempotency guard
if grep -qF "- **Remove unused code after refactoring** - Delete unused properties, functions" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -50,6 +50,7 @@ make setup-middle    # Initial setup
 - **All user-facing text must be localized** for international support
 - **Do not add comments** unless explicitly requested
 - **We only work in feature branches** - never push directly to develop/main
+- **Remove unused code after refactoring** - Delete unused properties, functions, and entire files that are no longer referenced
 
 ## 📝 Localization System
 
@@ -207,6 +208,23 @@ Modules/                # Swift packages
 - [ ] Single line commit message only
 - [ ] Professional message without AI attribution
 
+### Task-Based Branching
+**⚠️ CRITICAL: This is the FIRST thing to do when starting any task**
+
+When receiving a Linear task ID (e.g., `IOS-5292`):
+1. **Identify the task branch**: The branch name follows the format `ios-XXXX-description`
+   - Example: `ios-5292-update-space-hub-loading-state`
+   - You can retrieve the branch name from Linear issue details
+
+2. **Switch to the task branch IMMEDIATELY** before doing ANY other work:
+   ```bash
+   git checkout ios-5292-update-space-hub-loading-state
+   ```
+
+3. **All work for the task must be done in this dedicated branch**
+   - Never work on tasks in the wrong branch
+   - Verify you're on the correct branch: `git branch --show-current`
+
 ### Git & GitHub
 - **Main branch**: `develop`
 - **Feature branches**: `ios-XXXX-description`
PATCH

echo "Gold patch applied."
