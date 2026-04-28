#!/usr/bin/env bash
set -euo pipefail

cd /workspace/icerpc-csharp

# Idempotency guard
if grep -qF "For pull requests targeting any other branch (e.g., release branches), flag API-" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -18,4 +18,4 @@ allowed to make API-breaking changes. This is by design.
 Do not suggest adding `[Obsolete]` attributes, compatibility overloads, or migration paths for these changes.
 They are intentional. Skip them entirely.
 
-For pull requests targeting any other branch (e.g., release branches), flag API-breaking changes as warnings.
+For pull requests targeting any other branch (e.g., release branches), flag API-breaking changes as warnings.
\ No newline at end of file
PATCH

echo "Gold patch applied."
