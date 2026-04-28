#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rocketmq-rust

# Idempotency guard
if grep -qF "Root workspace commands do not cover standalone projects. If changes affect one " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,66 +1,99 @@
 # AGENTS.md
 
-## Scope
-This file applies to the whole repository unless a deeper `AGENTS.md` overrides it.
+## Scope and precedence
+- This file applies to the whole repository unless a deeper `AGENTS.md` overrides it.
+- Follow the nearest `AGENTS.md` for files under standalone projects and dashboard subdirectories.
+- Direct user instructions in the current conversation take precedence over this file.
+- If repository instructions conflict with each other, choose the more specific instruction and mention the conflict in the final response.
 
-## Toolchain
-- Use the repository Rust toolchain.
+## Repository shape
+- The repository root is the main Cargo workspace for the core RocketMQ Rust crates.
+- `rocketmq-example/` is a standalone Cargo project.
+- `rocketmq-dashboard/rocketmq-dashboard-gpui/` is a standalone Cargo project.
+- `rocketmq-dashboard/rocketmq-dashboard-tauri/` is the Tauri app root, not a Cargo workspace root.
+- `rocketmq-dashboard/rocketmq-dashboard-tauri/src-tauri/` is the standalone Rust backend for the Tauri app.
+- Root workspace validation does not validate standalone projects.
+
+## Codex workflow
+- Before editing, inspect the relevant files and check the worktree state with `git status --short`.
+- Treat existing uncommitted changes as user work. Do not overwrite, revert, or reformat unrelated changes.
+- Keep changes tightly scoped to the request. Avoid unrelated refactors, dependency updates, and configuration churn.
+- Prefer `rg` or `rg --files` for search. If unavailable, use the fastest local equivalent.
+- Follow existing module structure, naming, error handling, and test style before introducing new patterns.
+- Use patch-style edits for manual changes when tool support is available. Generated files and formatter output may be produced by their normal tools.
+- For behavior changes, add or update focused tests that would fail without the change.
+- Do not create commits, branches, or pull requests unless the user asks.
+
+## Rust toolchain and style
+- Use the repository Rust toolchain. Do not change `rust-toolchain.toml` unless explicitly required.
 - Respect `rustfmt.toml` and `.clippy.toml`.
-- Do not change toolchain or lint configuration unless explicitly required.
-
-## Mandatory validation
-After every Rust code change, always run the following for the affected Cargo project:
-1. `cargo fmt`
-2. `cargo clippy`
-
-Do not finish with unformatted code.
-Do not finish without a clippy pass.
-
-## Test policy
-- Tests only need to cover the modified area.
-- Do not run full-repository or full-workspace tests by default.
-- Prefer the smallest effective scope:
-  - package-level tests
-  - module-related tests
-  - named tests
-  - integration tests related to the change
-- Run broader tests only when the change affects shared infrastructure or multiple crates/projects.
-
-## Repository structure
-- The repository root is the main Cargo workspace.
-- `rocketmq-example` is a standalone Cargo project and must be validated separately.
-- `rocketmq-dashboard/rocketmq-dashboard-gpui` is a standalone Cargo project and must be validated separately.
-- `rocketmq-dashboard/rocketmq-dashboard-tauri` is not a Cargo workspace root.
-- The Rust backend for Tauri is in `rocketmq-dashboard/rocketmq-dashboard-tauri/src-tauri` and must be validated there separately.
-
-## Workspace changes
-For changes inside the root workspace, run from the repository root:
+- Do not relax lint, formatting, feature, or CI configuration to make a change pass unless the task specifically requires it.
+- Prefer clear, idiomatic Rust over clever abstractions.
+- Be mindful of allocations, blocking calls, and lock scope in hot paths and async code.
+
+## Mandatory Rust validation
+After every Rust code change, finish with a successful format pass and clippy pass for each affected Cargo project.
+
+Do not finish with unformatted Rust code.
+Do not finish without a relevant clippy pass.
+Do not claim validation passed unless the command completed successfully.
+
+Documentation-only changes do not require Cargo validation unless they affect generated Rust, build configuration, examples, or documented commands that need verification.
+
+## Root workspace validation
+For Rust changes inside the root workspace, run from the repository root:
 
 ```bash
 cargo fmt --all
 cargo clippy --workspace --no-deps --all-targets --all-features -- -D warnings
 ```
 
-Tests should remain targeted. Example:
+Package-level clippy may be useful while iterating, but the final required pass for root workspace Rust changes is the workspace command above.
+
+## Standalone project validation
+Root workspace commands do not cover standalone projects. If changes affect one of these projects, validate it in its own directory and follow any deeper `AGENTS.md` there:
+
+- `rocketmq-example/`
+- `rocketmq-dashboard/rocketmq-dashboard-gpui/`
+- `rocketmq-dashboard/rocketmq-dashboard-tauri/src-tauri/`
+
+When no deeper instruction gives a different command, use:
 
 ```bash
-cargo test -p rocketmq-common
-cargo test -p rocketmq-client
-cargo test -p rocketmq-remoting some_test_name
+cargo fmt --all
+cargo clippy --all-targets --all-features -- -D warnings
 ```
 
-## Standalone project rule
-Root workspace validation does not cover standalone projects.
+For `rocketmq-dashboard/rocketmq-dashboard-tauri/` frontend changes, follow the dashboard `AGENTS.md` in that directory.
+
+## Testing policy
+- Run tests only for the modified area by default.
+- Prefer the smallest effective scope: named test, module test, package test, then broader integration tests.
+- Run broader tests only when the change affects shared infrastructure, feature flags, public cross-crate APIs, or multiple crates.
+- For bug fixes, add or update a regression test when practical.
+- For new behavior, add or update tests that cover the externally visible behavior.
 
-If changes affect any of the following, validate them in their own directories:
-- `rocketmq-example`
-- `rocketmq-dashboard/rocketmq-dashboard-gpui`
-- `rocketmq-dashboard/rocketmq-dashboard-tauri/src-tauri`
+Examples:
+
+```bash
+cargo test -p rocketmq-common
+cargo test -p rocketmq-client --lib
+cargo test -p rocketmq-remoting some_test_name
+```
 
 ## Shared code rule
-If a shared crate is modified and that change can affect a standalone project, also validate the affected standalone project.
+If a shared crate is modified and that change can affect standalone projects, validate the affected standalone projects as well.
+
+Common shared crates include:
+- `rocketmq-common`
+- `rocketmq-runtime`
+- `rocketmq-client`
+- `rocketmq-remoting`
+- `rocketmq-macros`
+- `rocketmq-error`
 
-## Change hygiene
-- Keep changes scoped to the task.
-- Add or update tests when behavior changes.
-- Prefer minimal targeted validation over broad validation.
+## Final response expectations
+- Summarize the files changed and the intent of the change.
+- List validation commands run and their result.
+- If required validation was skipped or could not run, explain why and identify the remaining risk.
+- Mention any pre-existing unrelated worktree changes only if they matter to the task.
PATCH

echo "Gold patch applied."
