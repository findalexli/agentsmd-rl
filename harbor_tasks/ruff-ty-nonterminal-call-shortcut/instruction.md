# ty hangs on files with sequential TypeIs narrowing and match/assert_never

## Bug Report

When running `ty check` on Python files that combine sequential `TypeIs` narrowing
on large `Literal` union types with `match` statements using `assert_never`, the type
checker takes an extremely long time (minutes to hours) or appears to hang entirely.

## Reproduction

A file like the following triggers the issue:

```python
from typing import Literal, assert_never
from typing_extensions import TypeIs

Kind = Literal["a", "b", "c", ..., "z"]  # large union

def is_abc(t: Kind) -> TypeIs[Literal["a", "b", "c"]]:
    return t.startswith("a")

def is_def(t: Kind) -> TypeIs[Literal["d", "e", "f"]]:
    return t.startswith("d")

# ... more TypeIs guards ...

Action = Literal["act_one", "act_two", ..., "act_twenty"]

def process(kind: Kind, action: Action | None) -> str:
    if is_abc(kind):
        return "abc"
    if is_def(kind):
        return "def"
    # ... more narrowing calls with early returns ...

    match action:
        case "act_one":
            pass
        # ... more cases ...
        case _ as never:
            assert_never(never)
    return kind
```

The sequential `TypeIs` narrowing calls create many reachability constraints. Combined
with the `match`/`assert_never` pattern, this causes a combinatorial explosion in the
constraint evaluation.

## Relevant Code

The issue is in how `IsNonTerminalCall` predicates are evaluated in the reachability
constraint system:

- **`crates/ty_python_semantic/src/semantic_index/reachability_constraints.rs`** — The
  evaluation of `IsNonTerminalCall` predicates. Currently, every statement-level function
  call forces full type inference of the entire call expression to determine whether it
  could return `Never`. This is extremely expensive when there are many such calls.

- **`crates/ty_python_semantic/src/semantic_index/builder.rs`** — Where `IsNonTerminalCall`
  predicates are created for statement-level calls in function scopes (around line 2890+).

- **`crates/ty_python_semantic/src/semantic_index/predicate.rs`** — The `PredicateNode`
  enum and the `IsNonTerminalCall` variant definition.

- **`crates/ty_python_semantic/src/types/narrow.rs`** — Narrowing constraint builder that
  references `IsNonTerminalCall`.

## Expected Behavior

`ty check` on files with this pattern should complete in seconds, not minutes/hours. Most
statement-level function calls are obviously not `NoReturn` functions, so the system should
be able to determine this cheaply without inferring the full call expression type every time.

## Reference

See upstream issue: https://github.com/astral-sh/ty/issues/3120
