# ty: reject functional `TypedDict()` calls with mismatched name

## Background

In Python's typing system, [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict) supports a *functional* form:

```python
from typing import TypedDict

Movie = TypedDict("Movie", {"name": str, "year": int})
```

The *first argument* (the typename) must equal the name of the variable the
result is assigned to. The Python typing conformance test suite expects type
checkers to report a diagnostic when this invariant is violated.

`ty` (the type checker that lives in this repository, under `crates/ty*`) is
currently missing that check. Given:

```python
from typing import TypedDict

BadTypedDict3 = TypedDict("WrongName", {"name": str})
```

`ty check` exits without complaint about the name mismatch. It should produce
an error.

## What you need to make true

When `ty check` is run on a Python file containing a functional
`TypedDict(...)` call whose **string-literal first argument differs from the
variable the call's result is assigned to**, `ty` must emit a diagnostic with
all of the following properties:

1. **Lint code:** the diagnostic is reported under the existing
   `invalid-argument-type` lint (not a new lint code).

2. **Message contains the canonical phrase:** the diagnostic message must
   include, verbatim, the substring:

   ```
   must match the name of the variable it is assigned to
   ```

3. **Message names both identifiers:** the message must mention *both* the
   literal string typename **and** the assigned variable name, so that the
   user can see which is which. For example, for
   `BadTypedDict3 = TypedDict("WrongName", {"name": str})` the diagnostic
   output must contain both the string `WrongName` *and* the string
   `BadTypedDict3`.

4. **Coverage:** the check must apply equally to `typing.TypedDict` and to
   `typing_extensions.TypedDict` (both are commonly used in real code).

5. **No over-firing:**
   - `Good = TypedDict("Good", {...})` (matching names) must NOT produce a
     name-mismatch diagnostic.
   - Source files that contain no `TypedDict` calls must not produce any
     `TypedDict`-related diagnostic from this new check.

6. **No regressions:** the pre-existing diagnostic for a non-string typename
   argument (e.g. `Bad1 = TypedDict(123, {"name": str})`) must continue to
   fire — your change should not replace or short-circuit that path.

## Where the change belongs

The functional-`TypedDict` handling lives in the `ty_python_semantic` crate
(under `crates/ty_python_semantic/src/types/...`). You will need to look at
how the typename argument is currently inferred from a string literal and add
the comparison against the assigned variable's name there. mdtest coverage
for `TypedDict` lives under
`crates/ty_python_semantic/resources/mdtest/typed_dict.md`.

## Project conventions

This repository ships an `AGENTS.md` that applies to any change here. Some
points particularly relevant to this task:

- All changes must be tested. Prefer adding a new mdtest line in the
  existing `typed_dict.md` over creating a new file.
- Avoid `panic!`, `unreachable!`, and `.unwrap()`. Encode invariants in the
  type system instead.
- Prefer let-chains (`if let ... && let ... && ...`) over nested `if let`
  blocks.
- Rust imports always go at the top of the file, never inside a function.
- ty error messages should be concise — readable on a narrow terminal under
  `--output-format=concise`.
- Use comments to explain *why*, not to narrate *what*.
