# Reject functional `TypedDict()` with mismatched variable name (ty)

This repository contains both **Ruff** (Python linter/formatter) and **ty**
(Python type checker). Crates follow `ruff_*` and `ty_*` naming. The ty
binary lives at `crates/ty/src/main.rs` and you can run it during
development with `cargo run --bin ty -- check <file.py>` or directly via
`./target/debug/ty check <file.py>` after `cargo build --bin ty`.

## Background — functional `TypedDict`

PEP 589 and `typing(_extensions)` allow `TypedDict` to be created with a
*functional* call:

```py
from typing_extensions import TypedDict

Movie = TypedDict("Movie", {"title": str, "year": int})
```

By convention (and as required by `mypy` / `pyright`), the **first
positional argument** (the *typename* string literal) must equal the
**identifier the call is assigned to**. Otherwise the resulting type's
runtime `__name__` (`"Movie"`) silently differs from the binding it lives
under, and downstream tools that key off identity become unreliable.

## The bug

ty currently accepts a mismatched pair without complaint:

```py
from typing_extensions import TypedDict

# ty 0.0.x at base — silently accepted, no diagnostic
BadTypedDict3 = TypedDict("WrongName", {"name": str})
```

Running `cargo run --bin ty -- check the_file_above.py` exits 0 ("All
checks passed!"). It should not — `"WrongName"` is not the variable's
name (`BadTypedDict3`).

Sibling cases in the *same* code path are already handled. For example,
ty already rejects a non-string typename:

```py
# error[invalid-argument-type] — already diagnosed at base
Bad1 = TypedDict(123, {"name": str})
```

The mismatched-name case must be diagnosed in the same way.

## Required behavior

When ty encounters a functional-form `TypedDict(<string-literal>, <dict>)`
(or with `total=`/`closed=` kwargs) being assigned to a single variable,
and the string literal differs from that variable's identifier, ty must
emit a diagnostic with all of the following:

- **Rule / category:** `invalid-argument-type` (re-use the existing rule
  the sibling typename checks already use — do not invent a new one).
- **Message contents:** the diagnostic's primary message must mention
  *both* the offending typename string and the assigned-to variable
  identifier, so a user reading the output knows exactly which two names
  are out of sync. For the example
  `BadTypedDict3 = TypedDict("WrongName", {"name": str})` the message
  must contain both the literal `WrongName` and the literal
  `BadTypedDict3`.
- **Exit code:** `ty check` on a file containing the mismatch must exit
  non-zero (it currently exits 0).

## Cases that must continue to work

- `Movie = TypedDict("Movie", {"title": str, "year": int})` — names match,
  no name-mismatch diagnostic; ty must still exit 0 if no other errors.
- `Bad1 = TypedDict(123, {"name": str})` — non-string typename; the
  pre-existing `invalid-argument-type` diagnostic for the `typename`
  parameter must continue to fire.
- Trivial valid Python (no `TypedDict`) — ty must still pass cleanly.

## Cases the check should NOT apply to

The check is specifically about the *functional* `TypedDict("Name", ...)`
call form. The class-based form

```py
class Movie(TypedDict):
    title: str
    year: int
```

does not have an explicit string typename argument, so the check is
inapplicable there. Likewise, if the call is not bound to a single
plain-name target (e.g., the call appears as a sub-expression, in a
tuple-unpacking target, or has no assignment at all), there is no single
variable name to compare against and no diagnostic is required.

## Where to look

The functional-`TypedDict` argument validation already lives in the
`ty_python_semantic` crate, in the type inference builder code that
handles the `TypedDict(...)` call shape. The existing diagnostics for
`Bad1 = TypedDict(123, ...)`, `Bad2 = TypedDict("Bad2", "not a dict")`,
and `Bad3 = TypedDict("Bad3", {...}, total="not a bool")` are all emitted
from one place; the new check belongs alongside them, sharing the same
`INVALID_ARGUMENT_TYPE` lint and `report_lint(...).into_diagnostic(...)`
machinery.

You will need access to **the assignment target's name** at the point
where the typename argument is being checked. The semantic-model
`Definition` already exposes the binding's name; the existing
infrastructure should let you reach for it without new plumbing.

## Existing tests

The mdtest fixture for `TypedDict` lives at
`crates/ty_python_semantic/resources/mdtest/typed_dict.md`. The section
**"Function syntax with invalid arguments"** contains the sibling cases
listed above; that is the natural home for a new test asserting the
mismatched-name diagnostic.

To run only that mdtest file:

```sh
CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
  cargo nextest run -p ty_python_semantic -- mdtest::typed_dict
```

## Code Style Requirements

The repository's contributor guide (`AGENTS.md`) sets style constraints
that apply to this change. In particular:

- Avoid `panic!`, `unreachable!`, and `.unwrap()` in new code; encode
  invariants in the type system or handle the absent case explicitly.
- Prefer **let-chains** (`if let Some(x) = ... && cond && let Some(y) = ...`)
  over nested `if let` blocks. This check involves multiple optional
  lookups (the definition, the assigned identifier, the lint-builder) —
  compose them in a single chain.
- New `use` statements go at the top of the file, never locally inside
  functions.
- Reuse existing utilities (the existing `INVALID_ARGUMENT_TYPE` lint
  and `report_lint`/`into_diagnostic` flow). Don't introduce a new
  diagnostic plumbing path.
- Diagnostic messages are read on narrow terminals — keep the primary
  message concise.
- Do not narrate code with comments; only annotate non-obvious
  invariants.

You can lint your work with `cargo clippy --workspace --all-targets
--all-features -- -D warnings`.
