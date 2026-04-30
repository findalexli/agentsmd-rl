#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cockroach

# Idempotency guard
if grep -qF "**Block comments** (standalone line) use full sentences with capitalization and " "CLAUDE.md" && grep -qF "- **Underscore separation**: `start_key` not `startkey` (consistent with informa" "pkg/sql/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,121 +4,79 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## CockroachDB Development Environment
 
-CockroachDB is a distributed SQL database written in Go, built with Bazel and managed through a unified `./dev` tool.
+CockroachDB is a distributed SQL database written in Go. We use Bazel as a build
+system but most operations are wrapped through the `./dev` tool, which should be
+preferred to direct `go (build|test)` or `bazel` invocations.
 
 ### Essential Commands
 
-**Setup and Environment Check:**
-```bash
-./dev doctor              # Verify development environment setup
-```
+**Building a package / package tests**
+
+This is useful as a compilation check.
 
-**Building:**
 ```bash
-./dev build cockroach     # Build full cockroach binary
-./dev build short         # Build cockroach without UI (faster)
-./dev build roachtest     # Build integration test runner
-./dev build workload      # Build load testing tool
+# Invoke (but skip) all tests in that package, which
+# implies that both package and its tests compile.
+./dev test ./pkg/util/log -f -
+# Build package ./pkg/util/log
+./dev build ./pkg/util/log
 ```
 
 **Testing:**
 ```bash
-./dev test pkg/sql                   # Run unit tests for SQL package
-./dev test pkg/sql -f=TestParse -v   # Run specific test pattern.
-./dev test pkg/sql --race            # Run with race detection
-./dev test pkg/sql --stress          # Run repeatedly until failure
-./dev testlogic                      # Run all SQL logic tests
-./dev testlogic ccl                  # Run enterprise logic tests
-./dev testlogic base --config=local --files='prepare|fk' # Run specific test files under a specific configuration
+./dev test pkg/sql                   # run unit tests for SQL package (slow!)
+./dev test pkg/sql -f=TestParse -v   # run specific test pattern
 ```
 
 Note that when filtering tests via `-f` to include the `-v` flag which
 will warn you in the output if your filter didn't match anything. Look
 for `testing: warning: no tests to run` in the output.
 
-**Code Generation and Linting:**
-```bash
-./dev generate            # Generate all code (protobuf, parsers, etc.)
-./dev generate go         # Generate Go code only
-./dev generate bazel      # Update BUILD.bazel files when dependencies change
-./dev generate protobuf   # Generate files based on protocol buffer definitions
-./dev lint                # Run all linters (only run this when requested)
-./dev lint --short        # Run fast subset of linters (only run this when requested)
-```
+See `./dev test --help` for all options`.
 
-### Architecture Overview
+**Building:**
 
-CockroachDB follows a layered architecture:
-```
-SQL Layer (pkg/sql/) → Distributed KV (pkg/kv/) → Storage (pkg/storage/)
+```bash
+./dev build cockroach     # build full cockroach binary
+./dev build short         # build cockroach without UI (faster)
 ```
 
-**Key Components:**
-- **SQL Engine**: `/pkg/sql/` - Complete PostgreSQL-compatible SQL processing
-- **Transaction Layer**: `/pkg/kv/` - Distributed transactions with Serializable Snapshot Isolation
-- **Storage Engine**: `/pkg/storage/` - RocksDB/Pebble integration with MVCC
-- **Consensus**: `/pkg/raft/` - Raft protocol for data replication
-- **Networking**: `/pkg/rpc/`, `/pkg/gossip/` - RPC and cluster coordination
-- **Enterprise Features**: `/pkg/ccl/` - Commercial features (backup, restore, multi-tenancy)
-
-**Key Design Patterns:**
-- Range-based data partitioning (512MB default ranges)
-- Raft consensus per range for strong consistency
-- Lock-free transactions with automatic retry handling
-- Multi-tenancy with virtual clusters
+Building a CockroachDB binary (even in short mode) should be considered
+slow. Avoid doing this unless necessary.
 
-### Development Workflow
+Use `./dev build --help` for the entire list of artifacts that can
+be built.
 
-1. **Environment Setup**: Run `./dev doctor` to ensure all dependencies are installed.
-2. **Building**: Use `./dev build short` for iterative development, `./dev build cockroach` for full builds.
-3. **Testing**: Run package-specific tests with `./dev test pkg/[package]`.
-4. **Code Generation**: After schema/proto changes, run `./dev generate go`.
-5. **Linting**: Run with `./dev lint` or `./dev lint --short`. This takes a while, so no need to run it regularly.
-
-### Testing Strategy
-
-CockroachDB has comprehensive testing infrastructure:
-- **Unit Tests**: Standard Go tests throughout `/pkg/` packages.
-- **Logic Tests**: SQL correctness tests using `./dev testlogic`.
-- **Roachtests**: Distributed system integration tests.
-- **Acceptance Tests**: End-to-end testing in `/pkg/acceptance/`.
-- **Stress Testing**: Continuous testing with `--stress` flag.
-
-
-### Build System
+**Code Generation and Linting:**
 
-- **Primary Tool**: Bazel (wrapped by `./dev` script)
-- **Cross-compilation**: Support for Linux, macOS, Windows via `--cross` flag
-- **Caching**: Distributed build caching for faster builds
-- **Multiple Binaries**: Produces `cockroach`, `roachprod`, `workload`, `roachtest`, etc.
+Protocol buffers, SQL parser, SQL Optimizer rules and others rely on Go code
+generated by `./dev generate <args>`. This should be considered a slow command.
+Rebuild only what is actually needed. `./dev (test|build)` commands
+automatically generate their dependencies, but do not lift them into the
+worktree, i.e. if they need to be visible to you, you need to invoke the
+appropriate `./dev generate` command yourself.
 
-### Code Organization
+```bash
+./dev generate            # generate all code (protobuf, parsers, etc.) - SLOW
+./dev generate go         # generate Go code only
+./dev generate bazel      # update BUILD.bazel files when dependencies change
+./dev generate protobuf   # generate protobuf files - relatively fast
+```
 
-**Package Structure:**
-- `/pkg/sql/` - SQL layer (parser, optimizer, executor)
-- `/pkg/sql/opt` - Query optimizer and planner
-- `/pkg/sql/schemachanger` - Declarative schema changer
-- `/pkg/kv/` - Key-value layer and transaction management
-- `/pkg/storage/` - Storage engine interface
-- `/pkg/server/` - Node and cluster management
-- `/pkg/ccl/` - Enterprise/commercial features
-- `/pkg/util/` - Shared utilities across the codebase
-- `/docs/` - Technical documentation and RFCs
+See `./dev generate --help`.
 
-**Generated Code:**
-Large portions of the codebase are generated, particularly:
-- SQL parser from Yacc grammar
-- Protocol buffer definitions
-- Query optimizer rules
-- Various code generators in `/pkg/gen/`
+### Architecture Overview
 
-Always run `./dev generate` after modifying `.proto` files, SQL grammar, or optimizer rules.
+CockroachDB consists of many components and subsystems. The file .github/CODEOWNERS is a
+good starting point if the overall architecture is relevant to the task.
 
 ## Coding Guidelines
 
 ### Log and Error Redactability
 
-CockroachDB implements redactability to ensure sensitive information (PII, confidential data) is automatically removed or marked in log messages and error outputs. This enables customers to safely share logs with support teams.
+CockroachDB implements redactability to ensure sensitive information (PII,
+confidential data) is automatically removed or marked in log messages and error
+outputs. This enables customers to safely share logs with support teams.
 
 #### Core Concepts
 
@@ -136,17 +94,17 @@ CockroachDB implements redactability to ensure sensitive information (PII, confi
 **SafeValue Interface** - For types that are always safe:
 ```go
 type NodeID int32
-func (n NodeID) SafeValue() {}  // Always safe to log
+func (n NodeID) SafeValue() {}  // always safe to log
 
-// Interface verification pattern
+// Interface verification pattern.
 var _ redact.SafeValue = NodeID(0)
 ```
 
 **SafeFormatter Interface** - For complex types mixing safe/unsafe data:
 ```go
 func (s *ComponentStats) SafeFormat(w redact.SafePrinter, _ rune) {
     w.Printf("ComponentStats{ID: %v", s.Component)
-    // Use w.Printf(), w.SafeString(), w.SafeRune() to mark safe parts
+    // Use w.Printf(), w.SafeString(), w.SafeRune() to mark safe parts.
 }
 ```
 
@@ -157,6 +115,9 @@ func (s *ComponentStats) SafeFormat(w redact.SafePrinter, _ rune) {
 
 #### Redactcheck Linter
 
+Prefer using SafeFormatter, which does not require the below check.
+If implementing SafeValue instead:
+
 The linter in `/pkg/testutils/lint/passes/redactcheck/redactcheck.go`:
 - Maintains allowlist of types permitted to implement `SafeValue`
 - Validates `RegisterSafeType` calls
@@ -180,31 +141,44 @@ CockroachDB uses a custom code formatter called `crlfmt` that goes beyond standa
 
 #### What is crlfmt
 
-`crlfmt` is CockroachDB's **custom Go code formatter** (not a wrapper around standard tools) that enforces specific coding standards beyond what `gofmt` and `goimports` provide. It's an external tool developed specifically for CockroachDB's needs.
+`crlfmt` is CockroachDB's **custom Go code formatter** (not a wrapper around
+standard tools) that enforces specific coding standards beyond what `gofmt` and
+`goimports` provide. It's an external tool developed specifically for
+CockroachDB's needs. Editor-integrated agents often don't need to invoke this,
+since the editor does it automatically. Otherwise, the agent should invoke the
+tool after each round of edits to ensure correct formatting.
 
 **Repository**: `github.com/cockroachdb/crlfmt`
 
-#### Key Features
+#### Formatting Standards
 
-**Enhanced Formatting:**
-- **Column wrapping**: Wraps code at 100 columns (vs. Go's typical 80 or unlimited)
-- **Tab width**: Uses 2-space tabs by default (`-tab 2`)
-- **Import grouping**: Intelligent import organization (`-groupimports`)
-- **Line length enforcement**: Strict 100-character line limits
+**Line Length and Wrapping:**
+- Code: 100 columns, Comments: 80 columns
+- Tab width: 2 characters
 
-**Operation Modes:**
-- **Write mode**: Overwrite files in place (`-w`)
-- **Diff mode**: Show differences only (`-diff`, default)
-- **Fast mode**: Skip `goimports` for faster operation (`-fast`)
+**Function Signatures:**
+```go
+func (s *someType) myFunctionName(
+    arg1 somepackage.SomeArgType, arg2 int, arg3 somepackage.SomeOtherType,
+) (somepackage.SomeReturnType, error) {
+    // ...
+}
+
+// One argument per line for long lists.
+func (s *someType) myFunctionName(
+    arg1 somepackage.SomeArgType,
+    arg2 int,
+    arg3 somepackage.SomeOtherType,
+) (somepackage.SomeReturnType, error) {
+    // ...
+}
+```
 
 #### Common Usage Patterns
 
 **Basic Formatting:**
 ```bash
-# Format a single file (most common)
-crlfmt -w filename.go
-
-# Format with CockroachDB standard settings
+# Format (in-place) with CockroachDB standard settings
 crlfmt -w -tab 2 filename.go
 
 # Check formatting without writing changes
@@ -220,36 +194,6 @@ find pkg/sql -name "*.go" | xargs -n1 crlfmt -w
 for f in pkg/sql/*.go; do crlfmt -w "$f"; done
 ```
 
-#### Configuration Options
-
-**Standard Settings:**
-- **Tab width**: 2 spaces (`-tab 2`)
-- **Column wrap**: 100 characters (`-wrap 100`)
-- **Import grouping**: Enabled by default
-- **Source directory**: For import resolution (`-srcdir`)
-
-**Performance Options:**
-- **Fast mode**: Skip `goimports` (`-fast`)
-- **Ignore patterns**: Skip matching files (`-ignore regex`)
-
-#### Best Practices
-
-**Development Workflow:**
-1. **Always use `-w`**: Write changes to files rather than just showing diffs
-2. **Use `-tab 2`**: Maintain consistency with CockroachDB standards
-3. **Run after changes**: Format code after making modifications
-4. **Run after generation**: Format generated code to match standards
-5. **Pre-commit formatting**: Run before committing to avoid CI failures
-
-**When to Use:**
-- After making any code changes
-- After running code generation
-- When lint tests fail due to formatting
-- As part of regular development workflow
-- Before submitting pull requests
-
-`crlfmt` is essential for maintaining CockroachDB's code quality standards and should be part of every developer's regular workflow. It ensures consistent formatting across the large, complex codebase while handling the specific requirements of a distributed systems project.
-
 ### Go Coding Guidelines
 
 CockroachDB follows specific Go coding conventions inspired by the Uber Go style guide with CockroachDB-specific modifications.
@@ -267,35 +211,35 @@ type S struct {
     data string
 }
 
-// Value receiver - can be called on pointers and values
+// Value receiver - can be called on pointers and values.
 func (s S) Read() string {
     return s.data
 }
 
-// Pointer receiver - needed to modify data
+// Pointer receiver - needed to modify data.
 func (s *S) Write(str string) {
     s.data = str
 }
 
-// Interface verification pattern
+// Interface verification pattern.
 var _ redact.SafeValue = NodeID(0)
 ```
 
 #### Memory Management and Concurrency
 
 **Mutexes:**
 ```go
-// Zero-value mutex is valid
+// Zero-value mutex is valid.
 var mu sync.Mutex
 mu.Lock()
 
-// Embed mutex in struct (preferred for private types)
+// Embed mutex in struct (preferred for private types).
 type smap struct {
     sync.Mutex
     data map[string]string
 }
 
-// Named field for exported types
+// Named field for exported types.
 type SMap struct {
     mu   sync.Mutex
     data map[string]string
@@ -304,14 +248,14 @@ type SMap struct {
 
 **Defer for Cleanup:**
 ```go
-// Always use defer for locks and cleanup
+// Always use defer for locks and cleanup.
 func (m *SMap) Get(k string) string {
     m.mu.Lock()
     defer m.mu.Unlock()
     return m.data[k]
 }
 
-// For panic protection, use separate function
+// For panic protection, use separate function.
 func myFunc() error {
     doRiskyWork := func() error {
         p.Lock()
@@ -323,20 +267,29 @@ func myFunc() error {
 ```
 
 **Slice and Map Copying:**
+
+Comments should clarify ownership.
+
 ```go
-// Document if API captures by reference
 // SetTrips sets the driver's trips.
 // Note that the slice is captured by reference, the
 // caller should take care of preventing unwanted aliasing.
 func (d *Driver) SetTrips(trips []Trip) { d.trips = trips }
+```
+
+or
 
-// Or make defensive copy
+```
+// SetTrips sets the driver's trips. It does not hold on
+// to the provided slice.
 func (d *Driver) SetTrips(trips []Trip) {
     d.trips = make([]Trip, len(trips))
     copy(d.trips, trips)
 }
+```
 
-// Return copies for internal state
+```
+// Snapshot returns a copy of the internal state.
 func (s *Stats) Snapshot() map[string]int {
     s.Lock()
     defer s.Unlock()
@@ -350,22 +303,27 @@ func (s *Stats) Snapshot() map[string]int {
 
 #### Performance Guidelines
 
+Many code paths are performance-sensitive and in particular
+heap allocations should be avoided. In all code paths, reasonably
+performant code should be written, as long as complexity does not
+significantly increase as a result. Some examples of this follow.
+
 **String Conversion:**
 ```go
-// strconv is faster than fmt for primitives
-s := strconv.Itoa(rand.Int()) // Good
-s := fmt.Sprint(rand.Int())   // Slower
+// strconv is faster than fmt for primitives.
+s := strconv.Itoa(rand.Int()) // good
+s := fmt.Sprint(rand.Int())   // slower
 ```
 
 **String-to-Byte Conversion:**
 ```go
-// Avoid repeated conversion
-data := []byte("Hello world")      // Good - once
+// Avoid repeated conversion.
+data := []byte("Hello world")      // good - once
 for i := 0; i < b.N; i++ {
     w.Write(data)
 }
 
-// Bad - repeated allocation
+// Bad - repeated allocation.
 for i := 0; i < b.N; i++ {
     w.Write([]byte("Hello world"))
 }
@@ -377,7 +335,7 @@ for i := 0; i < b.N; i++ {
 
 **Enums:**
 ```go
-// Start enums at one unless zero value is meaningful
+// Start enums at one unless zero value is meaningful.
 type Operation int
 const (
     Add Operation = iota + 1
@@ -386,30 +344,6 @@ const (
 )
 ```
 
-#### Code Style Standards
-
-**Line Length and Wrapping:**
-- Code: 100 columns, Comments: 80 columns
-- Tab width: 2 characters
-
-**Function Signatures:**
-```go
-func (s *someType) myFunctionName(
-    arg1 somepackage.SomeArgType, arg2 int, arg3 somepackage.SomeOtherType,
-) (somepackage.SomeReturnType, error) {
-    // ...
-}
-
-// One argument per line for long lists
-func (s *someType) myFunctionName(
-    arg1 somepackage.SomeArgType,
-    arg2 int,
-    arg3 somepackage.SomeOtherType,
-) (somepackage.SomeReturnType, error) {
-    // ...
-}
-```
-
 **Import Grouping:**
 ```go
 import (
@@ -425,44 +359,44 @@ import (
 
 **Variable Declarations:**
 ```go
-// Top-level: omit type if clear from function return
+// Top-level: omit type if clear from function return.
 var _s = F()
 
-// Local: use short declaration
+// Local: use short declaration.
 s := "foo"
 
-// Empty slices: prefer var declaration
+// Empty slices: prefer var declaration.
 var filtered []int
-// Over: filtered := []int{}
+// Over: filtered := []int{}.
 
-// nil is valid slice
-return nil // Not return []int{}
+// nil is a valid slice.
+return nil // not return []int{}
 
-// Check empty with len(), not nil comparison
+// Check empty with len(), not nil comparison.
 func isEmpty(s []string) bool {
-    return len(s) == 0 // Not s == nil
+    return len(s) == 0 // not s == nil
 }
 ```
 
 **Struct Initialization:**
 ```go
-// Always specify field names
+// Always specify field names.
 k := User{
     FirstName: "John",
     LastName: "Doe",
     Admin: true,
 }
 
-// Use &T{} instead of new(T)
+// Use &T{} instead of new(T).
 sptr := &T{Name: "bar"}
 ```
 
 **Bool Parameters:**
 ```go
-// Avoid naked bools - use comments or enums
+// Avoid naked bools - use comments or enums.
 printInfo("foo", true /* isLocal */, true /* done */)
 
-// Better: custom types
+// Better: custom types.
 type EndTxnAction bool
 const (
     Commit EndTxnAction = false
@@ -473,12 +407,12 @@ func endTxn(action EndTxnAction) {}
 
 **Error Handling:**
 ```go
-// Reduce variable scope
+// Reduce variable scope.
 if err := f.Close(); err != nil {
     return err
 }
 
-// Reduce nesting - handle errors early
+// Reduce nesting - handle errors early.
 for _, v := range data {
     if v.F1 != 1 {
         log.Printf("Invalid v: %v", v)
@@ -494,29 +428,17 @@ for _, v := range data {
 
 **Printf and Formatting:**
 ```go
-// Format strings should be const for go vet
+// Format strings should be const for go vet.
 const msg = "unexpected values %v, %v\n"
 fmt.Printf(msg, 1, 2)
 
-// Printf-style function names should end with 'f'
+// Printf-style function names should end with 'f'.
 func Wrapf(format string, args ...interface{}) error
 
-// Use raw strings to avoid escaping
+// Use raw strings to avoid escaping.
 wantError := `unknown error:"test"`
 ```
 
-#### SQL Column Naming Standards
-
-**Principles for SHOW statements and virtual tables:**
-- **Consistent casing** across all statements
-- **Same concept = same word**: `variable`/`value` between different SHOW commands
-- **Usable without quotes**: `start_key` not `"Start Key"`, avoid SQL keywords
-- **Underscore separation**: `start_key` not `startkey` (consistent with information_schema)
-- **Avoid abbreviations**: `id` OK (common), `loc` not OK (use `location`)
-- **Disambiguate primary key columns**: `zone_id`, `job_id`, `table_id` not just `id`
-- **Specify handle type**: `table_name` vs `table_id` to allow both in future
-- **Match information_schema**: Use same labels when possible and appropriate
-
 #### Testing Patterns
 
 **Table-Driven Tests:**
@@ -572,21 +494,45 @@ func Connect(addr string, opts ...Option) (*Connection, error) {
 }
 ```
 
-### Code Commenting Guidelines
+### Writing Comments
+
+#### Block Comments vs Inline Comments
+
+**Block comments** (standalone line) use full sentences with capitalization and punctuation:
+```go
+// Bad - panics on wrong type.
+t := i.(string)
+
+// Good - handles gracefully.
+t, ok := i.(string)
+```
+
+**Inline comments** (end of code line) are lowercase without terminal punctuation:
+```go
+s := strconv.Itoa(rand.Int()) // good
+s := fmt.Sprint(rand.Int())   // slower
+func (n NodeID) SafeValue() {}  // always safe to log
+```
 
 #### Engineering Standards (Enforced in Reviews)
 
-**Requirements:**
-- **Full sentences**: Capital letter at beginning, period at end, subject and verb
-- **More comments than code** in struct, API, and protobuf definitions
-- **Field lifecycle documentation**: What initializes, accesses, when obsolete
-- **Function phases**: Separate different processing phases with summary comments
-- **Grammar matters**: Make honest attempt, reviewers prefix grammar suggestions with "nit:"
+CockroachDB is a complex system and you should write code under the assumption
+that it will have to be understood and modified in the future by readers who
+have basic familiarity with CockroachDB, but are not experts on the respective
+subsystem.
+
+Key concepts and abstractions should be explained clearly, and lifecycles and
+ownership clearly stated. Whenever possible, you should use examples to make the
+code accessible to the reader. Comments should always add depth to the code
+(rather than repeating the code).
+
+When reviewing, other than technical correctness, you should also focus on the
+above aspects. Do not over-emphasize on grammar and comment typos, prefix with
+"nit:" in reviews.
 
-**Prohibited:**
-- **Reading code aloud**: Don't write "increments x" for `x++`
-- **Obvious iterations**: Don't write "iterate over strings" for `for i := range strs`
-- **Over-emphasis on grammar**: Prefix with "nit:" in reviews
+CockroachDB is a distributed system that allows for rolling upgrades. This means
+that any shared state or inter-process communication needs to be mindful of
+compatibility issues.  See `pkg/clusterversion` for more on this.
 
 #### Comment Types and Examples
 
@@ -723,18 +669,23 @@ enum ReplicaType {
 
 ### Error Handling
 
-CockroachDB uses the [github.com/cockroachdb/errors](https://github.com/cockroachdb/errors) library, a superset of Go's standard `errors` package and `pkg/errors`.
+CockroachDB uses the
+[github.com/cockroachdb/errors](https://github.com/cockroachdb/errors) library,
+a superset of Go's standard `errors` package and `pkg/errors`. Importantly,
+`cockroachdb/errors` interoperates with `cockroachdb/redact`. Ensure that
+information that is passed to error constructors has proper redaction, as
+unredacted information might be stripped before reaching our support team.
 
 #### Creating Errors
 
 ```go
-// Simple static string errors
+// Simple static string errors.
 errors.New("connection failed")
 
-// Formatted error strings
+// Formatted error strings.
 errors.Newf("invalid value: %d", val)
 
-// Assertion failures for implementation bugs (generates louder alerts)
+// Assertion failures for implementation bugs (generates louder alerts).
 errors.AssertionFailedf("expected non-nil pointer")
 ```
 
@@ -743,10 +694,10 @@ errors.AssertionFailedf("expected non-nil pointer")
 It can be helpful to add context when propagating errors up the call stack:
 
 ```go
-// Wrap with context (preferred over fmt.Errorf with %w)
+// Wrap with context (preferred over fmt.Errorf with %w).
 return errors.Wrap(err, "opening file")
 
-// Wrap with formatted context
+// Wrap with formatted context.
 return errors.Wrapf(err, "connecting to %s", addr)
 ```
 
@@ -763,10 +714,10 @@ return errors.Wrap(err, "new store")
 #### User-Facing Information
 
 ```go
-// Add hints for end-users (actionable guidance, excluded from Sentry)
+// Add hints for end-users (actionable guidance, excluded from Sentry).
 errors.WithHint(err, "check your network connection")
 
-// Add details for developers (contextual info, excluded from Sentry)
+// Add details for developers (contextual info, excluded from Sentry).
 errors.WithDetail(err, "request payload was 2.5MB")
 ```
 
@@ -775,16 +726,16 @@ errors.WithDetail(err, "request payload was 2.5MB")
 For errors that clients need to detect, use sentinel errors or custom types:
 
 ```go
-// Sentinel error pattern
+// Sentinel error pattern.
 var ErrNotFound = errors.New("not found")
 
 func Find(id string) error {
     return ErrNotFound
 }
 
-// Caller detection with errors.Is (works across network boundaries!)
+// Caller detection with errors.Is (works across network boundaries!).
 if errors.Is(err, ErrNotFound) {
-    // handle not found
+    // Handle not found.
 }
 ```
 
@@ -799,7 +750,7 @@ func (e *NotFoundError) Error() string {
     return fmt.Sprintf("%s not found", e.Resource)
 }
 
-// Caller detection with errors.As
+// Caller detection with errors.As.
 var nfErr *NotFoundError
 if errors.As(err, &nfErr) {
     log.Printf("missing: %s", nfErr.Resource)
@@ -821,10 +772,10 @@ if errors.As(err, &nfErr) {
 Error messages are redacted by default in Sentry reports. Mark data as safe explicitly:
 
 ```go
-// Mark specific values as safe for reporting
+// Mark specific values as safe for reporting.
 errors.WithSafeDetails(err, "node_id=%d", nodeID)
 
-// The Safe() wrapper for known-safe values
+// The Safe() wrapper for known-safe values.
 errors.Newf("processing %s", errors.Safe(operationName))
 ```
 
@@ -833,10 +784,10 @@ errors.Newf("processing %s", errors.Safe(operationName))
 Always use the "comma ok" idiom to avoid panics:
 
 ```go
-// Bad - panics on wrong type
+// Bad - panics on wrong type.
 t := i.(string)
 
-// Good - handles gracefully
+// Good - handles gracefully.
 t, ok := i.(string)
 if !ok {
     return errors.New("expected string type")
@@ -848,13 +799,6 @@ if !ok {
 - `/docs/RFCS/20190318_error_handling.md` - Error handling RFC
 - [cockroachdb/errors README](https://raw.githubusercontent.com/cockroachdb/errors/refs/heads/master/README.md) - Full API documentation
 
-## Special Considerations
-
-- **Bazel Integration**: All builds must go through Bazel - do not use `go build` or `go test` directly
-- **SQL Compatibility**: Maintains PostgreSQL wire protocol compatibility
-- **Multi-Version Support**: Handles mixed-version clusters during upgrades
-- **Performance Critical**: Many components are highly optimized with careful attention to allocations and CPU usage
-
 ### Resources
 
 - **Main Documentation**: https://cockroachlabs.com/docs/stable/
diff --git a/pkg/sql/CLAUDE.md b/pkg/sql/CLAUDE.md
@@ -0,0 +1,13 @@
+# SQL Package Development Guide
+
+## SQL Column Naming Standards
+
+**Principles for SHOW statements and virtual tables:**
+- **Consistent casing** across all statements
+- **Same concept = same word**: `variable`/`value` between different SHOW commands
+- **Usable without quotes**: `start_key` not `"Start Key"`, avoid SQL keywords
+- **Underscore separation**: `start_key` not `startkey` (consistent with information_schema)
+- **Avoid abbreviations**: `id` OK (common), `loc` not OK (use `location`)
+- **Disambiguate primary key columns**: `zone_id`, `job_id`, `table_id` not just `id`
+- **Specify handle type**: `table_name` vs `table_id` to allow both in future
+- **Match information_schema**: Use same labels when possible and appropriate
PATCH

echo "Gold patch applied."
