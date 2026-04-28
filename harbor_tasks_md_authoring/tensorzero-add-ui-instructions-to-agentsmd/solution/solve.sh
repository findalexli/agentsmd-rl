#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tensorzero

# Idempotency guard
if grep -qF "- After modifying UI code, run from the `ui/` directory: `pnpm run format`, `pnp" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -13,3 +13,7 @@ The pre-commit hooks automatically handle this by running `uv lock` and `uv expo
 # CI/CD
 
 - Most GitHub Actions workflows run on Unix only, but some also run on Windows and macOS. For workflows that run on multiple operating systems, ensure any bash scripts are compatible with all three platforms. You can check which OS a workflow uses by looking at the `runs-on` field. Setting `shell: bash` in the job definition is often sufficient.
+
+# UI
+
+- After modifying UI code, run from the `ui/` directory: `pnpm run format`, `pnpm run lint`, `pnpm run typecheck`. All commands must pass.
PATCH

echo "Gold patch applied."
