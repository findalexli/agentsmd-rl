#!/usr/bin/env bash
set -euo pipefail

cd /workspace/services

# Idempotency guard
if grep -qF "- Memory allocator: Uses jemalloc by default with built-in heap profiling suppor" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -18,6 +18,13 @@ This is a Rust workspace containing multiple services and libraries:
 - **database** - PostgreSQL abstraction and migrations
 - **model** - Serialization models for API
 - **contracts** - Smart contract bindings
+- **ethrpc** - Extended Ethereum RPC client with batching layer
+- **chain** - Blockchain interaction utilities
+- **number** - Numerical type extensions and conversions for 256-bit integers
+- **app-data** - Order metadata validation with 8KB default size limit
+- **alerter** - Monitors orderbook metrics for orders that should be solved but aren't
+- **testlib** - Shared helpers for writing unit and end-to-end tests
+- **observe** - Initialization and helper functions for logging and metrics
 
 ## Architecture Overview
 
@@ -60,7 +67,7 @@ User signs order → Orderbook validates → Autopilot includes in auction
 
 ## Technology Stack
 
-- **Language**: Rust 2021+ Edition
+- **Language**: Rust 2024 Edition
 - **Runtime**: Tokio async
 - **Database**: PostgreSQL with sqlx
 - **Web3**: Alloy
@@ -71,12 +78,39 @@ User signs order → Orderbook validates → Autopilot includes in auction
 - **Protocol Documentation**: https://docs.cow.fi/
   - Technical Reference: API specs and SDK docs
   - Concepts: Protocol fundamentals and architecture
-
-## Testing
-
-- Use `just` commands for running tests (see Justfile)
+- **Alloy (Web3 library)**: Fetch https://alloy.rs/introduction/prompting for an AI-optimized guide covering providers, transactions, contracts, and migration from ethers-rs
+
+## Development Commands
+
+### Testing
+- Use `cargo nextest run` instead of `cargo test` (CI uses nextest and handles global state differently)
+- Run specific test suites:
+  - Unit tests: `cargo nextest run`
+  - Database tests: `cargo nextest run postgres -p orderbook -p database -p autopilot --test-threads 1 --run-ignored ignored-only`
+  - E2E local tests: `cargo nextest run -p e2e local_node --test-threads 1 --failure-output final --run-ignored ignored-only`
+  - E2E forked tests: `cargo nextest run -p e2e forked_node --test-threads 1 --run-ignored ignored-only --failure-output final`
+  - Driver tests: `RUST_MIN_STACK=3145728 cargo nextest run -p driver --test-threads 1 --run-ignored ignored-only`
 - E2E tests available in `crates/e2e`
-- Local development environment in `playground/`
+
+### Testing Requirements
+- PostgreSQL tests require local database: Run `docker compose up -d` first
+- Forked network tests require `anvil` (from Foundry) and RPC URLs
+  - Anvil binary: configurable via `ANVIL_COMMAND` env var (defaults to `"anvil"`, must be in PATH)
+  - Required env vars: `FORK_URL_MAINNET` and `FORK_URL_GNOSIS` (RPC endpoints for forking)
+- Use `--test-threads 1` for database and E2E tests to avoid conflicts
+- CI runs doc-tests, unit tests, DB tests, E2E tests (local and forked), and driver tests
+
+### Linting and Formatting
+- Format: **always** run with the nightly toolchain: `cargo +nightly fmt --all`
+- Spot format: `cargo +nightly fmt -- <path>` (never call stable `cargo fmt`)
+- Lint: `cargo clippy --locked --workspace --all-features --all-targets -- -D warnings`
+- Check format: `cargo +nightly fmt --all -- --check`
+
+### Local Development Environment
+- Start local PostgreSQL: `docker compose up -d`
+- Full playground environment: `docker compose -f playground/docker-compose.fork.yml up -d`
+- For forked network tests, set environment variables: `FORK_URL_MAINNET` and `FORK_URL_GNOSIS`
+- Reset playground: `docker compose -f playground/docker-compose.fork.yml down --remove-orphans --volumes`
 
 ## Directory Structure
 
@@ -87,6 +121,31 @@ playground/     # Local dev environment
 configs/        # Configuration files
 ```
 
+## Workspace Configuration
+
+- Rust Edition 2024
+- Uses workspace dependencies for consistency
+- Tokio-console support: **Only available in playground environment** (set `TOKIO_CONSOLE=true` to activate when running in playground)
+- Production builds do **not** include tokio-console overhead
+- Runtime log filter changes via UNIX socket at `/tmp/log_filter_override_<program_name>_<pid>.sock`
+- Memory allocator: Uses jemalloc by default with built-in heap profiling support (enable at runtime via MALLOC_CONF environment variable). Can optionally use mimalloc via `--features mimalloc-allocator`
+
+## Playground Environment
+
+- Runs in **Fork** mode: anvil forks a real network via `ETH_RPC_URL` (set in `playground/.env`). A clean local network mode is planned but not yet implemented.
+- Access full local development stack with CoW Swap UI at http://localhost:8000
+- CoW Explorer available at http://localhost:8001
+- Orderbook API at http://localhost:8080
+- Database admin (Adminer) at http://localhost:8082
+- Uses test mnemonic: "test test test test test test test test test test test junk"
+- First 10 accounts have 10000 ETH balance by default, set by anvil
+
+## Development Notes
+
+- Binaries support `--help` for comprehensive command documentation
+- OpenAPI documentation available for orderbook, driver, and solver APIs
+- Performance profiling: Only available in playground (requires tokio-console feature + tokio_unstable cfg)
+
 # General Coding Instructions
 
 If there is a test you can run then run it or `cargo check` or `cargo build`; run it after you have made changes.
PATCH

echo "Gold patch applied."
