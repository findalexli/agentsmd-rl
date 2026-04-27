#!/usr/bin/env bash
set -euo pipefail

cd /workspace/e2b

# Idempotency guard
if grep -qF "Default credentials are stored in .env.local in the repository root or inside ~/" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,5 @@
+Use pnpm for node and poetry for python to install and update dependencies.
+Run `pnpm run format`, `pnpm run lint` and `pnpm run typecheck` before commiting changes.
+To re-generate the API client run `make codegen` in the repository root.
+Run tests on affected codepaths using `pnpm run test`.
+Default credentials are stored in .env.local in the repository root or inside ~/.e2b/config.json.
PATCH

echo "Gold patch applied."
