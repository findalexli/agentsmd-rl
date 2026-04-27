# ty: improve invariant matching of formal union vs inferable typevar

## Context

`ty` is the Python type checker that lives alongside Ruff in this repository
(crates prefixed with `ty_*`). It uses a constraint-solving approach for
generic type inference: when a generic class's constructor is called, the
solver visits each argument and incrementally builds a *specialization*
(a mapping from typevars to concrete types) by walking the formal type
against the actual type.

You can run the relevant test suite with:

```sh
cargo nextest run -p ty_python_semantic --test mdtest 'mdtest::call/constructor.md'
```

To isolate a single test inside a markdown fixture, set
`MDTEST_TEST_FILTER` to a substring of the section header:

```sh
MDTEST_TEST_FILTER="Generic constructor inference from overloaded" \
    cargo nextest run -p ty_python_semantic --test mdtest 'mdtest::call/constructor.md'
```

## The bug

Several mdtest cases in
`crates/ty_python_semantic/resources/mdtest/call/constructor.md` —
specifically those under the section
**"Generic constructor inference from overloaded `__init__` self types"** —
currently fail. Read those test cases; they describe the exact behavior the
fix must produce.

The pattern that breaks today is a generic class whose `__init__` overloads
remap the class typevar via the `self` annotation, where one of those
overloads uses a *union* containing a typevar — for example:

```py
T = TypeVar("T")
CT = TypeVar("CT")

class ClassSelector(Generic[T]):
    @overload
    def __init__(self: ClassSelector[CT], *, default: CT, class_: type[CT]) -> None: ...
    @overload
    def __init__(self: ClassSelector[CT | None], *, default: None = None, class_: type[CT]) -> None: ...
    def __init__(self, *, default=None, class_=None): ...
```

Calling `ClassSelector(class_=MyClass)` should pick the second overload and
infer `ClassSelector[MyClass | None]`. Today the solver leaves the
class-level typevar `T` unsolved and reveals the type as
`ClassSelector[T@ClassSelector]`, then reports a spurious
`invalid-argument-type` error because the inferred receiver type
(`ClassSelector[None]`, derived only from the `default=None` parameter)
disagrees with the expected union receiver type
(`ClassSelector[None | MyClass]`).

The same issue appears even without overloads — a single `__init__` whose
`self` annotation has the shape `Self[CT | None]` and that takes a `type[CT]`
parameter should infer `Self[CT | None]`, but currently leaves the class
typevar unsolved.

## What is expected

All of the assertions in the new section pass, including the
`# revealed: …` comments and the explicit-specialization error case
(`ClassSelector[int](class_=MyClass)  # error: [invalid-argument-type]`).
At the same time, every other constructor.md test, every
`mdtest::generics/legacy/*` test, and `cargo check -p ty_python_semantic
--tests` must keep succeeding — the fix should be narrow and not perturb
unrelated inference paths.

## Hints

- The bug lives in the constraint-solver path that walks a formal type
  against an actual type and accumulates per-typevar mappings. Look for
  the place where a formal *union* type is matched against an arbitrary
  actual type in *invariant* position.
- Think about what an invariant match means semantically: it is
  equality-like, not assignability-like. If the actual side is itself a
  bare inferable typevar, what should that typevar be bound to so the
  equation is consistent?
- Consider what happens if the solver descends into individual elements
  of the formal union when the actual is an unsolved typevar: a partial
  mapping might be recorded against a non-matching element (e.g. mapping
  `T` to `None` while `CT` is still being solved from another argument)
  and later block the correct solution.

## Code Style Requirements

This repository runs Clippy and follows the rules described in `AGENTS.md`
at the repository root. In particular:

- Prefer let chains (`if let` combined with `&&`) over nested `if let` /
  `match` blocks where it improves readability.
- Avoid `panic!`, `unreachable!`, and `.unwrap()`. Use exhaustive matching
  or propagate `Result`/`Option` instead.
- Place any new `use` statements at the top of the file, not inside
  functions.
- Use comments purposefully — don't narrate the code, but *do* explain
  why a non-obvious branch exists (especially if it is a guard against a
  subtle correctness hazard).
- Follow the surrounding match-arm style of the function you are editing
  (use the existing `add_type_mapping` helper, return `Ok(())` once the
  mapping is recorded, etc.).

The graders for this task verify both the behavioral fix (all the
mdtests pass and the crate still compiles) and a rubric drawn from
`AGENTS.md`.
