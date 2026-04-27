#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swc

# Idempotency guard
if grep -qF "4. You can run fixture tests by doing `./scripts/test.sh`, and you can do `UPDAT" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,3 +1,11 @@
+# AI Agent Rules
+
+When working in a specific directory, apply the rules from that directory and all parent directories up to the root.
+
+## While working on `.`
+
+*Source: `AGENTS.md`*
+
 1. Write performant code. Always prefer performance over other things.
 2. Write comments and documentations in English.
 3. Do not use unstable, nightly only features of rustc.
@@ -6,3 +14,15 @@
 6. When instructed to fix tests, do not remove or modify existing tests.
 7. Write documentation for your code.
 8. Run `cargo fmt --all` before commiting files.
+
+
+---
+
+## While working on `crates/swc_ecma_minifier`
+
+*Source: `crates/swc_ecma_minifier/AGENTS.md`*
+
+1. You can run execution tests by doing `./scripts/exec.sh` to see if your changes are working.
+2. If an execution test fails, you are wrong.
+3. Always run execution tests after making changes.
+4. You can run fixture tests by doing `./scripts/test.sh`, and you can do `UPDATE=1 ./scripts/test.sh` to update fixtures.
PATCH

echo "Gold patch applied."
