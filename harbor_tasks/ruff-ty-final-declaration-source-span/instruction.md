# Bug: ty diagnostics for invalid `Final` attribute assignments lack source annotation

## Summary

When `ty` reports an `invalid-assignment` error for assigning to a `Final` attribute, the diagnostic only shows the assignment site. It does not include a secondary annotation pointing back to where the attribute was originally declared as `Final`. This makes it harder for users to understand *why* the attribute is final, especially when the declaration is in a parent class or a different module.

## Reproduction

```python
from typing import Final

class C:
    x: Final[int] = 1

    def f(self):
        self.x = 2  # error: [invalid-assignment]
```

Running `ty check` on this file produces:

```
error[invalid-assignment]: Cannot assign to final attribute `x` on type `Self@f`
  --> src/example.py:7:9
   |
 6 |     def f(self):
 7 |         self.x = 2  # error: [invalid-assignment]
   |         ^^^^^^ `Final` attributes can only be assigned in the class body or `__init__`
```

The diagnostic does **not** point to line 4 (`x: Final[int] = 1`) where the attribute was declared as `Final`.

The same issue occurs for:
- Inherited `Final` attributes from a parent class
- `__init__` assignments when the attribute already has a value in the class body
- Cross-module `Final` attribute declarations

## Relevant Code

The diagnostic logic for final attribute assignments lives in:

- `crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs`

This file contains `report_final_instance_attribute_assignment` which emits the `invalid-assignment` diagnostic. There is a TODO comment acknowledging that the diagnostic should point to the `Final` declaration but doesn't yet.

To resolve the owning declaration, you may also need to look at:

- `crates/ty_python_semantic/src/types.rs` — the `nominal_class()` method on `Type`, which resolves the class that owns an attribute. Currently it doesn't handle all type variants.

## Expected Behavior

The `invalid-assignment` diagnostic should include a secondary annotation pointing to the `Final` declaration site, like:

```
error[invalid-assignment]: Cannot assign to final attribute `x` on type `Self@f`
  --> src/example.py:4:8
   |
 3 | class C:
 4 |     x: Final[int] = 1
   |        ---------- Attribute declared as `Final` here
 5 |
 6 |     def f(self):
 7 |         self.x = 2
   |         ^^^^^^ `Final` attributes can only be assigned in the class body or `__init__`
```

This should also work for inherited attributes, `__init__` reassignments, and cross-module declarations.
