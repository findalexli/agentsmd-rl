# Optimize UTF-8 String Decoding

## Problem

The oxc project's JavaScript deserializers use TextDecoder for UTF-8 string decoding from raw buffers. Benchmarks show Buffer.prototype methods are faster for this use case. The current implementation creates a TextDecoder instance and uses it for decode operations.

## Goal

Replace TextDecoder-based UTF-8 decoding with Buffer.prototype methods across the codebase.

## Files to Modify

1. **Rust code generator**: `tasks/ast_tools/src/generators/raw_transfer.rs`
   - This generates the JS deserializer files
2. **Generated JS files**: The deserializer files in:
   - `napi/parser/src-js/generated/deserialize/` (multiple files)
   - `apps/oxlint/src-js/generated/deserialize.js`
3. **Direct implementation**: `apps/oxlint/src-js/plugins/source_code.ts`

## Required Changes

### Rust Code Generator (`raw_transfer.rs`)

The string deserializer section currently uses TextDecoder for UTF-8 decoding. This should be updated to use Buffer.prototype methods available in Node.js instead.

### Generated JS Files

The generated deserializers currently use TextDecoder patterns for string decoding. After the fix, they should use Buffer.prototype methods for UTF-8 string decoding instead.

### source_code.ts

The source text initialization currently uses TextDecoder. After the fix, it should use Buffer.prototype methods.

## Verification

After changes:
1. Rust compiles: `cargo check -p oxc_ast_tools`
2. Generated files do not contain `new TextDecoder`, `decodeStr`, or `textDecoder` in string deserialization code
3. Run `cargo test -p oxc_ast_tools` to verify the generator works

## Notes

- `utf8Slice` and `latin1Slice` are built-in Buffer methods available in Node.js
- The change produces functionally equivalent output but faster
- The Rust generator (`raw_transfer.rs`) is the source of truth; run `cargo run -p oxc_ast_tools` to regenerate JS files

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
