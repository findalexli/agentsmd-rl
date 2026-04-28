# Fix the per-base lint panic in ty's static class definition checker

The ty type checker (under `crates/ty_python_semantic/`) crashes on a small
family of perfectly-valid (or invalidly-typed-but-still-parseable) Python
class definitions: any class whose `bases()` list contains a *starred
fixed-length tuple* and whose unpacked element list contains an item that
would normally produce a per-base lint diagnostic such as
`subclass-of-final-class`, `invalid-named-tuple`, `invalid-protocol`, or
`invalid-base`.

## Reproduction

Running `cargo build --bin ty` and then

```
ty check repro.py
```

with `repro.py` being any of

```python
class InheritsFromFinalViaStarred(*(int, bool)): ...

final_bases = (int, bool)
class InheritsFromFinalViaNamedStarred(*final_bases): ...

from typing import NamedTuple
class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...

from typing import Protocol
class ProtocolWithStarredBases(Protocol, *(int, str)): ...

from typing import Generic
class BareGenericInStarred(*(int, Generic)): ...
```

is expected to print regular ty diagnostics. Instead, ty panics in the
`SUBCLASS_OF_FINAL_CLASS`/`INVALID_NAMED_TUPLE`/`INVALID_PROTOCOL`/`INVALID_BASE`
arms of the per-base lint loop with an out-of-bounds index error similar to

```
panicked at ...: index out of bounds: the len is 1 but the index is 1
```

## Expected behaviour

After the fix, **none of the inputs above may cause ty to panic.** Each
input must instead produce the per-base diagnostic that the user would
expect for the unpacked entries of the starred tuple:

| Input                                                              | Expected diagnostic       |
| ------------------------------------------------------------------ | ------------------------- |
| `class X(*(int, bool)): ...`                                       | `subclass-of-final-class` |
| `final_bases = (int, bool); class X(*final_bases): ...`            | `subclass-of-final-class` |
| `class N(NamedTuple, *(int, str)): ...`                            | `invalid-named-tuple`     |
| `class P(Protocol, *(int, str)): ...`                              | `invalid-protocol`        |
| `class X(*(int, Generic)): ...`                                    | `invalid-base`            |

The diagnostic-rule names above are the lint identifiers ty uses (the
literal strings that appear in the rendered diagnostic, e.g.
`error[subclass-of-final-class]`).

Pre-existing behaviour for *non-starred* class definitions must be
unchanged. In particular, a plain final-class subclass like
`class FinalChild(bool): ...` must still produce
`subclass-of-final-class`; vanilla class definitions like
`class A: ...; class B(A): ...` must still produce no diagnostics.

## Where to look

The panic originates from the per-base lint loop inside
`check_static_class_definitions` (in the static class inference builder).
The loop iterates over the class's *expanded* bases list (which unpacks
fixed-length starred tuples), but the diagnostic source span is fetched
by indexing back into the un-expanded `class_node.bases()` AST list with
the same loop index. When a starred tuple has been unpacked, the two
lists have different lengths, and the index is out of bounds.

A previous, closely related panic in the MRO error reporting arms of
the same function (`StaticMroErrorKind::DuplicateBases` / `InvalidBases`)
has already been fixed in this codebase. Reading how those arms now
obtain a source span for an entry of the *expanded* base list is a
useful starting point — the right shape of fix exists elsewhere in the
same function.

## Testing

The repository's mdtest suite covers per-base diagnostics in the MRO
diagnostics test file. Add coverage for the
starred-tuple cases above to that file (under a sensible new section) so
that the mdtest framework asserts the diagnostics are emitted without a
panic. Per AGENTS.md:

> All changes must be tested. If you're not testing your changes, you're
> not done.

You can run the affected mdtest with:

```
CARGO_PROFILE_DEV_OPT_LEVEL=1 INSTA_FORCE_PASS=1 INSTA_UPDATE=always \
  cargo nextest run -p ty_python_semantic -- mdtest::mro
```

## Style requirements

- Imports must go at the top of the file (no local imports inside
  functions).
- Prefer let chains (`if let ... && let Some(...) = ...`) over nested
  `if let` blocks where applicable.
- Avoid `panic!`, `unreachable!`, and `.unwrap()` / `.expect()` on values
  whose absence is reachable. The whole bug is an indexing-based panic;
  the fix should encode the pairing invariant in the iteration value
  rather than re-introducing a different unchecked lookup.
- Use comments purposefully — to explain invariants or unusual choices,
  not to narrate code.
- Reuse existing utilities rather than introducing a new abstraction
  parallel to one already in the codebase.

You do **not** need to run `cargo dev generate-all`, `uvx prek run -a`,
or any other tooling that touches schemas / docs / lockfiles for this
change.
