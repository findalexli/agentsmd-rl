#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cc-wf-studio

# Idempotency guard
if grep -qF "npm run check   # Run all Biome checks (lint + format, with auto-fix)" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -79,9 +79,7 @@ fix: add missing MCP node definition to workflow schema
 **Always run these commands in the following order after code modifications:**
 
 ```bash
-npm run format  # Auto-format code with Biome
-npm run lint    # Check for linting issues
-npm run check   # Run all Biome checks (lint + format verification)
+npm run check   # Run all Biome checks (lint + format, with auto-fix)
 npm run build   # Build extension and webview (verify compilation)
 ```
 
@@ -90,11 +88,9 @@ npm run build   # Build extension and webview (verify compilation)
 #### During Development
 1. **After code modification**:
    ```bash
-   npm run format && npm run lint && npm run check
+   npm run check
    ```
-   - Fixes formatting issues automatically
-   - Identifies linting problems
-   - Verifies code quality standards
+   - Runs lint + format with auto-fix in a single command
 
 2. **Before manual E2E testing**:
    ```bash
@@ -105,7 +101,7 @@ npm run build   # Build extension and webview (verify compilation)
 
 3. **Before git commit**:
    ```bash
-   npm run format && npm run lint && npm run check
+   npm run check
    ```
    - Ensures all code quality standards are met
    - Prevents committing code with linting/formatting issues
PATCH

echo "Gold patch applied."
