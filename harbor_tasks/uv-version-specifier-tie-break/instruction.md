# Normalize singular version-specifier intervals

You are working in a checkout of [astral-sh/uv](https://github.com/astral-sh/uv) at `/workspace/uv`.

## Symptom

`VersionSpecifiers` parses a comma-separated list of `Operator`+`Version`
specifiers (e.g. `>=1.4.4, <=1.4.4`). Two specifier strings that describe
the *same* set of versions but in different orderings should round-trip
to the same value.

Today they don't. Concretely, in `crates/uv-pep440`:

```rust
use std::str::FromStr;
use uv_pep440::VersionSpecifiers;

let lower_then_upper = VersionSpecifiers::from_str(">=1.4.4, <=1.4.4").unwrap();
let upper_then_lower = VersionSpecifiers::from_str("<=1.4.4, >=1.4.4").unwrap();

assert_eq!(lower_then_upper, upper_then_lower); // FAILS today
```

The two values compare unequal because the internal storage preserves the
original input ordering when both specifiers refer to the *same* version.
Operator equality is irrelevant — both sides describe the singleton
interval `{1.4.4}`, so they should be considered the same value.

## Expected behavior

After your fix:

1. Both orderings parse to *equal* `VersionSpecifiers` values.
2. The `Display` (`to_string()`) output of each is the canonical form
   `"<=1.4.4, >=1.4.4"` — i.e. when two specifiers share a version,
   the one whose operator sorts smaller comes first.
3. Specifiers whose versions are distinct keep their existing
   primary-by-version ordering. For example, both `">=1.0, <2.0"` and
   `"<2.0, >=1.0"` continue to render as `">=1.0, <2.0"`.

The same canonical-form rule must hold for any version, not just `1.4.4`
— for example, `">=2.0.0, <=2.0.0"` and `"<=2.0.0, >=2.0.0"` must both
display as `"<=2.0.0, >=2.0.0"`.

`Operator`'s existing `Ord` derivation already orders the comparator
operators in the way callers expect; you should rely on it rather than
inventing a new ordering.

## Scope

The fix is internal to the `uv-pep440` crate. You do not need to change
any other crate, run network-dependent tests, or modify tooling.

## Code Style Requirements

- The repo's CLAUDE.md applies to your changes:
  - Avoid `panic!`, `unreachable!`, `.unwrap()`, unsafe code, and clippy
    rule ignores.
  - Prefer `if let`, `match`, and let-chains over nested fallibility.
  - Prefer `#[expect(...)]` over `#[allow(...)]` when disabling clippy.
  - Prefer top-level `use` imports over local or fully-qualified paths.
  - Avoid shortening variable names (e.g. use `version` not `ver`,
    `operator` not `op`).
- `cargo check -p uv-pep440 --all-targets` and
  `cargo test -p uv-pep440 --lib` must keep passing.
- Always attempt to add a test case for the changed behavior in the
  `uv-pep440` crate's existing test module.
