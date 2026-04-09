# Fix broken doctests in uv-keyring

## Problem

Running `cargo test -p uv-keyring` causes doctest compilation failures. There are multiple issues in the crate's documentation code examples:

1. Code blocks in `crates/uv-keyring/README.md` and `crates/uv-keyring/src/mock.rs` reference a crate named `keyring` (e.g., `use keyring::{Entry, Result}`) which does not exist — the crate was renamed to `uv_keyring` when forked, so these imports fail with `unresolved import`.

2. The README example uses `.await` calls inside a synchronous `fn main()`, causing `await is only allowed inside async functions and blocks` errors.

3. The `crates/uv-keyring/src/mock.rs` module-level doc comment contains code examples with the same wrong `keyring::` references.

These broken examples are compiled as doctests by the `doc_comment::doctest!` macro in `crates/uv-keyring/src/lib.rs`.

## Expected Behavior

`cargo test --doc -p uv-keyring` should pass without compilation errors. All documentation code examples should either compile correctly or be removed/replaced with prose.

## Files to Look At

- `crates/uv-keyring/README.md` — usage example with wrong imports and missing async context
- `crates/uv-keyring/src/lib.rs` — contains the `doctest!` macro that compiles README as a doctest
- `crates/uv-keyring/src/mock.rs` — module doc comment with broken code examples
- `crates/uv-keyring/Cargo.toml` — dev-dependencies (includes `doc-comment` crate)
