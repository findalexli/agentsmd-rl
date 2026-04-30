#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nearcore

# Idempotency guard
if grep -qF "- Run with `RUSTFLAGS=\"-D warnings\"` env variable and `--all-features --all-targ" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -18,6 +18,10 @@
 
 ## Clippy
 - Only run clippy prior to making a commit. It is somewhat expensive.
+- Run with `RUSTFLAGS="-D warnings"` env variable and `--all-features --all-targets` args.
+  ```
+  RUSTFLAGS="-D warnings" cargo clippy --all-features --all-targets
+  ```
 
 ## OpenAPI Spec
 - Do NOT update the OpenAPI spec unless explicitly asked.
PATCH

echo "Gold patch applied."
