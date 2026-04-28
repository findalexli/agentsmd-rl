#!/usr/bin/env bash
set -euo pipefail

cd /workspace/eslint-interactive

# Idempotency guard
if grep -qF "- Commit messages follow [Conventional Commits](https://www.conventionalcommits." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -77,3 +77,9 @@ Higher-level orchestration: call Core methods, show spinners, handle user prompt
 ### ESLint Internals (`src/eslint/`)
 
 This code is forked from the internal ESLint API. Since the API required to implement eslint-interactive is not publicly exposed by ESLint, we are doing this.
+
+## Other
+
+- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
+  - `<type>` is one of: feat, fix, docs, refactor, test, chore, deps
+  - Example: `feat: implement some feature`
PATCH

echo "Gold patch applied."
