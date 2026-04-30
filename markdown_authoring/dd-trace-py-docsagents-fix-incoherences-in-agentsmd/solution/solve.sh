#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dd-trace-py

# Idempotency guard
if grep -qF "**Purpose:** Creates or updates release notes using Reno, following dd-trace-py'" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -15,7 +15,6 @@
 3. Assume business logic (always ask)
 4. Remove AIDEV- comments without instruction
 5. Skip linting before committing
-6. Check and remove unexpected prints
 
 **Always:**
 1. Use the run-tests skill for test execution
@@ -24,6 +23,7 @@
 4. Update AIDEV- anchors when modifying related code
 5. Consider performance impact (this runs in production)
 6. Consider architecture (try to use well-established patterns for the problem at hand)
+7. Check for and remove unexpected prints
 
 ## Initial Setup for AI Assistants
 
@@ -101,11 +101,12 @@ This project has custom skills that provide specialized workflows. **Always chec
 
 ### releasenote
 
-**Use whenever:** Creating or updating release notes for changes on the current branch.
+**Use whenever:** Creating or updating release notes for changes in the current branch.
 
-**Purpose:** Creates release notes using Reno, following dd-trace-py's conventions:
+**Purpose:** Creates or updates release notes using Reno, following dd-trace-py's conventions:
+- Generates Reno release note files for the current branch changes
 - Generates properly formatted release note files
-- Follows guidelines in `docs/releasenotes.rst`
+- Follows the guidelines in `docs/releasenotes.rst`
 - Places notes in the `releasenotes/` directory
 
 **Usage:** Use the Skill tool with command "releasenote"
PATCH

echo "Gold patch applied."
