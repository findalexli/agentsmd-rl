#!/usr/bin/env bash
set -euo pipefail

cd /workspace/swc

# Idempotency guard
if grep -qF "- The suite mirrors `swc_ecma_parser` fixture skip rules for `typescript/tsc` an" "crates/swc_es_parser/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/swc_es_parser/AGENTS.md b/crates/swc_es_parser/AGENTS.md
@@ -1,9 +1,9 @@
-# swc_es_parser Bootstrap Design
+# swc_es_parser Parity Design
 
 ## AST Model
 
 - `swc_es_ast` stores nodes in arena pools and references them using typed ids.
-- Initial node groups include statements, declarations, expressions, module declarations, class/function, JSX, and TypeScript placeholders.
+- The parser keeps allocating directly into `swc_es_ast` without intermediate trees.
 
 ## Error Model
 
@@ -16,11 +16,13 @@
 - Hand-written recursive descent parser with Pratt-style expression precedence.
 - Script/module/program entry points share the same token stream and AST store.
 - Module declarations are represented as `Stmt::ModuleDecl` for top-level interoperability.
+- A parity fixture mode can classify known shared fixtures as expected success or expected failure.
 
-## Fixture Reuse
+## Fixture Parity Contract
 
-- `swc_es_parser/tests/smoke.rs` consumes fixture inputs from `swc_ecma_parser/tests`.
-- Fixture output is intentionally parser-local and does not target `swc_ecma_parser` snapshot parity.
+- `swc_es_parser/tests/parity_suite.rs` reuses the `swc_ecma_parser/tests` fixture corpus.
+- The suite enforces pass/fail parity only (not diagnostic-text parity).
+- The suite mirrors `swc_ecma_parser` fixture skip rules for `typescript/tsc` and `test262` pass ignores.
 
 ## Performance Notes
 
PATCH

echo "Gold patch applied."
