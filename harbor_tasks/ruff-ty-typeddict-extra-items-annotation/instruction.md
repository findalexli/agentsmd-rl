# [ty] Infer `extra_items` keyword in class-based TypedDicts as an annotation expression

## Problem

The `ty` type checker does not properly validate the `extra_items` keyword argument in class-based TypedDict definitions. Currently, `extra_items` is inferred as a regular expression rather than as a type annotation, which means:

1. **Invalid type qualifiers are silently accepted.** For example, `class TD(TypedDict, extra_items=Required[int])` does not produce any error, even though `Required` and `NotRequired` are not valid qualifiers for `extra_items` (only `ReadOnly` is). The same applies to `ClassVar`, `Final`, and `InitVar`.

2. **Forward references in `extra_items` are not handled correctly.** Stringified forward references like `extra_items="Foo | None"` are not resolved as type annotations, and self-referential forward references in stub files do not work.

## Expected Behavior

When the `ty` checker validates a class-based TypedDict definition:

- The `extra_items` keyword should be treated as a **type annotation expression** (not a regular expression).
- Invalid type qualifiers in `extra_items` must produce an `invalid-type-form` diagnostic. Specifically, these qualifiers are NOT valid in `extra_items`:
  - `Required[...]`
  - `NotRequired[...]`
  - `ClassVar[...]`
  - `Final[...]`
  - `InitVar[...]`
- `ReadOnly[...]` should remain valid in `extra_items` and must NOT produce an `invalid-type-form` diagnostic.
- Plain type annotations (e.g., `extra_items=int`) should also be accepted without producing an `invalid-type-form` diagnostic.
- Forward references (stringified in `.py` files, bare in `.pyi` stub files) should be properly resolved.
- For non-`typing.TypedDict` classes that happen to accept an `extra_items` keyword, the value should continue to be treated as a regular expression, not a type annotation.

## How to Verify

Run `ty check` on code like:

```python
from typing_extensions import TypedDict, Required, NotRequired, ClassVar, Final, ReadOnly

# Should produce 'invalid-type-form' error
class Bad1(TypedDict, extra_items=Required[int]):
    name: str

# Should produce 'invalid-type-form' error
class Bad2(TypedDict, extra_items=NotRequired[str]):
    x: int

# Should produce 'invalid-type-form' error
class Bad3(TypedDict, extra_items=ClassVar[int]):
    label: str

# Should produce 'invalid-type-form' error
class Bad4(TypedDict, extra_items=Final[int]):
    key: str

# Should NOT produce 'invalid-type-form' error (plain type)
class Good1(TypedDict, extra_items=int):
    name: str

# Should NOT produce 'invalid-type-form' error (ReadOnly is valid)
class Good2(TypedDict, extra_items=ReadOnly[int]):
    name: str
```

Additionally, update the TypedDict markdown test cases to reflect the new behavior for `extra_items` validation, including tests for `ClassVar` and `InitVar` which should also trigger `invalid-type-form` errors.
