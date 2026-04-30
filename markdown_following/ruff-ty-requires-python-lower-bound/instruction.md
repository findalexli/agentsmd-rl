# [ty] Respect supported lower bounds from `requires-python`

## Problem

When a `pyproject.toml` specifies `requires-python` with an unusual version specifier, ty crashes with a panic. For example, setting `requires-python = "==2.7"` (a Python 2 version) or `requires-python = "==44.44"` (a far-future version) causes ty to panic during project metadata discovery instead of handling these cases gracefully.

This affects any project whose `requires-python` doesn't map to a version that ty natively supports (Python 3.7+).

## Expected Behavior

1. **For Python 2 specifiers** (e.g., `requires-python = "==2.7"`): ty should resolve to the lowest supported Python 3 version (3.7) without panicking. The exit code should not be 101 (Rust panic code) and output should not contain "panic".

2. **For unsupported future versions** (e.g., `requires-python = "==44.44"`): ty should produce a non-zero exit code and display a clear error message. The error message must contain either:
   - The word "supported", OR
   - The phrase "does not include"
   Example: "does not include any Python version supported by ty"

3. **Code style requirements** (per AGENTS.md guidelines):
   - Avoid using `.unwrap()`, `panic!()`, or `unreachable!()` patterns in the function handling requires-python resolution
   - Rust imports should always go at the top of files, never locally inside functions

## CI Requirements

After applying your fix, the following commands must pass:
- `cargo fmt --check` — code formatting
- `cargo check -p ty_project` — type checking
- `cargo clippy -p ty_project --all-targets --all-features` — linting

## Function to Modify

The `requires-python` resolution logic lives in the `crates/ty_project/src/metadata/pyproject.rs` file, in the function that resolves `requires-python` specifiers.

## Technical Context

The issue occurs during project metadata discovery when ty encounters a `requires-python` specifier that doesn't directly map to a supported Python version. Currently, ty only supports Python versions 3.7 and above. When processing version specifiers like `==2.7` or `==44.44`, the code should handle these gracefully rather than crashing.

## Error Message Requirements

When encountering a `requires-python` specifier that doesn't include any Python version supported by ty (such as `==44.44`), the error message must contain either:
- The word "supported" (e.g., "does not include any Python version supported by ty")
- The phrase "does not include"
