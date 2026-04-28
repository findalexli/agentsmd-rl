#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cockroach

# Idempotency guard
if grep -qF "./dev test ./pkg/util/log -f -." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -17,7 +17,7 @@ This is useful as a compilation check.
 ```bash
 # Invoke (but skip) all tests in that package, which
 # implies that both package and its tests compile.
-./dev test ./pkg/util/log -f -
+./dev test ./pkg/util/log -f -.
 # Build package ./pkg/util/log
 ./dev build ./pkg/util/log
 ```
PATCH

echo "Gold patch applied."
