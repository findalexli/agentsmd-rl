#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ai-maestro

# Idempotency guard
if grep -qF "**This is NON-NEGOTIABLE.** Every PR to main MUST include a version bump. No exc" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -54,14 +54,28 @@ This script updates ALL version references across the codebase:
 
 **DO NOT manually edit version numbers in individual files.** Always use the script to ensure consistency.
 
+## Pre-PR Checklist (MANDATORY)
+
+**⚠️ STOP! Before creating ANY Pull Request to main, complete this checklist:**
+
+```
+□ 1. BUMP VERSION: ./scripts/bump-version.sh patch
+□ 2. BUILD PASSES: yarn build
+□ 3. COMMIT version bump with your changes
+```
+
+**This is NON-NEGOTIABLE.** Every PR to main MUST include a version bump. No exceptions.
+
+---
+
 ## Release & Marketing Workflow
 
 ### Pull Request Protocol
 
 **IMPORTANT:** Every time you create a Pull Request to main, also draft an X (Twitter) post to announce the release.
 
 **PR Creation Checklist:**
-1. **BUMP VERSION FIRST** - Run `./scripts/bump-version.sh patch` (or minor/major) BEFORE creating the PR. This is mandatory for every PR to main.
+1. ✅ **VERSION BUMPED** (see Pre-PR Checklist above - this should already be done)
 2. Create PR with comprehensive description (summary, features, bug fixes, breaking changes)
 3. Draft X post highlighting key features and improvements
 4. Include release notes or link to PR in the post
PATCH

echo "Gold patch applied."
