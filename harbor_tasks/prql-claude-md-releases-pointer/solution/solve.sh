#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prql

# Idempotency: skip if the new section header already exists.
if grep -Fq "## Releases & Environment" CLAUDE.md; then
    echo "CLAUDE.md already contains the Releases & Environment section; nothing to do."
    exit 0
fi

git apply <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 40a79cbc1aba..75033478072f 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
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

echo "Patch applied."
