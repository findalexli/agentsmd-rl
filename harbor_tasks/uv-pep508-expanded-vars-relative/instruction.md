# Treat PEP 508 URLs with expanded variables as relative

The `uv-pep508` crate provides `VerbatimUrl`, the Rust type used to represent
PEP 508 URLs (the URLs allowed after `name @ ` in dependency specifiers).
`VerbatimUrl` exposes a method:

```rust
pub fn was_given_absolute(&self) -> bool
```

It is supposed to indicate whether the *original* string the URL was parsed
from looked like an absolute path or absolute file URL. The result drives,
among other things, whether `uv` records a dependency in a lock file as an
absolute or relative path.

## The bug

`uv` permits PEP 508 URLs to contain `${VAR}` references that are expanded
against the process environment at parse time. Common shapes (taken from
real `pyproject.toml` files) are:

```text
b @ file://${PWD}/b
c @ file:///${PROJECT_ROOT}/c
```

After expansion, the URL string no longer contains the `${...}` reference
and may have become a syntactically absolute file URL — for example,
`file:///abs/path/foo`. As a result, `was_given_absolute()` currently
returns `true` for these URLs, which causes `uv lock` to record absolute
paths in the lock file and break workflows that rely on `${PWD}` /
`${PROJECT_ROOT}` to stay relative.

When the original given form contained an environment variable reference
that was successfully expanded, `was_given_absolute()` must return `false`,
even if the expanded URL would otherwise look absolute. This preserves the
relative-path semantics that users expect from `${PWD}` and
`${PROJECT_ROOT}`.

URLs that did *not* contain any expanded variable references must keep
their existing classification. In particular:

- A plain `file:///abs/path/foo` (no variables) must remain **absolute**.
- A `file:///abs/path/with$dollar/foo` where the literal `$` is **not** part
  of a `${NAME}` reference (and therefore nothing actually expanded) must
  remain **absolute**.
- A plain relative path like `./relative/path/foo` must remain
  **non-absolute** as before.

## API to be tested

The behavior is accessed through the `Pep508Url` trait's `parse_url`
method on `VerbatimUrl`:

```rust
use std::path::Path;
use uv_pep508::{Pep508Url, VerbatimUrl};

let url = <VerbatimUrl as Pep508Url>::parse_url(
    "file://${SOME_VAR}/foo",
    None, /* or Some(working_dir) */
)?;
let _ = url.was_given_absolute();
```

The crate must continue to compile both with default features and with the
`non-pep508-extensions` feature enabled. The grader will use both feature
configurations.

## Existing tests must keep passing

The crate's library unit tests (`cargo test -p uv-pep508 --lib`) and the
crate's compile checks (`cargo check -p uv-pep508 --tests` with and without
`--features non-pep508-extensions`) must continue to succeed.

## Code Style Requirements

This crate is part of the `uv` workspace. Follow the conventions from
`CLAUDE.md` at the repo root:

- Avoid `panic!`, `unreachable!`, `.unwrap()`, and unsafe code.
- Prefer patterns like `if let` and let chains over nested matches.
- Prefer `#[expect(...)]` over `#[allow(...)]` if a clippy lint must be
  silenced.
- The crate must continue to compile cleanly under `cargo check
  -p uv-pep508 --tests` (with and without the `non-pep508-extensions`
  feature) — i.e., no new compile errors from your edits.
- Do not change behavior unrelated to the regression described above.
