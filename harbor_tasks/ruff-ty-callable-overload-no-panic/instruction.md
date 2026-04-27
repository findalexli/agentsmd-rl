# Avoid panicking on overloaded `Callable` type context

## Repository

`ty` is the Python type checker that lives in this repository alongside Ruff.
The relevant crate for type inference is `ty_python_semantic`. The `ty` CLI
binary is built with `cargo build --bin ty` and lives at
`target/debug/ty`.

## Symptom

`ty` aborts with an internal panic on the following Python code:

```py
def _(x: bool):
    signatures = {
        "upper": str.upper,
        "lower": str.lower,
        "title": str.title,
    }

    f = signatures.get("", lambda x: x)
    reveal_type(f)
```

Running `target/debug/ty check <file.py>` produces a diagnostic at the
`error[panic]` severity, with the panic message:

```
``Callable` type annotations cannot be overloaded`
```

The process exits with status code `101`. The panic also fires on closely
related shapes — for example `dict.setdefault(key, lambda x: x)` against a
dict whose values are callables, or a single-key dict like
`{"u": str.upper}.get("u", lambda x: x)`.

## Expected behaviour

`ty check` must not panic on any of these inputs. It should complete normally
(exit code 0 if no other diagnostics, or non-zero only for ordinary
type errors that are not panics — never `error[panic]` and never exit 101).
The lambda's revealed type is permitted to be `(x) -> Unknown` in this case;
the requirement is simply that the type checker remains a non-panicking
function that produces a result.

## Where to look

The panic originates in the bidirectional-inference path for **lambda
expressions** inside `crates/ty_python_semantic`. The check that triggers it
is the assumption that a `Callable` type context resolves to exactly one
overload signature. When the resolved callable carries multiple overload
signatures (which happens whenever the lambda's target type comes from an
overloaded source such as `dict.get` / `dict.setdefault`), this assumption
breaks and the code calls `panic!`.

The fix is *not* to teach the inferencer to handle multi-overload contexts
fully — leave that as future work. The expectation is to gracefully fall
through (no extra type context for the lambda body) when more than one
overload is present, while preserving the existing behaviour for the
single-signature case.

## Validation

After your change, the repro above (and the variations listed under
"Symptom") must run cleanly through `target/debug/ty check`. Re-build with
`cargo build --bin ty` after edits.

## Code Style Requirements

This repository's `AGENTS.md` ships with several rules that bite on this
change:

- **Avoid `panic!`, `unreachable!`, `.unwrap()` patterns.** When you have to
  remove an existing `panic!`, replace it with logic that encodes the
  invariant in the type system or returns a graceful sentinel — do not
  silently swallow the case.
- **Prefer `let` chains** (`if let … && let …`) over nested `if let`
  statements where they reduce indentation.
- **No local imports inside functions.** Rust imports go at the top of the
  file.
- **Comments only when they explain a non-obvious "why"** — not what the code
  does. If you leave a TODO at the new fall-through, it should explain *why*
  the multi-overload case is deferred.
- **`uvx prek run -a`** is the project's pre-push hook; the diff must pass
  the workspace's existing `cargo check -p ty_python_semantic`.
