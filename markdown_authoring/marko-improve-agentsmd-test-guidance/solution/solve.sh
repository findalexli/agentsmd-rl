#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marko

# Idempotency guard
if grep -qF "Prefer running specific fixtures when possible. Running the entire suite takes t" "packages/runtime-tags/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/runtime-tags/AGENTS.md b/packages/runtime-tags/AGENTS.md
@@ -188,7 +188,11 @@ npm test -- --grep "runtime-tags.*" # all tests (uses mocha)
 npm test -- --grep "runtime-tags.* <fixture> " # specific fixture
 npm test -- --grep "runtime-tags.* <fixture> compile" # compiled outputs only
 npm test -- --grep "runtime-tags.* <fixture> render" # render outputs only
-npm test -- --grep "runtime-tags.*" --update # snapshot update
+
+npm test -- --grep "runtime-tags.*" --update # all tests snapshot update
+npm test -- --grep "runtime-tags.* <fixture> " --update # fixture snapshot update
 
 npm test -- --grep "translator-interop.*" # interop tests (run after the base tags runtime tests pass)
 ```
+
+Prefer running specific fixtures when possible. Running the entire suite takes time!
PATCH

echo "Gold patch applied."
