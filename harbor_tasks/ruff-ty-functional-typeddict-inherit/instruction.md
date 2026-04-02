# Bug: ty doesn't support class-based TypedDict inheriting from functional TypedDict

## Description

The `ty` type checker does not correctly handle the case where a class-based `TypedDict` inherits from a functional-form `TypedDict`. When a functional `TypedDict` is used as a base class for a class-based `TypedDict`, the fields from the functional parent are not recognized in the child class.

## Reproduction

```python
from typing import TypedDict

Base = TypedDict("Base", {"a": int}, total=False)

class Child(Base):
    b: str
    c: list[int]

child = Child(a=1, b="hello", c=[1, 2, 3])
```

Running `ty check` on this file produces incorrect errors. The type checker does not see the `a` field from `Base` as being part of `Child`, and `reveal_type(child["a"])` does not correctly resolve to `int`.

Additionally, when a class inherits from a functional `TypedDict` that is also decorated with `@dataclass`, the `invalid-dataclass` error should still be raised — but the inheritance itself should be recognized.

## Relevant Files

The TypedDict field inheritance logic is in `crates/ty_python_semantic/src/types/class/static_literal.rs`, specifically in the method that collects fields from the MRO (method resolution order). The type qualifier validation (e.g. `Required`/`NotRequired`) and `TypedDict` constructor validation live in `crates/ty_python_semantic/src/types/infer/builder.rs`. The `ClassType` helpers are in `crates/ty_python_semantic/src/types/class.rs`.

## Expected Behavior

- `Child` should inherit the `a` field from the functional `Base` TypedDict
- `reveal_type(child["a"])` should resolve to `int`
- Required/optional field semantics from the parent should be preserved
- The `invalid-dataclass` diagnostic should still fire for dataclasses inheriting from functional TypedDicts
