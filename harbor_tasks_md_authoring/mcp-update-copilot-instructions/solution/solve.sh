#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp

# Idempotency guard
if grep -qF "Copilot submitted PRs are not trustworthy by default. Users with `write` access " ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -22,3 +22,9 @@
 - Include tests that cover your changes
 - Update CHANGELOG.md with your changes
 - Run `.\eng\common\spelling\Invoke-Cspell.ps1`
+- Create the auto-generated PR body as normal, but `copilot` should add an additional section after all of its regular PR body content. The contents should be:
+  ```
+  ## Invoking Livetests
+
+  Copilot submitted PRs are not trustworthy by default. Users with `write` access to the repo need to validate the contents of this PR before leaving a comment with the text `/azp run mcp - pullrequest - live`. This will trigger the necessary livetest workflows to complete required validation.
+  ```
\ No newline at end of file
PATCH

echo "Gold patch applied."
