#!/usr/bin/env bash
set -euo pipefail

cd /workspace/liam

# Idempotency guard
if grep -qF "- Follow principles in @docs/test-principles.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -111,6 +111,10 @@ function saveUser(data: UserData, userId: string) {
 - Generate CSS type definitions with `pnpm gen:css`
 - Use CSS variables according to their intended purpose. Spacing variables should be used exclusively for margins and padding, while height and width specifications should use appropriate units (rem, px, etc.)
 
+### Testing
+
+- Follow principles in @docs/test-principles.md
+
 ## Pull Requests
 
 When creating pull requests, refer to @.github/pull_request_template.md for the required information and format.
PATCH

echo "Gold patch applied."
