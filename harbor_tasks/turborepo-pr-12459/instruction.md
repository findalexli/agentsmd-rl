# Instruction — vercel/turborepo#12459

## Problem

`turbo watch` crashes with a thread panic when the task graph contains persistent
tasks (e.g., `"persistent": true` in `turbo.json`, commonly used for dev servers
like `vite`, `webpack dev-server`, `nodemon`, etc.).

## Target Files

- `crates/turborepo-lib/src/task_graph/visitor/mod.rs` — `finish()` method, error collection
- `crates/turborepo-lib/src/run/mod.rs` — `execute_visitor()` method, process cleanup

## Verification

- The `turborepo-lib` crate must compile cleanly with `cargo check -p turborepo-lib`
- Clippy must pass with no warnings: `cargo clippy -p turborepo-lib`
- Existing unit tests must pass: `cargo test -p turborepo-lib`
- Watch mode tests must pass: `cargo test -p turborepo-lib run::watch`
- Visitor command tests must pass: `cargo test -p turborepo-lib task_graph::visitor::command`
- Task filter tests must pass: `cargo test -p turborepo-lib run::task_filter`
- Formatting check must pass: `cargo fmt --check`
