# Avoid panic on overloaded `Callable` type context in `ty`

You are working in the `ruff` workspace at `/workspace/ruff`. The
repository contains both the Ruff linter/formatter and the `ty` Python
type checker. The crates follow a naming convention: `ruff_*` for Ruff,
`ty_*` for ty. The bug below is in the type-context handling inside
`ty_python_semantic`.

## Symptom

`ty` performs *bidirectional* (expected-type-driven) inference for some
expressions — most relevantly, lambda bodies. When the expected type is
itself a `Callable`, ty extracts that callable's *signature* and uses it
as the type context for inferring the lambda parameters and body.

If the expected `Callable` type is **overloaded** (i.e. has more than
one signature in its `signatures().overloads` list), the current code
panics rather than gracefully falling back. The panic is a hard
`panic!` and crashes the type checker (and any consumer of it). It is
reachable from ordinary user code, e.g. the standard-library
`dict.get` which has three overloads in typeshed:

```python
def _(x: bool):
    signatures = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
    }
    f = signatures.get("", lambda x: x)
```

When ty type-checks the program above, it tries to use the inferred
type of the `default` parameter of `dict.get` as type context for the
`lambda x: x` expression. That parameter's type comes from an
overloaded `Callable`, and ty hits the panic instead of recovering.

## What you need to do

Fix the panic. The well-formed behaviour is: when the candidate
`Callable` type-context for a bidirectional-inference position has more
than one overload, ty should *gracefully decline* to use a callable
type-context for that position rather than crashing. Concretely, the
type-context machinery should be able to produce `None` (or its
moral equivalent) for the callable signature when the resolved
`Callable` annotation has zero or multiple overloads, and let the
caller proceed without bidirectional context.

Leave a short `TODO` note where the multi-overload case currently goes
unhandled — multi-inference for multiple overloads is a future
extension, similar to the existing TODO about multi-inference for
multiple `Callable` annotations in a union.

The fix is a small, localised change inside
`crates/ty_python_semantic/`. Do not introduce new public APIs or
helper modules.

## How to test

A regression mdtest will be added during grading. To run mdtest
locally for a single file (per `AGENTS.md`):

```sh
CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
    cargo nextest run -p ty_python_semantic --test mdtest -- mdtest::bidirectional
```

The pre-existing `bidirectional.md` mdtest must continue to pass after
your change.

## Code Style Requirements

This repository's `AGENTS.md` lays out development rules. The most
relevant ones for this task:

- **Try hard to avoid `panic!`, `unreachable!`, `.unwrap()`** — encode
  constraints in the type system instead. The fix here removes a
  `panic!` and should not introduce a new one.
- Follow existing code style. Check neighbouring files for patterns.
- Rust imports go at the top of the file, never locally in functions.
- Prefer `let` chains (`if let` combined with `&&`) over nested
  `if let` statements.
- Use comments purposefully. Don't narrate code; do explain non-obvious
  invariants or `TODO`s.
- The change must compile cleanly with `cargo check --tests -p
  ty_python_semantic`.

You do not need to run `cargo clippy` or `uvx prek run -a` for this
task — only the build and the mdtest must succeed.
