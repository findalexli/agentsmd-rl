# Task: Fix Display v2 Formatting for Bare Aggregate Expressions

## Problem

When using Display v2 format strings with bare expressions like `{field_name}` (without an explicit transform like `:json` or `:str`), aggregate types (structs, enums, vectors) are incorrectly formatted using the `:str` transform, which often produces poor output or fails entirely. The formatter should implicitly apply the `:json` transform for aggregate types when no explicit transform is specified.

## Affected Code

The display formatting logic is in `crates/sui-display/src/v2/`:
- `parser.rs` - Defines the `Transform` enum
- `interpreter.rs` - Evaluates format expressions
- `writer.rs` - Writes formatted output
- `value.rs` - Value representation and atom formatting

## Expected Behavior

1. A bare expression like `{struct_field}` should produce JSON output when the field is a struct
2. A bare expression like `{enum_field}` should produce JSON output when the field is an enum
3. A bare expression like `{vector_field}` should produce JSON output when the field is a vector
4. Simple scalar values (addresses, bools, numbers, strings) should still use string formatting

## Example

For a struct `Inner { count: u64, label: String }`, the format string `"{inner}"` should produce:
```json
{"count": "42", "label": "hello"}
```

Not a string representation.

## What You Need To Do

1. Understand how the current transform handling works in the display formatter
2. Modify the `Transform` enum to support optional transforms
3. Update the writer logic to detect when no transform is specified and intelligently choose between JSON and string formatting based on the value type
4. Ensure scalar values (that can be converted to `Atom`) still get string formatting
5. Ensure the solution passes all existing tests and the repo's linting requirements

## Repo Guidelines

From CLAUDE.md:
- Run `cargo xclippy` after finishing changes
- Never use `#[allow(dead_code)]` or lint suppressions - fix underlying issues
- All unit tests must work properly
- Run `cargo check -p sui-display` and `cargo test -p sui-display --lib` to verify
