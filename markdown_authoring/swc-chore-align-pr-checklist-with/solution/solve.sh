#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swc

# Idempotency guard
if grep -qF "-   Before opening or updating a PR, always run this baseline locally." "AGENTS.md" && grep -qF "-   Before opening or updating a PR, always run this baseline locally." "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -25,6 +25,21 @@
 -   You can do `UPDATE=1 cargo test` to get test outputs updated for fixture tests.
 -   When instructed to fix tests, do not remove or modify existing tests.
 
+## PR / CI rule
+
+-   Before opening or updating a PR, always run this baseline locally.
+    -   `cargo fmt --all`
+    -   `cargo clippy --all --all-targets -- -D warnings`
+-   For each touched Rust crate, run crate-level verification locally.
+    -   `cargo test -p <crate>`
+-   If wasm binding packages are touched, run:
+    -   `(cd bindings/binding_core_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_minifier_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_es_ast_viewer && ./scripts/test.sh)`
+-   If node bindings or integration paths are touched, run:
+    -   `(cd packages/core && yarn build:dev && yarn test)`
+
 ## Compatibility rule
 
 -   Do not use unstable, nightly only features of rustc.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -33,6 +33,21 @@ When working in a specific directory, apply the rules from that directory and al
 -   You can do `UPDATE=1 cargo test` to get test outputs updated for fixture tests.
 -   When instructed to fix tests, do not remove or modify existing tests.
 
+## PR / CI rule
+
+-   Before opening or updating a PR, always run this baseline locally.
+    -   `cargo fmt --all`
+    -   `cargo clippy --all --all-targets -- -D warnings`
+-   For each touched Rust crate, run crate-level verification locally.
+    -   `cargo test -p <crate>`
+-   If wasm binding packages are touched, run:
+    -   `(cd bindings/binding_core_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_minifier_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_typescript_wasm && ./scripts/test.sh)`
+    -   `(cd bindings/binding_es_ast_viewer && ./scripts/test.sh)`
+-   If node bindings or integration paths are touched, run:
+    -   `(cd packages/core && yarn build:dev && yarn test)`
+
 ## Compatibility rule
 
 -   Do not use unstable, nightly only features of rustc.
PATCH

echo "Gold patch applied."
