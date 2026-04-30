# Preserve end-of-line comments when removing dependencies

You are working in the [astral-sh/uv](https://github.com/astral-sh/uv) repository at `/workspace/uv`.
The repo is a Rust workspace; the relevant crate is `uv-workspace`.

## Bug

When `uv remove <name>` is invoked on a `pyproject.toml`, the helper that
performs the removal drops trailing/inline comments that belong to *adjacent*
dependency entries. Concretely, given

```toml
[project]
dependencies = [
    "numpy>=2.4.3", # essential comment
    "requests>=2.32.5",
]
```

removing `requests` currently produces

```toml
[project]
dependencies = [
    "numpy>=2.4.3",
]
```

— the end-of-line comment `# essential comment` on the `numpy` line has been
silently lost. The expected output preserves the comment:

```toml
[project]
dependencies = [
    "numpy>=2.4.3", # essential comment
]
```

## Why this happens

`toml_edit` represents inline (end-of-line) comments by attaching them to the
*prefix decoration* of the **following** array item, not to the item the
comment visually belongs to. So in the example above, the comment
`# essential comment` is stored on the `requests` entry's prefix. When
`requests` is removed naively, that prefix decoration — and therefore the
comment — disappears with it.

## Required behavior

The removal logic must, before deleting an item, transfer that item's prefix
decoration so the comment survives. Specifically:

1. **Inline comment on the previous line.** Removing an item whose prefix
   carries a comment that visually belongs to the *previous* line must leave
   that comment attached to the previous line, character-for-character.
   (`"numpy>=2.4.3", # essential comment` must remain a single line, with
   the comma-space-hash spacing preserved.)

2. **Inline comment on the removed line itself.** When the removed item *itself*
   carries an inline comment and is in the middle of the array, that comment
   must remain in the output (it may be repositioned to its own line by the
   array's reformatter, but the text of the comment must not be lost).

3. **Own-line comment above the removed item.** If a standalone comment line
   sits immediately above the removed item, that comment must be retained in
   the output.

4. **Multiple adjacent matches.** When several adjacent entries match and are
   all removed (e.g. two consecutive `typing-extensions` lines with markers),
   any inline comments that belong to surrounding entries must keep their
   original line ordering — the comment that was first in the source must
   still appear first in the output.

5. **Comment on the last entry.** If the *last* item in the array is removed
   and its prefix carries a comment, that comment must be preserved in the
   array's trailing decoration so it is not dropped.

Your fix should live in the `remove_dependency` helper in
`crates/uv-workspace/src/pyproject_mut.rs`. You may edit only this file —
the test suite exercises the public `PyProjectTomlMut::remove_dependency`
API, which delegates to that helper.

The bug is tracked at <https://github.com/astral-sh/uv/issues/18555>.

## Code Style Requirements

This crate is checked with the standard Rust toolchain. Your change must
compile cleanly under `cargo check -p uv-workspace --lib` with no warnings
or errors. Per the repository's `CLAUDE.md`:

- Avoid `panic!`, `unreachable!`, `.unwrap()`, unsafe code, and `#[allow(...)]`.
- Prefer `if let` (and let-chains, e.g. `if let Some(x) = ... && cond`) for
  fallibility over nested matches or unwraps.
- Prefer top-level imports over local imports or fully-qualified names.
- Avoid shortening variable names (e.g. use `prefix`, not `pfx`).

## Verification

You can iterate locally with the existing pre-existing unit tests:

```
cargo test -p uv-workspace --lib pyproject_mut::test
```

The grader will additionally exercise the public
`PyProjectTomlMut::remove_dependency` API on inputs covering each of the
behaviors above.
