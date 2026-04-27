#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotency guard
if grep -qF "- **No naked returns in non-trivial functions** - For functions with named retur" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -67,25 +67,25 @@ func TestConnectionBilateralCleanup(t *testing.T) {
 // Step 5: Refactor for clarity
 ```
 
-To make sure tests are easy to read, we use testify assertions. Make sure to use assert.Eventually instead of using manual thread.sleep and timeouts.
+To make sure tests are easy to read, we use `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/require` for assertions. Use `assert.Eventually` instead of manual `time.Sleep()` and timeouts. Use `t.Cleanup()` for test cleanup and `t.Context()` for the test's parent context.
 
 ## :rotating_light: Error Handling Excellence
 
 Error handling is not an afterthought - it's core to reliable software.
 
 ### Go Error Patterns
 ```go
-// YES - Clear error context
+// YES - Clear error context with vterrors
 func ProcessUser(id string) (*User, error) {
     if id == "" {
-        return nil, fmt.Errorf("user ID cannot be empty")
+        return nil, vterrors.Errorf(vtrpcpb.Code_FAILED_PRECONDITION, "user ID cannot be empty")
     }
-    
+
     user, err := db.GetUser(id)
     if err != nil {
-        return nil, fmt.Errorf("failed to get user %s: %w", id, err)
+        return nil, vterrors.Wrapf(err, "failed to get user %s", id)
     }
-    
+
     return user, nil
 }
 
@@ -97,11 +97,12 @@ func ProcessUser(id string) *User {
 ```
 
 ### Error Handling Principles
-1. **Wrap errors with context** - Use `fmt.Errorf("context: %w", err)`
-2. **Validate early** - Check inputs before doing work
-3. **Fail fast** - Don't continue with invalid state
-4. **Log appropriately** - Errors at boundaries, debug info internally
-5. **Return structured errors** - Use error types for different handling
+1. **Use `vterrors`** - Prefer `vterrors` over `fmt.Errorf` or `errors` package, with an appropriate `vtrpcpb.Code` (e.g., `vtrpcpb.Code_FAILED_PRECONDITION` for unexpected input values, `vtrpcpb.Code_INTERNAL` for internal operation failures)
+2. **Wrap errors with context** - Use `vterrors.Wrapf(err, "context")`
+3. **Validate early** - Check inputs before doing work
+4. **Fail fast** - Don't continue with invalid state
+5. **Log appropriately** - Errors at boundaries, debug info internally
+6. **Return structured errors** - Use error types for different handling
 
 ### Testing Error Paths
 ```go
@@ -158,6 +159,38 @@ return user.NeedsMigration() && migrate(user) || user
 - **Interface naming** - Single-method interfaces end in `-er` (Reader, Writer, Handler)
 - **Context first** - Always pass `context.Context` as the first parameter
 - **Channels for coordination** - Use channels to coordinate goroutines, not shared memory
+- **No naked returns in non-trivial functions** - For functions with named return values, avoid bare `return` and explicitly return all result values (very small helpers are the only exception). This does not prohibit plain `return` in `func f() { ... }` when used for early-exit/guard clauses.
+- **Reduce nesting** - Prefer early returns and guard clauses over deeply nested `if` conditions
+- **Copyright header** - New Go files must include the project copyright header with the current year
+- **Always run `gofumpt -w`** on changed Go files before committing - this is mandatory
+- **Always run `goimports -local "vitess.io/vitess" -w`** on changed Go files before committing
+
+## :building_construction: Vitess-Specific Conventions
+
+### Generated Code
+- **Never** directly edit files with a `Code generated ... DO NOT EDIT` header - these are generated and will be overwritten
+- Run `make codegen` to regenerate after modifying source definitions
+
+#### Protobufs
+- **Never** directly edit files under `go/vt/proto/` - they are generated from `proto/*.proto` protobuf definitions
+- After modifying `proto/*.proto` files, run `make proto` to regenerate
+- Avoid storing timestamps or time durations as integers; use `vttime.Time` for timestamps and `vttime.Duration` (or `google.protobuf.Duration`, as appropriate) for durations instead
+- Avoid storing tablet aliases as a string: use `topodata.TabletAlias`
+
+#### SQL Parser
+- **Never** directly edit these generated files in `go/vt/sqlparser/`: `sql.go`, `ast_clone.go`, `ast_copy_on_rewrite.go`, `ast_equals.go`, `ast_format_fast.go`, `ast_path.go`, `ast_rewrite.go`, `ast_visit.go`, `cached_size.go`
+- After modifying source files (e.g., `sql.y`, AST definitions), run `make codegen` to regenerate
+
+### Command-Line Flags
+- New flags must **not** use underscores (use hyphens instead)
+- When flags are added or modified, update the corresponding `go/flags/endtoend/` files - column/whitespace alignment matters
+
+### TabletAlias Formatting
+- Format `*topodatapb.TabletAlias` using `topoproto.TabletAliasString(alias)` in logs and error messages so that tablet aliases are human-readable
+
+### EmergencyReparentShard (ERS)
+- ERS must prioritize **certainty** that we picked the most-advanced candidate
+- Changes should prioritize reducing points of failure - avoid new RPCs or work that may delay or make ERS more brittle
 
 ## :mag: Dubugging & Troubleshooting
 
PATCH

echo "Gold patch applied."
