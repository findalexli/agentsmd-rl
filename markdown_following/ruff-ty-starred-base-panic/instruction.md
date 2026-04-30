# ty: per-base lint checks panic on starred fixed-length-tuple bases

You are working in the `astral-sh/ruff` monorepo. This repository contains
both the Ruff linter/formatter and the ty type checker. ty's source lives
under `crates/ty_*` and reuses a number of `ruff_*` crates (parser, AST,
etc.).

## Bug

When ty type-checks a class whose bases include a starred unpack of a
fixed-length tuple, it panics. The minimal reproducer is:

```py
class StarredFinalBase(*(int, bool)): ...
```

Running `cargo run --bin ty -- check repro.py` against this file produces
output like:

```
error[panic]: Panicked at crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs:...:... when checking `repro.py`: `index out of bounds: the len is 1 but the index is 1`
info: This indicates a bug in ty.
```

and exits with code `101` (Rust's standard panic exit code).

The same panic is hit by every starred-tuple base — including starred
unpacks of named tuple variables — and across several per-base lint arms,
not just `subclass-of-final-class`. For example each of these should also
type-check without panicking:

```py
from typing import Generic, NamedTuple, Protocol

final_bases = (int, bool)
class InheritsFromFinalViaNamedStarred(*final_bases): ...

class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...

class ProtocolWithStarredBases(Protocol, *(int, str)): ...

class BareGenericInStarred(*(int, Generic)): ...
```

## Expected behaviour after the fix

For each of the reproducers above, ty must:

1. **Not panic.** No `error[panic]` line in the output, and the process must
   exit with a normal code (e.g. `0` for clean files, or `1` if lint
   diagnostics were reported) — never `101`.
2. **Emit the correct per-base lint for every unpacked element.** In
   particular:
   - For `class StarredFinalBase(*(int, bool)): ...` the
     `subclass-of-final-class` diagnostic must fire on the unpacked `bool`.
   - For `class InheritsFromFinalViaNamedStarred(*final_bases): ...` (where
     `final_bases = (int, bool)`) the `subclass-of-final-class` diagnostic
     must again fire on the unpacked `bool`.
   - For `class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...`
     the `invalid-named-tuple` diagnostic must fire on each unpacked
     non-`Generic[]` base.
   - For `class ProtocolWithStarredBases(Protocol, *(int, str)): ...` the
     `invalid-protocol` diagnostic must fire on each unpacked non-protocol
     base.
   - For `class BareGenericInStarred(*(int, Generic)): ...` the
     `invalid-base` diagnostic must fire on the unpacked plain `Generic`.
3. **Not regress any non-starred behaviour.** A direct `class
   D(bool): ...` must still produce the `subclass-of-final-class`
   diagnostic; an ordinary clean module must still type-check with exit
   code `0`.

## Hints about the cause

The per-base lint loop in `check_static_class_definitions` iterates over
the *expanded* bases list (which has one entry per unpacked element of a
starred base) but uses the loop index to look up the corresponding AST node
in `class_node.bases()`, which has one entry per *syntactic* base. When a
starred fixed-length tuple unpacks more than one element the expanded list
becomes longer than the AST list, and the indexing panics with
`index out of bounds`.

A related panic in the MRO error reporting was previously fixed by
introducing an `expanded_class_base_entries` helper that returns one entry
per unpacked element together with the source AST node it came from. The
per-base lint loop should use the same helper so that AST source-node
look-ups always line up with the iterated entries.

## Code Style Requirements

- The crate must continue to build cleanly: `cargo build --bin ty` from
  the repository root must succeed with no errors.
- Follow the existing code style in `crates/ty_python_semantic/`. In
  particular this codebase prefers `let` chains (`if let X = a && let Y =
  b && …`) over deeply nested `if let` blocks, and avoids `panic!` /
  `.unwrap()` when the constraint can be encoded in the type system.
- Rust imports go at the top of the file, never locally inside functions.
- Don't introduce ad-hoc `panic!` / `unreachable!` calls or wholly new
  lint paths — the fix should reuse the existing per-base abstractions.

## What to test

The grading harness runs `ty check` against each of the reproducers above
on the repository's freshly built debug binary. Your fix is graded on:

- No panic on any starred-tuple base case.
- The exact per-base lint kinds listed above (`subclass-of-final-class`,
  `invalid-named-tuple`, `invalid-protocol`, `invalid-base`) are reported
  for the unpacked elements.
- Direct (non-starred) inheritance and clean modules behave as before.
- `cargo build --bin ty` succeeds at the repository root.
