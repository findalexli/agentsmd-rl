#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vitess

# Idempotency guard
if grep -qF "- **Reuse existing helpers** - Before writing new parsing/validation code, check" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -67,7 +67,14 @@ func TestConnectionBilateralCleanup(t *testing.T) {
 // Step 5: Refactor for clarity
 ```
 
-To make sure tests are easy to read, we use `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/require` for assertions. Use `assert.Eventually` instead of manual `time.Sleep()` and timeouts. Use `t.Cleanup()` for test cleanup and `t.Context()` for the test's parent context.
+To make sure tests are easy to read, we use `github.com/stretchr/testify/assert` and `github.com/stretchr/testify/require` for assertions:
+- Use `require` (not `assert`) when the test cannot continue after a failure (e.g., `require.NoError` after setup that must succeed)
+- Use `assert.Eventually` instead of manual `time.Sleep()` and timeouts
+- Use `t.Context()` instead of `context.Background()` — it integrates with test cancellation
+- Use `t.Cleanup()` for test teardown
+- Use `assert.ErrorContains` / `require.ErrorContains` to check error messages
+- Use the `_test.go` suffix for mocks and test helpers that are only used by the current package's tests; if helpers or mocks need to be imported by other packages' tests or fuzz harnesses, put them in a normal reusable package such as `testlib` or `testutil`
+- CI timeouts must be generous (30s+) — GitHub Actions runners can be resource-starved with multi-second pauses; sub-second timeouts cause flakiness with no recourse but retry
 
 ## :rotating_light: Error Handling Excellence
 
@@ -103,6 +110,15 @@ func ProcessUser(id string) *User {
 4. **Fail fast** - Don't continue with invalid state
 5. **Log appropriately** - Errors at boundaries, debug info internally
 6. **Return structured errors** - Use error types for different handling
+7. **Never silently swallow errors** - When recovering from an error (e.g., restarting replication), always log the original error before the recovery attempt so operators can trace what happened
+8. **Log with context** - Include workflow name, recovery type, tablet alias, and other identifiers in log messages — a keyspace/tablet can have many concurrent workflows
+
+### Failure-Path Safety
+Multi-step operations must not leave the system in a half-applied state:
+- If step 2 of 3 succeeds but step 3 fails, ensure step 2 is rolled back or the cleanup path handles it
+- Deferred cleanup must use bounded contexts — never `context.Background()` for operations that could hang indefinitely
+- When holding a mutex, always bound the operation with a reasonable timeout
+- Test failure paths, not just the happy path — a test that only proves "step X ran" without covering "what if step X+1 fails" is incomplete
 
 ### Testing Error Paths
 ```go
@@ -137,23 +153,36 @@ return user.NeedsMigration() && migrate(user) || user
 - Obvious parameter types
 - No hidden side effects
 
-### 3. Performance with Clarity
-- Optimize hot paths
-- But keep code readable
+### 3. Conditions Must Be as Specific as the Intent
+- Guard clauses should match *exactly* the intended case, not just currently-known cases
+- A check like `len(tables) == 0` when you mean "is virtual dual" will silently fire for future zero-table cases
+- A nil return from a helper (e.g., `operatorKeyspace()` returning nil for composite operators) should not be treated as "safe to skip" — handle it explicitly
+- When catching MySQL error codes, match the specific codes that apply to your call site, not a broad class
+
+### 4. Zero-Value / Default Behavior Safety
+- New struct fields must not change behavior for existing callers who omit them
+- Prefer negative-polarity booleans (`NoCrossKeyspaceJoins` not `AllowCrossKeyspaceJoins`) so the zero-value preserves existing behavior
+- When a flag value of `0` or empty previously meant "disabled," don't change it to mean "unlimited" — preserve the existing semantic or make the change explicit
+- Validate mutually exclusive flags in `PreRunE` and add unit tests for invalid combinations
+
+### 5. Performance with Clarity
+- Optimize hot paths, but keep code readable
+- Preallocate slices and maps when the size is known: `make([]T, 0, len(source))`
+- Avoid duplicate work — cache results of expensive calls like `reflect.Value.MapKeys()` instead of calling twice
 - Document why, not what
 
-### 4. Fail Fast and Clearly
+### 6. Fail Fast and Clearly
 - Validate inputs early
 - Return clear error messages
 - Help future debugging
 
-### 5. Interfaces Define What You Need, Not What You Provide
+### 7. Interfaces Define What You Need, Not What You Provide
 - When you need something from another component, define the interface in your package
 - Don't look at what someone else provides - define exactly what you require
 - This keeps interfaces small, focused, and prevents unnecessary coupling
 - Types and their methods live together. At the top of files, use a single ```type ()``` with all type declarations inside.
 
-### 6. Go-Specific Best Practices
+### 8. Go-Specific Best Practices
 - **Receiver naming** - Use consistent, short receiver names (e.g., `u *User`, not `user *User`)
 - **Package naming** - Short, descriptive, lowercase without underscores
 - **Interface naming** - Single-method interfaces end in `-er` (Reader, Writer, Handler)
@@ -164,6 +193,9 @@ return user.NeedsMigration() && migrate(user) || user
 - **Copyright header** - New Go files must include the project copyright header with the current year
 - **Always run `gofumpt -w`** on changed Go files before committing - this is mandatory
 - **Always run `goimports -local "vitess.io/vitess" -w`** on changed Go files before committing
+- **Use format verbs precisely** - Use `%s` for strings and `%d` for integers, not `%v` for everything
+- **Structured logging** - New log messages should use structured logging with `slog`-style fields (e.g., `log.Warn("message", slog.Any("error", err))`) rather than printf-style logging with format strings
+- **Reuse existing helpers** - Before writing new parsing/validation code, check for existing utilities (e.g., `sqlerror` package for MySQL error codes, `mysqlctl.ParseVersionString()`, `strings.Split()`, `topoproto.TabletAliasString()` for formatting tablet aliases)
 
 ## :building_construction: Vitess-Specific Conventions
 
@@ -180,6 +212,7 @@ return user.NeedsMigration() && migrate(user) || user
 #### SQL Parser
 - **Never** directly edit these generated files in `go/vt/sqlparser/`: `sql.go`, `ast_clone.go`, `ast_copy_on_rewrite.go`, `ast_equals.go`, `ast_format_fast.go`, `ast_path.go`, `ast_rewrite.go`, `ast_visit.go`, `cached_size.go`
 - After modifying source files (e.g., `sql.y`, AST definitions), run `make codegen` to regenerate
+- Field order in AST structs matters — generated walkers visit fields in declaration order, so reordering fields changes semantic-analysis walk order and can break scope setup
 
 ### Command-Line Flags
 - New flags must **not** use underscores (use hyphens instead)
@@ -188,11 +221,21 @@ return user.NeedsMigration() && migrate(user) || user
 ### TabletAlias Formatting
 - Format `*topodatapb.TabletAlias` using `topoproto.TabletAliasString(alias)` in logs and error messages so that tablet aliases are human-readable
 
+### MySQL Flavor Isolation
+- MySQL-version-specific behavior belongs in the corresponding flavor implementation (e.g., MariaDB handling in the MariaDB flavor file), not in generic code
+- Be aware that MariaDB and older MySQL versions may not support all system variables (e.g., `super_read_only`) — other Vitess call sites already warn-and-continue for `ERUnknownSystemVariable`
+
+### User-Visible Changes
+- Any user-visible behavioral change — even a correctness fix — needs explicit callout in release/deployment notes
+- Removing or renaming a public API function (e.g., in `sqlparser`) is a breaking change for downstream users — call it out explicitly or keep a thin compatibility wrapper
+- Changelog summaries are for key changes all users should know about — internal implementation details don't belong there
+- Keep PRs clean of unrelated diffs (e.g., stray `package-lock.json` changes, `go.sum` without `go mod tidy`)
+
 ### EmergencyReparentShard (ERS)
 - ERS must prioritize **certainty** that we picked the most-advanced candidate
 - Changes should prioritize reducing points of failure - avoid new RPCs or work that may delay or make ERS more brittle
 
-## :mag: Dubugging & Troubleshooting
+## :mag: Debugging & Troubleshooting
 
 When things don't work as expected, we debug systematically:
 
@@ -205,23 +248,21 @@ When things don't work as expected, we debug systematically:
 
 ### Debugging Tools & Techniques
 ```go
-// Use structured logging for debugging
-log.WithFields(log.Fields{
-    "user_id": userID,
-    "action": "process_payment", 
-    "amount": amount,
-}).Debug("Starting payment processing")
+// Use structured logging (slog-style) for new code
+log.Info("Starting payment processing",
+    slog.String("user_id", userID),
+    slog.String("action", "process_payment"),
+    slog.Float64("amount", amount),
+)
 
 // Add strategic debug points
 func processPayment(amount float64) error {
-    log.Debugf("processPayment called with amount: %f", amount)
-    
     if amount <= 0 {
-        return fmt.Errorf("invalid amount: %f", amount)
+        return vterrors.Errorf(vtrpcpb.Code_INVALID_ARGUMENT, "invalid amount: %f", amount)
     }
-    
+
     // More processing...
-    log.Debug("Payment validation passed")
+    log.Info("Payment validation passed")
     return nil
 }
 ```
PATCH

echo "Gold patch applied."
