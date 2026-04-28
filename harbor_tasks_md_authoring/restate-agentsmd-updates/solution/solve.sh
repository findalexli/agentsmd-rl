#!/usr/bin/env bash
set -euo pipefail

cd /workspace/restate

# Idempotency guard
if grep -qF "4. **Lint check** (if you modified Rust files): Run `cargo clippy --all-features" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -58,8 +58,9 @@ After making code changes, always run the following validation steps before comm
 1. **Build check**: Run `cargo check` to ensure the code compiles without errors.
 2. **Run tests**: Run `cargo nextest run --all-features` to ensure all tests pass.
 3. **Format check** (if you modified Rust files): Run `cargo fmt --all -- --check` to verify formatting.
-4. **Lint check** (if you modified Rust files): Run `cargo clippy --all-features --workspace -- -D warnings` to check for lint warnings.
+4. **Lint check** (if you modified Rust files): Run `cargo clippy --all-features --all-targets --workspace -- -D warnings` to check for lint warnings.
 5. **Deny check** (if you modified Cargo.toml or Cargo.lock): Run `cargo deny --all-features check` to check for license and security issues.
+6. If you are making changes to Cargo.toml files, make sure to also regenerate workspace-hack (cargo hakari generate)
 
 When renaming or changing trait methods, function signatures, or public APIs, search the entire codebase
 for all usages to ensure they are all updated consistently. Use `grep`, `rg`, or similar tools to find all
PATCH

echo "Gold patch applied."
