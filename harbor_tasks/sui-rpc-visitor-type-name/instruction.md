# RPC Visitor: Handle TypeName as String

## Problem

The RPC visitor in `sui-types` does not handle `0x1::type_name::TypeName` as a special string-like case. When a Move value of type `0x1::type_name::TypeName` is serialized in RPC outputs (gRPC, GraphQL, Display), it appears as a nested object with a `name` field rather than as a plain string. Other string-like Move types (`0x1::ascii::String`, `0x1::string::String`, `0x2::url::Url`) are already unwrapped in this way; TypeName should be treated consistently with them.

## Expected Behavior

After the fix, a `0x1::type_name::TypeName` value should serialize as a plain JSON string in RPC output, not as `{"name": "..."}`.

## Where to Look

The type layout for `0x1::type_name::TypeName` (with module `type_name`, struct name `TypeName`, address `0x1`, and a single field `name`) needs to be recognized in the special-case handling for string-like types in both `crates/sui-types/src/object/rpc_visitor/mod.rs` and `crates/sui-display/src/v2/value.rs`.

The pattern to follow is visible in how `move_ascii_str_layout()`, `move_utf8_str_layout()`, and `url_layout()` are used — each has a layout function in `base_types` that the special-case code calls. A corresponding layout function for TypeName should be added to `base_types` and then referenced in those two RPC/display modules.

## Verification

The sui-types library tests (`cargo test -p sui-types --lib`) and sui-display library tests (`cargo test -p sui-display --lib`) should all pass after the change.

Specifically, the RPC visitor tests for `json_ascii_string`, `json_utf8_string`, and `json_url` verify the pattern for string-like type handling and should continue to pass. The base_types unit tests and rpc_visitor JSON tests should also be green.

## Notes

- `TypeName` is defined in the Move standard library at `0x1::type_name::TypeName` with a single field `name` of type `0x1::ascii::String`.
- TypeName does not introduce a leading `0x` for hexadecimal addresses in its string representation.