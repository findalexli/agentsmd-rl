#!/usr/bin/env bash
set -euo pipefail

cd /workspace/tsgolint

# Idempotency guard
if grep -qF "- `typescript-go/` - **[SUBMODULE]** TypeScript Go port submodule (temporary loc" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -28,7 +28,7 @@ If you need to modify typescript-go functionality permanently:
 2. Create a patch file in `patches/` using `git format-patch`
 3. Document the patch purpose in `patches/README.md`
 4. Reset the typescript-go submodule to its original state
-5. The patches will be applied during the build process using `git am --3way --no-gpg-sign ../patches/*.patch`
+5. The patches are applied during project initialization (`just init`) using `git am --3way --no-gpg-sign ../patches/*.patch`
 
 ### Exposing New Functions
 
@@ -44,14 +44,15 @@ When exposing new functions from typescript-go:
 
 ## Repository Structure
 
-- `typescript-go/` - **[SUBMODULE - DO NOT MODIFY]** TypeScript Go port submodule
-- `patches/` - Patches applied to typescript-go during build
+- `typescript-go/` - **[SUBMODULE]** TypeScript Go port submodule (temporary local edits are OK for testing; never commit submodule pointer changes)
+- `patches/` - Patches applied to typescript-go during `just init`
 - `shim/` - **[GENERATED - DO NOT EDIT]** Generated Go bindings to typescript-go internals
 - `cmd/` - CLI entry point and main application
 - `internal/` - Core linting logic and rule implementations
+  - `collections/` - Copied from `typescript-go/internal/collections` during `just init`
   - `linter/` - Linting engine and worker pool
   - `rule/` - Rule interface and context management
-  - `rules/` - Individual rule implementations (40+ rules)
+  - `rules/` - Individual rule implementations (50+ rules)
   - `utils/` - Shared utilities and helpers
 - `e2e/` - End-to-end tests and fixtures
 - `tools/` - Development tools and generators
@@ -70,7 +71,7 @@ TSGolint serves as a type-aware linting backend for Oxlint:
 - **Oxlint** handles CLI, file discovery, and output formatting
 - **TSGolint** processes TypeScript files and returns diagnostics
 - Uses typescript-go for native-speed parsing and type checking
-- Implements 40+ type-aware rules from typescript-eslint
+- Implements 50+ type-aware rules from typescript-eslint
 
 ### 2. Performance Design
 
@@ -83,9 +84,9 @@ TSGolint serves as a type-aware linting backend for Oxlint:
 Rules follow a consistent pattern:
 
 ```go
-type Rule interface {
-    Name() string
-    Run(ctx RuleContext) RuleListeners
+type Rule struct {
+    Name string
+    Run  func(ctx RuleContext, options any) RuleListeners
 }
 ```
 
@@ -125,11 +126,11 @@ cd e2e && pnpm test
 **Prefer ast-grep over grep/ripgrep for searching code patterns:**
 
 ```bash
-# Find all rule implementations
-ast-grep --pattern 'type $NAME struct { $$$ }' --lang go
+# Find all rule definitions
+ast-grep --pattern 'var $RULE = rule.Rule{$$$}' --lang go internal/rules/
 
-# Find specific function patterns
-ast-grep --pattern 'func ($_ $_) Run(ctx RuleContext) RuleListeners'
+# Find rules that parse options
+ast-grep --pattern 'utils.UnmarshalOptions[$TYPE](options, $RULE_NAME)' --lang go internal/rules/
 
 # Find TypeScript test fixtures
 ast-grep --pattern 'expect($$$)' --lang ts internal/rules/fixtures/
@@ -168,9 +169,10 @@ OXC_LOG=debug tsgolint
 
 ### DO NOT Modify
 
-- `typescript-go/*` - Submodule (use patches instead)
+- `typescript-go/*` - Submodule in this repo (do not commit direct submodule pointer updates; use `patches/*` for permanent changes)
 - `shim/*` - Generated code (regenerate with tools)
 - `.gitmodules` - Submodule configuration
+- `internal/collections/*` - Synced from `typescript-go` by `just init`
 
 ### Modify with Caution
 
@@ -206,7 +208,7 @@ When working on TSGolint:
 
 ## Common Pitfalls
 
-1. **Modifying typescript-go**: Changes will be lost on submodule update
+1. **Modifying typescript-go without patches**: Changes will be lost on submodule update
 2. **Editing shims**: Manual edits will be overwritten on regeneration
 3. **Blocking workers**: Reduces parallelism and performance
 4. **AST assumptions**: TypeScript AST differs from ESTree
@@ -247,10 +249,10 @@ tsgolint -cpuprof cpu.prof <files>
 go tool pprof cpu.prof
 
 # Search for code patterns (prefer ast-grep over grep/ripgrep for code searches)
-ast-grep --pattern 'func $NAME($$$) RuleListeners' internal/rules/
+ast-grep --pattern 'var $RULE = rule.Rule{$$$}' --lang go internal/rules/
 
 # Check rule coverage
-ast-grep --pattern 'func ($_ $_) Run(ctx RuleContext) RuleListeners' internal/rules/
+ast-grep --pattern 'var $RULE = rule.Rule{$$$}' --lang go internal/rules/ | wc -l
 ```
 
 ## Integration with Oxlint
@@ -262,11 +264,11 @@ TSGolint is designed as a backend for Oxlint:
 3. TSGolint returns structured diagnostics
 4. Oxlint formats and displays results
 
-The integration point is the headless service mode in `cmd/tsgolint/service.go`.
+The integration point is the headless mode in `cmd/tsgolint/headless.go` (with payload schema in `cmd/tsgolint/payload.go`).
 
 ## Contributing Guidelines
 
-1. **Never commit typescript-go changes**
+1. **Never commit `typescript-go` submodule pointer changes**
 2. Follow existing code patterns
 3. Add comprehensive tests
 4. Document complex logic
PATCH

echo "Gold patch applied."
