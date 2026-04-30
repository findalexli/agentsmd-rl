#!/usr/bin/env bash
set -euo pipefail

cd /workspace/css-modules-kit

# Idempotency guard
if grep -qF "- `<type>` is one of: feat, fix, docs, refactor, test, chore, deps" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -116,10 +116,22 @@ function myFunction() {
 - pnpm, pnpm workspaces
 - Changesets
 
-## Other
+## Development Flow
 
+- Write PR descriptions and commit messages in English
 - Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
-  - `<type>`: use one of feat, fix, docs, refactor, test, chore, deps
+  - `<type>` is one of: feat, fix, docs, refactor, test, chore, deps
   - `[optional scope]`: choose one of core, ts-plugin, codegen, vscode, stylelint-plugin, eslint-plugin, zed
     - For changes spanning multiple packages, use comma-separated scopes like `feat(core, ts-plugin): ...`
 - If you make changes that affect users, add a changeset file under `.changeset`
+- Assign appropriate labels when creating a PR
+  - `Type: Breaking Change`: Breaking changes
+  - `Type: Bug`: Bug fixes
+  - `Type: Documentation`: Documentation changes
+  - `Type: Feature`: New features
+  - `Type: Refactoring`: Refactoring
+  - `Type: Testing`: Test additions/modifications
+  - `Type: Maintenance`: Repository maintenance
+  - `Type: CI`: CI/CD changes
+  - `Type: Security`: Security-related changes
+  - `Type: Dependencies`: Dependency updates
PATCH

echo "Gold patch applied."
