#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gluesql

# Idempotency guard
if grep -qF "- When importing items, group them under a single `use` statement whenever possi" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,6 +1,7 @@
 # AGENTS.md
 - After editing code, run `cargo clippy --all-targets -- -D warnings`.
 - Then run `cargo fmt --all`.
+- When importing items, group them under a single `use` statement whenever possible.
 - Run tests related to your changes when available; running the entire test suite is not required.
 - Commit only when the above steps succeed.
 - Branch names may contain only lowercase a-z, dashes (-), and slashes (/).
PATCH

echo "Gold patch applied."
