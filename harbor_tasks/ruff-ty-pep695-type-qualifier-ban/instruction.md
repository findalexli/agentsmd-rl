# Bug: ty silently accepts type qualifiers in PEP 695 type alias definitions

## Summary

The `ty` type checker does not flag an error when type qualifiers like `ClassVar`, `Final`, `Required`, `NotRequired`, `ReadOnly`, or `InitVar` are used on the right-hand side of a PEP 695 `type` alias statement. According to the typing spec, the RHS of `type X = ...` is a *type expression*, not an *annotation expression*, and type qualifiers are only valid in annotation expressions. `ty` already correctly rejects these qualifiers in PEP 613 (`TypeAlias`) aliases, but PEP 695 aliases are not covered.

## Reproduction

```python
from typing_extensions import ClassVar, Final, Required, NotRequired, ReadOnly
from dataclasses import InitVar

type Bad1 = ClassVar[str]    # should be an error, but ty accepts it
type Bad2 = ClassVar         # should be an error
type Bad3 = Final[int]       # should be an error
type Bad4 = Final            # should be an error
type Bad5 = Required[int]    # should be an error
type Bad6 = NotRequired[int] # should be an error
type Bad7 = ReadOnly[int]    # should be an error
type Bad8 = InitVar[int]     # should be an error
type Bad9 = InitVar          # should be an error
```

Running `ty check` on this file produces no diagnostics, but it should report `invalid-type-form` errors for each of these aliases.

## Relevant Code

The type alias inference logic is in:

- `crates/ty_python_semantic/src/types/infer/builder.rs` — look at `infer_type_alias`. This method handles PEP 695 `type X = ...` statements. The issue is in how it processes the RHS value expression — it currently treats the value as an annotation expression rather than a type expression. Compare with how PEP 613 aliases (using `TypeAlias`) are handled.

- `crates/ty_python_semantic/src/types/infer/builder/type_expression.rs` — the type expression inference code. Note that `InitVar` may need additional handling here since it might not yet be covered in type-expression context (even though other qualifiers like `ClassVar` and `Final` already are).

- `crates/ty_python_semantic/src/types.rs` — the `InvalidTypeExpression` enum and error formatting. If `InitVar` needs a new variant, this is where it would go.

## Expected Behavior

`ty` should report `invalid-type-form` diagnostics for all type qualifiers used in PEP 695 type alias definitions, with messages like:

> Type qualifier `typing.ClassVar` is not allowed in type expressions (only in annotation expressions)
