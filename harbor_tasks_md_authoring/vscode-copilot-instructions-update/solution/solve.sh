#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency guard
if grep -qF "- Do not use `any` or `unknown` as the type for variables, parameters, or return" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -130,7 +130,7 @@ function f(x: number, y: string): void { }
 - Don't add tests to the wrong test suite (e.g., adding to end of file instead of inside relevant suite)
 - Look for existing test patterns before creating new structures
 - Use `describe` and `test` consistently with existing patterns
+- Prefer regex capture groups with names over numbered capture groups.
 - If you create any temporary new files, scripts, or helper files for iteration, clean up these files by removing them at the end of the task
-- Do not use `any` or `unknown` as the type for variables, parameters, or return values unless absolutely necessary. If they need type annotations, they should have proper types or interfaces defined.
 - Never duplicate imports. Always reuse existing imports if they are present.
-- Prefer regex capture groups with names over numbered capture groups.
+- Do not use `any` or `unknown` as the type for variables, parameters, or return values unless absolutely necessary. If they need type annotations, they should have proper types or interfaces defined.
PATCH

echo "Gold patch applied."
