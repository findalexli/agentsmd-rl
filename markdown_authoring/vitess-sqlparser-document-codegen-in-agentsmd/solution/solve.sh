#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotency guard
if grep -qF "- **Resolving merge conflicts in generated files** \u2192 resolve the *source* file c" "go/vt/sqlparser/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/go/vt/sqlparser/AGENTS.md b/go/vt/sqlparser/AGENTS.md
@@ -1,5 +1,40 @@
 # SQL Parser
 
+## Code Generation
+
+Many files in this package are generated. **Never edit generated files directly.**
+
+### Commands
+
+| Command | What it does |
+|---|---|
+| `make codegen` | Runs both `make sqlparser` and `make sizegen` |
+| `make sqlparser` | Runs `go generate ./go/vt/sqlparser/...` (parser + AST helpers + formatter) |
+| `make sizegen` | Runs `sizegen` to regenerate `cached_size.go` files across the repo |
+
+### Generated file map
+
+| Generated file | Source / generator | Regenerate with |
+|---|---|---|
+| `sql.go` | `sql.y` via `goyacc` | `make sqlparser` |
+| `ast_clone.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_copy_on_rewrite.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_equals.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_path.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_rewrite.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_visit.go` | `ast.go` via `asthelpergen` | `make sqlparser` |
+| `ast_format_fast.go` | AST types via `astfmtgen` | `make sqlparser` |
+| `cached_size.go` | AST types via `sizegen` | `make sizegen` |
+
+The `go:generate` directives live in `generate.go`.
+
+### When to regenerate
+
+- **Modified `sql.y`** → `make sqlparser` (or `make codegen` to also update sizes)
+- **Modified AST types in `ast.go`** → `make codegen`
+- **Modified size-cached types** → `make sizegen`
+- **Resolving merge conflicts in generated files** → resolve the *source* file conflict, then regenerate
+
 ## Tokenizer
 
 The tokenizer (`token.go`) processes SQL input character-by-character. When
PATCH

echo "Gold patch applied."
