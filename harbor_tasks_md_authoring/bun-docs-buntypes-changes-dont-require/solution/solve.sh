#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency guard
if grep -qF "Edits to **TypeScript type declarations** (`packages/bun-types/**/*.d.ts`) do no" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -32,6 +32,16 @@ When exec args are present, build output is suppressed unless the build fails 
 bun run build:release --build-dir=build/baseline
 ```
 
+### Changes that don't require a build
+
+Edits to **TypeScript type declarations** (`packages/bun-types/**/*.d.ts`) do not touch any compiled code, so `bun bd` is unnecessary. The types test just packs the `.d.ts` files and runs `tsc` against fixtures — it never executes your build. Run it directly with the system Bun:
+
+```sh
+bun test test/integration/bun-types/bun-types.test.ts
+```
+
+This is an explicit exception to the "never use `bun test` directly" rule. There are no native changes for a debug build to pick up, so don't wait on one.
+
 ## Testing
 
 ### Running Tests
PATCH

echo "Gold patch applied."
