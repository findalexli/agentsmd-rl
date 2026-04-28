#!/usr/bin/env bash
set -euo pipefail

cd /workspace/camunda

# Idempotency guard
if grep -qF "- Do not use commit scopes \u2014 commitlint enforces `scope-empty`. Use `fix: ...` n" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -98,6 +98,7 @@ Types: `build`, `ci`, `deps`, `docs`, `feat`, `fix`, `merge`, `perf`, `refactor`
 
 - Separate behavioral changes from structural/refactoring changes into distinct commits
 - Commit messages should explain *why*, not just *what* changed
+- Do not use commit scopes — commitlint enforces `scope-empty`. Use `fix: ...` not `fix(ci): ...`
 
 ## Pull Request Conventions
 
PATCH

echo "Gold patch applied."
