#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if value_delimiter already present for no_emit_package in ExportArgs
if grep -A5 'no_emit_package.*Vec<PackageName>' crates/uv-cli/src/lib.rs | grep -q 'value_delimiter'; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-cli/src/lib.rs b/crates/uv-cli/src/lib.rs
index 516c9582dd8ef..fcf820ce7ebb1 100644
--- a/crates/uv-cli/src/lib.rs
+++ b/crates/uv-cli/src/lib.rs
@@ -1683,7 +1683,7 @@ pub struct PipCompileArgs {

     /// Specify a package to omit from the output resolution. Its dependencies will still be
     /// included in the resolution. Equivalent to pip-compile's `--unsafe-package` option.
-    #[arg(long, alias = "unsafe-package", value_hint = ValueHint::Other)]
+    #[arg(long, alias = "unsafe-package", value_delimiter = ',', value_hint = ValueHint::Other)]
     pub no_emit_package: Option<Vec<PackageName>>,

     /// Include `--index-url` and `--extra-index-url` entries in the generated output file.
@@ -4999,6 +4999,7 @@ pub struct ExportArgs {
         long,
         alias = "no-install-package",
         conflicts_with = "only_emit_package",
+        value_delimiter = ',',
         value_hint = ValueHint::Other,
     )]
     pub no_emit_package: Vec<PackageName>,
@@ -5009,6 +5010,7 @@ pub struct ExportArgs {
         alias = "only-install-package",
         conflicts_with = "no_emit_package",
         hide = true,
+        value_delimiter = ',',
         value_hint = ValueHint::Other,
     )]
     pub only_emit_package: Vec<PackageName>,

PATCH

echo "Patch applied successfully."
