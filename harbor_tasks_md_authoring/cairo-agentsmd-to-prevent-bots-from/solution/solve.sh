#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cairo

# Idempotency guard
if grep -qF "Do not read or grep crates/cairo-lang-syntax/src/node/ast.rs. Instead read crate" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1 @@
+Do not read or grep crates/cairo-lang-syntax/src/node/ast.rs. Instead read crates/cairo-lang-syntax-codegen/src/generator.rs.
PATCH

echo "Gold patch applied."
