# RPC Visitor: Handle TypeName as String

## Problem

The RPC visitor in `sui-types` doesn't handle `0x1::type_name::TypeName` as a special case like it does for other "string-like" Move types. Currently, when a Move value of type `0x1::type_name::TypeName` is serialized in RPC outputs (gRPC, GraphQL, Display), it appears as an object with a nested `name` field containing the actual type string.

The desired behavior is to unwrap `TypeName` and represent it directly as its inner string value, similar to how `0x1::ascii::String`, `0x1::string::String`, and `0x2::url::Url` are handled.

## Files to Modify

The main files involved are:

1. **`crates/sui-types/src/base_types.rs`** - Add layout and constants for `TypeName`
   - Define `STD_TYPE_NAME_MODULE_NAME` and `STD_TYPE_NAME_STRUCT_NAME` constants
   - Define `RESOLVED_STD_TYPE_NAME` for the resolved type reference
   - Add `type_name_layout()` function returning the `MoveStructLayout` for TypeName

2. **`crates/sui-types/src/object/rpc_visitor/mod.rs`** - Add TypeName to special case handling
   - Import `type_name_layout` from base_types
   - Add `type_name_layout()` to the special case check that unwraps string-like types
   - Update the comment to include TypeName

3. **`crates/sui-display/src/v2/value.rs`** - Add TypeName handling in Display formatting
   - Import `type_name_layout` from sui_types::base_types
   - Add `type_name_layout()` to the list of layouts that get special Atom treatment
   - Add tests for TypeName handling in the test module

## Key Details

- `TypeName` is defined in the Move standard library at `0x1::type_name::TypeName`
- It has a single field `name` of type `0x1::ascii::String`
- For historical reasons, TypeName does NOT introduce a leading `0x` for hexadecimal addresses in its string representation
- The existing tests for `json_ascii_string`, `json_utf8_string`, and `json_url` show the pattern to follow

## Testing

Run the relevant crate tests:

```bash
# Test sui-types (especially the rpc_visitor tests)
cargo test -p sui-types --lib

# Test sui-display
cargo test -p sui-display --lib
```

The fix should make TypeName serialize as a plain JSON string instead of an object.
