# Bug: Functional `TypedDict` with mismatched name is silently accepted

## Summary

When creating a `TypedDict` using the functional form (e.g., `MyDict = TypedDict("SomeOtherName", {"key": str})`), the `ty` type checker does not raise a diagnostic when the string name passed to `TypedDict()` differs from the variable it's assigned to. According to the Python typing spec and conformance test suite, this should be an error.

## Reproduction

Create a Python file with:

```python
from typing import TypedDict

# This should be flagged — "WrongName" doesn't match "BadTypedDict"
BadTypedDict = TypedDict("WrongName", {"name": str})

# This is fine — names match
GoodTypedDict = TypedDict("GoodTypedDict", {"name": str})
```

Running `ty check` on this file should report a diagnostic for the mismatched case, but currently it silently accepts it.

## Relevant Code

The functional `TypedDict` construction is handled in:

- `crates/ty_python_semantic/src/types/infer/builder/typed_dict.rs`

Look at where the `name` argument is processed — the code extracts the string literal value and creates a `Name` from it, but does not compare it to the assigned variable's name.

The `definition` parameter already carries the variable name (accessible via the `name()` method on the definition), so the information needed for the check is available in scope.

## Expected Behavior

`ty` should emit an `invalid-argument-type` diagnostic when the string name passed to `TypedDict()` doesn't match the name of the variable it's being assigned to, similar to how `NamedTuple` name mismatches are handled.
