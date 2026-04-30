# [ty] TypedDict Constructor Inference Issues

## Problem

The ty type checker has several issues with TypedDict constructor call validation:

1. **Duplicate diagnostics**: When a TypedDict constructor call contains an error referencing an undefined name as a keyword argument value (e.g., `TD(x=missing)`), ty emits the same `unresolved-reference` diagnostic message twice instead of once.

2. **String constant keys not recognized**: When constructing a TypedDict with a positional dict literal that uses `Final` string constants as keys (e.g., `Record({VALUE_KEY: "x"})` where `VALUE_KEY: Final = "value"`), ty fails to resolve the constant to its string value. This causes incorrect `error[...]` diagnostics (including `invalid-argument-type` when the value type doesn't match).

3. **Mixed dict + keyword args not fully validated**: When a TypedDict constructor call combines a positional dict literal with keyword arguments (e.g., `TD({"x": 1}, y="bar")`), ty does not properly validate the keyword arguments or count their keys as provided, leading to false `error[...]` diagnostics for missing required keys.

## Expected Behavior

- Each `unresolved-reference` diagnostic should be emitted exactly once, not duplicated
- `Final` string constants should be properly resolved when used as dict literal keys in TypedDict constructors; code using `Final` constants as keys should produce no `error[...]` diagnostics when the types match
- Mixed positional dict literal + keyword argument calls should validate both parts and combine their provided keys for required-key checking; valid mixed calls should produce no `error[...]` diagnostics
- Type mismatches through constant keys should be detected and reported as `invalid-argument-type` errors

## Testing

The following validation commands must pass for the `ty_python_semantic` crate:

- `cargo clippy -p ty_python_semantic -- -D warnings` — linting with warnings as errors
- `cargo fmt --check -p ty_python_semantic` — formatting check
- `cargo check -p ty_python_semantic --all-targets` — type check
- `cargo doc --no-deps -p ty_python_semantic` with `RUSTDOCFLAGS="-D warnings"` — documentation build
