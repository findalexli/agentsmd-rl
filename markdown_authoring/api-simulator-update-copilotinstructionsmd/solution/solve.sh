#!/usr/bin/env bash
set -euo pipefail

cd /workspace/api-simulator

# Idempotency guard
if grep -qF ".github/copilot-instructions.md" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -83,10 +83,4 @@ templates/                    # Scaffold templates used during code generation
 
 Always run `yarn lint:fix` before committing to automatically fix linting issues, then run `yarn test` to verify nothing is broken. Run `yarn lint` before opening a PR to confirm no remaining errors. Black-box tests require a build (`yarn build`) and Python 3 with pytest and requests installed (`pip install -r test-black-box/requirements.txt`); run them when touching server startup or CLI behaviour.
 
-## Coding Conventions
 
-### TypeScript vs JavaScript
-
-- New files under `src/server/` and `src/repl/` should be **TypeScript** (`.ts`).
-- Files under `src/typescript-generator/` are intentionally **JavaScript** (`.js`) because they generate code as strings and mixing generated-string manipulation with TypeScript generics adds noise without benefit.
-- Keep new additions consistent with the language used by existing files in the same directory.
PATCH

echo "Gold patch applied."
