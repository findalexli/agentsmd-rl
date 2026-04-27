#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotency guard
if grep -qF "`web/book/src/project/contributing/development.md`." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -88,3 +88,8 @@ View target/doc/prqlc/module_name/index.html
 # For function documentation
 View target/doc/prqlc/fn.compile.html
 ```
+
+## Releases & Environment
+
+For releases or environment issues, see
+`web/book/src/project/contributing/development.md`.
PATCH

echo "Gold patch applied."
