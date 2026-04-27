# Make `uv cache clear` work as an alias of `uv cache clean`

The uv CLI uses [clap](https://docs.rs/clap) to parse subcommands. Today,
running `uv cache clean` clears the cache as expected, but a common point
of confusion is that users frequently type `uv cache clear` instead — and
that command currently fails with a clap "unrecognized subcommand" error.

Your job is to make `uv cache clear` behave as a true alias of
`uv cache clean`, so that both invocations dispatch to the exact same
handler with the exact same arguments and the same `--help` output.

## Repository

The uv source tree is checked out at `/workspace/uv` (Rust workspace,
edition 2024). The `uv` binary is built into `target/debug/uv` — after
making your change, rebuild with:

```bash
cargo build --bin uv
```

## Required behavior (after your fix)

Concretely, every one of the following must hold:

1. `uv cache clear --help` exits with status `0` and prints help text.
   (At baseline it exits non-zero because clap does not know the
   subcommand `clear`.)
2. `uv cache clear --cache-dir <some-dir>` runs to completion and exits
   `0`, just like `uv cache clean --cache-dir <some-dir>` does.
3. `uv cache clear` actually removes the cache contents — i.e. it really
   is the same operation as `cache clean`, not a separate no-op
   subcommand. Populate a cache directory with a sentinel file, run
   `uv cache clear --cache-dir <dir>`, and the directory must be empty
   (or removed) afterwards.
4. The help text printed by `uv cache clear --help` must match the help
   text printed by `uv cache clean --help` byte-for-byte, modulo the
   `Usage:` line which naturally mentions the invoked name. (This is the
   distinguishing property of a clap subcommand alias versus two
   independent subcommands that happen to share an implementation.)
5. `uv cache clean` must continue to work exactly as before — the alias
   addition must not break the original subcommand name.

## Constraints

- Do not introduce a new `Clear` enum variant or a duplicate handler.
  The two names must dispatch to the same code path; the existing
  `Clean` handler should be reused.
- Do not change the public signature of `CleanArgs` or the behavior of
  the existing cache-clean implementation.
- You may only modify Rust source files under `crates/`. Do not edit
  generated files, snapshot fixtures, or `Cargo.lock`.

## Code Style Requirements

The repository's CLAUDE.md specifies several Rust style rules that apply
here:

- AVOID using `panic!`, `unreachable!`, `.unwrap()`, unsafe code, and
  clippy rule ignores.
- PREFER patterns like `if let` to handle fallibility.
- PREFER `#[expect()]` over `#[allow()]` if clippy must be disabled.
- PREFER top-level imports over local imports or fully qualified names.
- AVOID shortening variable names (e.g., `version` not `ver`).
- The `uv-cli` crate must continue to compile cleanly under
  `cargo check -p uv-cli`.

## How your change will be evaluated

A test suite will:

- Invoke the rebuilt `target/debug/uv` binary as a subprocess with the
  argument lists `cache clear --help`, `cache clear --cache-dir <dir>`,
  `cache clean --help`, and `cache clean --cache-dir <dir>`, asserting
  on exit codes and on the equivalence of the two help outputs.
- Populate a temporary cache directory with a sentinel file, run
  `cache clear`, and assert the directory is empty afterwards.
- Run `cargo check -p uv-cli` and require it to succeed.
