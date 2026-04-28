#!/usr/bin/env bash
set -euo pipefail

cd /workspace/wvlet

# Idempotency guard
if grep -qF "- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -273,4 +273,12 @@ For error reporting, use WvletLangException and StatusCode enum. If necessary er
 
 ## Testing Notes
 - Use `shouldContain "(keyword)"` for checking string fragment in AirSpec
-- To debug SQL generator, add -L *GenSQL=trace to the test option
\ No newline at end of file
+- To debug SQL generator, add -L *GenSQL=trace to the test option
+
+## GitHub CLI Commands
+
+### Pull Request Management
+- Read PR review comments: `gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments`
+- Check PR status: `gh pr status`
+- View PR checks: `gh pr checks PR_NUMBER`
+- Merge PR: `gh pr merge --squash --auto`
\ No newline at end of file
PATCH

echo "Gold patch applied."
