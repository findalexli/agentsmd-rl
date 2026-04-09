# [ty] TypedDict Constructor Inference Issues

## Problem

The ty type checker has several issues with TypedDict constructor call validation:

1. **Duplicate diagnostics**: When a TypedDict constructor call contains an error (e.g., referencing an undefined name as a keyword argument value), ty emits the same diagnostic message twice. For example, `TD(x=missing)` produces two `unresolved-reference` errors instead of one.

2. **String constant keys not recognized**: When constructing a TypedDict with a positional dict literal that uses `Final` string constants as keys (e.g., `Record({VALUE_KEY: "x"})` where `VALUE_KEY: Final = "value"`), ty fails to resolve the constant to its string value and incorrectly reports errors.

3. **Mixed dict + keyword args not fully validated**: When a TypedDict constructor call combines a positional dict literal with keyword arguments (e.g., `TD({"x": 1}, y="bar")`), ty does not properly validate the keyword arguments or count their keys as provided, leading to false "missing required key" errors.

## Expected Behavior

- Each diagnostic should be emitted exactly once, not duplicated
- `Final` string constants should be properly resolved when used as dict literal keys in TypedDict constructors
- Mixed positional dict literal + keyword argument calls should validate both parts and combine their provided keys for required-key checking

## Files to Look At

- `crates/ty_python_semantic/src/types/infer/builder.rs` — type inference for call expressions, including how TypedDict constructor arguments are inferred and type-checked
- `crates/ty_python_semantic/src/types/typed_dict.rs` — TypedDict-specific validation logic for dict literal entries and keyword arguments
