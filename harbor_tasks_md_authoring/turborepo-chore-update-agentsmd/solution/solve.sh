#!/usr/bin/env bash
set -euo pipefail

cd /workspace/turborepo

# Idempotency guard
if grep -qF "- If you do not have dependencies available, you can download them with `pnpm in" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -27,6 +27,11 @@ When making changes to the codebase, check if the following docs need updates:
 
 ## Pull Request Guidelines
 
+### Always run pre-commit/pre-push hooks
+
+- You are not allowed to use `--no-verify` when making a commit or push.
+- If you do not have dependencies available, you can download them with `pnpm install --frozen-lockfile`.
+
 ### PR Title Format
 
 PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/). See [`.github/workflows/lint-pr-title.yml`](./.github/workflows/lint-pr-title.yml) for the enforced constraints.
PATCH

echo "Gold patch applied."
