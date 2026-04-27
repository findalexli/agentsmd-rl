#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swc

# Idempotency guard
if grep -qF "- Do not add a third pass, and do not merge analysis and transformation into a s" "crates/swc_es_minifier/AGENTS.md" && grep -qF "- Do not add a third pass, and do not merge analysis and transformation into a s" "crates/swc_es_transforms/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/swc_es_minifier/AGENTS.md b/crates/swc_es_minifier/AGENTS.md
@@ -0,0 +1,8 @@
+### Instructions
+
+- This crate must operate in exactly two passes.
+- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.
+- Pass 2 is the transform pass. It must apply transformations using data from pass 1.
+- Do not add a third pass, and do not merge analysis and transformation into a single pass.
+- Never add dependencies on any `swc_ecma_*` crate.
+
diff --git a/crates/swc_es_transforms/AGENTS.md b/crates/swc_es_transforms/AGENTS.md
@@ -0,0 +1,8 @@
+### Instructions
+
+- This crate must operate in exactly two passes.
+- Pass 1 is the analysis pass. It must collect data only and must not transform the AST.
+- Pass 2 is the transform pass. It must apply transformations using data from pass 1.
+- Do not add a third pass, and do not merge analysis and transformation into a single pass.
+- Never add dependencies on any `swc_ecma_*` crate.
+
PATCH

echo "Gold patch applied."
