#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mono

# Idempotency guard
if grep -qF "2. **Optional fields convention**: In this codebase, whenever there's an optiona" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,10 @@
+# Project Guidelines for Claude
+
+## Code Quality
+1. **Always run lint and format after every change** - This ensures code consistency and catches potential issues early.
+2. **TypeScript checking must pass before every commit** - Most packages have a `type-check` command that must pass before committing changes.
+
+## TypeScript Conventions
+2. **Optional fields convention**: In this codebase, whenever there's an optional field (marked with `?`), the type is always explicitly defined as `type | undefined`. 
+   - Example: `foo?: number | undefined` (not just `foo?: number`)
+   - You can always explicitly pass `undefined` for optional fields in this codebase
\ No newline at end of file
PATCH

echo "Gold patch applied."
