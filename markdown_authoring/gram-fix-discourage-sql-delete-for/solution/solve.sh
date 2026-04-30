#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gram

# Idempotency guard
if grep -qF "Deleting rows with `DELETE FROM table` is strongly discouraged. Instead," "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -193,7 +193,7 @@ create table if not exists example (
 );
 ```
 
-Deleting rows with `DELETE FROM table` is not strongly discouraged. Instead,
+Deleting rows with `DELETE FROM table` is strongly discouraged. Instead,
 use:
 
 ```sql
PATCH

echo "Gold patch applied."
