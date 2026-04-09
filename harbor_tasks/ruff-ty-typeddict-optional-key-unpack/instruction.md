# [ty] Non-required TypedDict keys incorrectly satisfy required keys during unpacking

## Problem

When unpacking a `TypedDict` with non-required (optional) keys via `**kwargs` into a `TypedDict` constructor that requires those keys, `ty` does not report a `missing-typed-dict-key` error. For example:

```python
from typing import TypedDict

class MaybeName(TypedDict, total=False):
    name: str

class NeedsName(TypedDict):
    name: str

def f(maybe: MaybeName) -> NeedsName:
    return NeedsName(**maybe)  # ty incorrectly accepts this
```

Since `MaybeName` uses `total=False`, the `name` key may not be present at runtime. Unpacking it into `NeedsName(**maybe)` should flag that the required key `name` might be missing, but `ty` currently treats all keys from the source `TypedDict` as provided regardless of whether they are required or optional.

The same issue affects `NotRequired` individual fields — a `NotRequired[str]` field in the source should not satisfy a required field in the target during `**kwargs` unpacking.

## Expected Behavior

`ty` should emit a `missing-typed-dict-key` diagnostic when an optional/non-required key from the source `TypedDict` is the only source for a required key in the target `TypedDict` constructor.

## Files to Look At

- `crates/ty_python_semantic/src/types/typed_dict.rs` — TypedDict key extraction and validation logic for `**kwargs` unpacking
- `crates/ty_python_semantic/src/types/class.rs` — intersection type construction used during TypedDict key merging
- `crates/ty_python_semantic/resources/mdtest/typed_dict.md` — mdtest cases for TypedDict behavior
