# ty wrongly treats `dataclasses.field()` as special outside dataclass context

## Problem

The `ty` type checker incorrectly special-cases `dataclasses.field()` calls even when they appear in classes decorated with `@dataclass_transform()` that do NOT list `field` in their `field_specifiers`. This causes `ty` to treat `field(init=False)` as removing the field from the constructor (making it required), when it should actually treat the entire `field(...)` expression as an ordinary default value for that field.

Concretely, given:

```python
@dataclass_transform()
def create_model(*, init: bool = True):
    ...

@create_model()
class A:
    name: str = field(init=False)
```

`ty` incorrectly infers `A.__init__` as `(self: A, name: str) -> None` (name required), so `A()` produces a missing-argument error. The correct inference is `(self: A, name: str = ...) -> None` (name has a default), so both `A()` and `A(name="foo")` should be valid.

The same bug also manifests when `dataclass_transform` specifies *other* field specifiers (e.g., a custom `other_field` function) — `dataclasses.field()` is still wrongly treated as special even though it's not in the `field_specifiers` list.

## Expected Behavior

- `dataclasses.field()` should only be treated as a special field specifier when it is explicitly listed in `field_specifiers` of the active `dataclass_transform` (or when using stdlib `@dataclass`, which implicitly includes it).
- When `field()` is NOT listed in `field_specifiers`, it should be treated as an ordinary default value expression.
- The stdlib `@dataclass` behavior must remain unchanged — `field(init=False)` should still remove the parameter from `__init__`.

## Files to Look At

- `crates/ty_python_semantic/src/types/call/bind.rs` — function call binding logic that determines how `field()` calls are handled during constructor synthesis
- `crates/ty_python_semantic/src/types/class/static_literal.rs` — static class literal analysis that processes field specifiers and determines field properties (init, kw_only, alias, converter)
