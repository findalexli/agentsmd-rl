# sui-display implicit :json transform feature

## Background

The `sui-display` crate provides display formatting for Move values. Display expressions can include a transform modifier (e.g., `:json`, `:hex`, `:bcs`) to change how values are rendered.

## Feature: Implicit :json Transform for Bare Expressions

When a display expression has **no explicit transform** (bare expression like `{st}` or `{en}`), and the value is a **struct or enum** (not a simple atom like address/u64), the system should automatically format the value as JSON.

This means:
- Bare struct expressions → JSON output
- Bare enum expressions → JSON output
- Atom expressions (address, bool, u8, etc.) remain as their native display form
- Values with explicit transforms (e.g., `{value:json}`) continue to work as before

## Files to Modify

- `crates/sui-display/src/v2/parser.rs` — Transform enum definition
- `crates/sui-display/src/v2/value.rs` — Strand::Value type, format_as_str method
- `crates/sui-display/src/v2/writer.rs` — write logic for handling None transform on atoms
- `crates/sui-display/src/v2/interpreter.rs` — how transform is passed through eval

## Expected Behaviors

### Transform Enum (parser.rs)
The `Transform` enum should not derive `Default`. The `Str` variant should not have a `#[default]` attribute.

### Strand::Value (value.rs)
The `transform` field in `Strand::Value` should be `Option<Transform>` (not plain `Transform`).

### Writer Logic (writer.rs)
When writing strand values:
- If `transform` is `None` AND the value is an atom → format using `format_as_str()` (native string representation)
- If `transform` is `None` AND the value is not an atom → format as JSON
- If `transform` is `Some(Transform::Json)` → format as JSON
- If `transform` is `Some(Transform::Str)` → format using `.unwrap_or(Transform::Str)` (default to Str transform)

The writer should use pattern matching with `None | Some(Transform::Json)` to detect JSON-eligible cases, and should check `transform.is_none()` when deciding how to format an atom.

### Interpreter (interpreter.rs)
The interpreter should pass `transform` through directly (via `*transform`) rather than calling `unwrap_or_default()`.

### format_as_str (value.rs)
The `format_as_str` method on `Atom` should be `pub(crate)` so the writer can use it.

### Unit Test (mod.rs)
A unit test named `test_format_single_bare_expression_falls_back_to_json` should exist that validates bare struct/enum expressions produce JSON output.

## Verification

Your implementation is correct if:
- `cargo check -p sui-display` passes
- `cargo clippy -p sui-display -- -D warnings` passes
- `cargo fmt --check -p sui-display` passes
- `cargo doc -p sui-display --no-deps` passes
- `cargo xlint` passes
- `cargo test -p sui-display --lib test_format_single_bare_expression_falls_back_to_json` shows "1 passed"
- `cargo test -p sui-display --lib` passes completely