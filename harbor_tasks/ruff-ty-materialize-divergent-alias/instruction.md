# ty crashes or produces incorrect types on recursive type aliases with Callable

## Bug description

When a recursive type alias wraps `TypeIs` or `TypeGuard` around a `Callable` that refers
back to the alias itself, ty's type resolution produces incorrect results. In some cases,
the type checker enters an infinite loop or crashes with a stack overflow.

The root cause is in the type materialization logic: when ty resolves types and encounters
an internal cycle marker during recursive alias resolution, the materialization step
incorrectly replaces the marker with a concrete type. This destroys the cycle-tracking
information that the resolver relies on to terminate, causing unbounded recursion.

A secondary symptom: in classes with multiple self-referential attributes forming cycles,
`reveal_type()` reports spurious type elements that shouldn't be present (e.g. extra
`Unknown` variants leaking into the inferred union).

## Reproduction

```python
from typing_extensions import TypeGuard, TypeIs
from collections.abc import Callable

# These recursive aliases wrap TypeIs/TypeGuard around Callable.
# ty should handle these without crashing.
type CallableIs = TypeIs[Callable[[], CallableIs]]
type CallableGuard = TypeGuard[Callable[[], CallableGuard]]
```

Running `ty check` on this file should complete without error. Currently, it either
crashes or fails to resolve the types correctly.

## Relevant code

The type mapping / materialization logic lives in `crates/ty_python_semantic/src/types.rs`.
Look for the `TypeMapping::Materialize` match arm — this is where the type-mapping
dispatch decides how to transform dynamic types during resolution. The issue is that
a specific internal cycle marker type is not being preserved during materialization.
