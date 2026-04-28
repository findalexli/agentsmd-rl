#!/usr/bin/env bash
set -euo pipefail

cd /workspace/libxmtp

# Idempotency guard
if grep -qF "For changes in the `bindings_node` crate, run the `./dev/lint` script, but also " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -29,11 +29,13 @@ LibXMTP is a shared library encapsulating the core functionality of the XMTP mes
 ## Development Commands
 
 ### Environment Setup
+
 ```bash
 dev/up                    # Install dependencies and start services
 ```
 
 ### Testing
+
 ```bash
 cargo test                # Run Rust tests
 RUST_LOG=off cargo test   # Run tests with minimal logging
@@ -42,6 +44,7 @@ dev/test/browser-sdk     # Run browser SDK tests
 ```
 
 ### Code Quality
+
 ```bash
 dev/lint                 # Run all linting (shellcheck, markdown, rust)
 dev/fmt                  # Format code (markdown and rust)
@@ -50,12 +53,14 @@ dev/lint-rust           # Run Rust clippy linter against all targets
 ```
 
 ### Build & Services
+
 ```bash
 dev/docker/up           # Start Docker services (XMTP node)
 dev/docker/down         # Stop Docker services
 ```
 
 ### Platform-Specific
+
 ```bash
 dev/check-wasm          # Check WASM bindings
 dev/check-android       # Check Android bindings
@@ -65,19 +70,23 @@ dev/check-swift         # Check Swift bindings
 ## Testing Tips
 
 ### Log Output Control
+
 - `CONTEXTUAL=1 cargo test` - Async-aware structured logging
 - `STRUCTURED=1 cargo test` - JSON structured logs
 - `RUST_LOG=xmtp_mls=debug,xmtp_api=off cargo test` - Filter by crate
 
 ### Test Utilities
+
 - Many developers use `cargo nextest` for better test isolation
 - Use `TestLogReplace` for human-readable test output
 - Build `TesterBuilder` with `.with_name()` for named test instances
 
 ### Writing Tests
+
 - **ALWAYS use `#[xmtp_common::test]` instead of `#[test]`** - This ensures tests run in both native and WebAssembly environments
 - Use `rstest` for parameterized tests with `#[case]` attributes for concise, case-driven testing
 - Example:
+
   ```rust
   use rstest::rstest;
 
@@ -94,6 +103,8 @@ dev/check-swift         # Check Swift bindings
   }
   ```
 
+- Use the `tester!` macro for tests that require a wallet
+
 ## Required Tools
 
 - Rust (via rustup)
@@ -106,12 +117,14 @@ dev/check-swift         # Check Swift bindings
 The project provides Nix flake-based development shells with all required dependencies. This is the recommended approach for development as it provides consistent, reproducible environments across different platforms.
 
 ### Prerequisites
+
 ```bash
 # Install Nix with flakes enabled
 curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
 ```
 
 ### Available Development Shells
+
 ```bash
 nix develop                    # Default shell for general Rust development
 nix develop .#android         # Android development shell with NDK
@@ -121,7 +134,9 @@ nix develop .#wasmBuild       # WebAssembly build environment
 ```
 
 ### Using the Default Shell
+
 The default development shell includes:
+
 - Rust toolchain (version pinned to 1.89.0)
 - Cargo and related tools
 - Docker and Docker Compose
@@ -139,6 +154,7 @@ dev/lint
 ```
 
 ### Shell Features
+
 - **Cachix Integration**: Pre-built binaries available via `xmtp.cachix.org`
 - **Pinned Dependencies**: Consistent tool versions across all environments
 - **Cross-compilation**: Android and iOS targets available in respective shells
@@ -153,4 +169,12 @@ dev/lint
 
 ## Database
 
-Uses Diesel ORM with SQLite backend. Migrations are in `xmtp_db/migrations/`.
\ No newline at end of file
+Uses Diesel ORM with SQLite backend. Migrations are in `xmtp_db/migrations/`.
+
+### Code Change Requirements
+
+When making code changes in Rust, always ensure that the code is linted and formatted by running the `./dev/lint` script.
+
+For changes in the `bindings_node` crate, run the `./dev/lint` script, but also run `yarn` and `yarn format:check` in the `bindings_node` folder.
+
+Add new test coverage when appropriate.
PATCH

echo "Gold patch applied."
