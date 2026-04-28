#!/usr/bin/env bash
set -euo pipefail

cd /workspace/oxc

# Idempotency guard
if grep -qF "- **oxc_language_server**: Editor integration - `cargo test -p oxc_language_serv" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -31,11 +31,12 @@ Avoid editing `generated` subdirectories.
 - `oxc_diagnostics` - Error reporting
 - `oxc_traverse` - AST traversal utilities
 - `oxc_allocator` - Memory management
+- `oxc_language_server` - LSP server for editor integration
 - `oxc` - Main crate
 
 ## Development Commands
 
-Prerequisites: Rust (MSRV: 1.87.0), Node.js, pnpm, just
+Prerequisites: Rust (MSRV: 1.88.0), Node.js, pnpm, just
 
 **Setup Notes:**
 
@@ -224,6 +225,7 @@ just test-transform --filter <path>             # Filter tests
 - **oxc_ecmascript**: ECMAScript operations - `cargo test -p oxc_ecmascript`
 - **oxc_regular_expression**: Regex parsing - `cargo test -p oxc_regular_expression`
 - **oxc_syntax**: Syntax utilities - `cargo test -p oxc_syntax`
+- **oxc_language_server**: Editor integration - `cargo test -p oxc_language_server`
 
 ### Conformance Testing Foundation
 
@@ -286,6 +288,7 @@ Tests are TypeScript files in each package's `test/` directory.
 | Isolated Declarations | `tests/fixtures/*.ts`                   |
 | Semantic              | `tests/` directory                      |
 | NAPI packages         | `test/` directory (Vitest)              |
+| Language Server       | Inline and `/fixtures`                  |
 
 ## Notes
 
PATCH

echo "Gold patch applied."
