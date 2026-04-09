# [ty] Fix signature help for ParamSpec-specialized class calls

## Problem

Signature help breaks when calling a ParamSpec-generic class constructor inside a subscript expression. For example, given:

```python
class A[**P]: ...

A[int,]()
```

The IDE signature help fails to correctly combine the display items with the semantics of the signature. The current implementation uses offset-based parameter label extraction from the signature string, which does not work for synthesized parameters like bare ParamSpec signatures.

Additionally:
- When calling a function typed as `Callable[P, None]`, bare ParamSpec parameters (rendered as `**P`) incorrectly appear as keyword argument completions. They should be excluded since they don't correspond to valid keyword arguments.
- Active parameter tracking does not correctly handle variadic parameters — when passing arguments beyond the formally-declared parameters into a bare ParamSpec, the active parameter index should remain on the variadic parameter rather than becoming `None`.

## Expected Behavior

- Signature help for ParamSpec-generic class constructors should render a correct signature label with properly tracked parameters.
- Bare ParamSpec parameters should not produce keyword argument completions.
- Active parameter tracking should keep variadic parameters active for any additional positional or keyword arguments.

## Files to Look At

- `crates/ty_ide/src/signature_help.rs` — builds signature help details for the IDE. The `create_signature_details_from_call_signature_details` function maps semantic call details into displayable `SignatureDetails`.
- `crates/ty_python_semantic/src/types/ide_support.rs` — provides `CallSignatureDetails` and parameter extraction. Currently stores parameter info as parallel arrays of offsets/names/kinds; this representation cannot handle synthesized parameters.
- `crates/ty_ide/src/completion.rs` — `add_function_arg_completions` filters parameters for argument completions. Needs to skip variadic and keyword-variadic parameters.
- `crates/ty_python_semantic/src/types/display.rs` — renders parameter lists including ParamSpec. The display formatting for ParamSpec parameters may need to emit structured detail information.
