# Optimize UTF-8 String Decoding

## Problem

The oxc project's JavaScript deserializers use `TextDecoder` for UTF-8 string decoding from raw buffers. This is slower than `Buffer.prototype.utf8Slice`, which benchmarks show is ~5% faster.

## Goal

Replace `TextDecoder`-based UTF-8 decoding with `Buffer.prototype.utf8Slice` across the codebase.

## Files to Modify

1. **Rust code generator**: `tasks/ast_tools/src/generators/raw_transfer.rs`
2. **Generated JS files** (produced by the Rust generator):
   - `napi/parser/src-js/generated/deserialize/js.js`
   - `napi/parser/src-js/generated/deserialize/js_parent.js`
   - `napi/parser/src-js/generated/deserialize/js_range.js`
   - `napi/parser/src-js/generated/deserialize/js_range_parent.js`
   - `napi/parser/src-js/generated/deserialize/ts.js`
   - `napi/parser/src-js/generated/deserialize/ts_parent.js`
   - `napi/parser/src-js/generated/deserialize/ts_range.js`
   - `napi/parser/src-js/generated/deserialize/ts_range_parent.js`
   - `apps/oxlint/src-js/generated/deserialize.js`
3. **Direct implementation**: `apps/oxlint/src-js/plugins/source_code.ts`

## Required Patterns

After the fix, files must contain:

- **Rust generator**: Must use `utf8Slice, latin1Slice` destructured from `Buffer.prototype`; must use `utf8Slice.call(uint8, pos, end)` for string decoding; must not have `decodeStr` or `textDecoder` in the string deserializer body
- **Generated JS files**: Must contain `{ utf8Slice, latin1Slice } = Buffer.prototype`; must use `utf8Slice.call(uint8, pos, end)` for UTF-8 decoding; must not contain `new TextDecoder`, `decodeStr(`, or `textDecoder`
- **source_code.ts**: Must destructure `{ utf8Slice } = Buffer.prototype`; must use `utf8Slice.call(buffer, sourceStartPos, sourceStartPos + sourceByteLen)`; must not use `new TextDecoder` or `textDecoder`
- **Comments** in all files should reference `utf8Slice`, not `TextDecoder`

## Verification

After changes:
1. Rust generator compiles: `cargo check -p oxc_ast_tools`
2. Generated files contain the required patterns above
3. No `TextDecoder` or `decodeStr` remains in the string deserialization code

## Notes

- The `utf8Slice` method is available on `Buffer.prototype` in Node.js
- The change produces functionally equivalent output but faster
- The Rust generator (`raw_transfer.rs`) is the source of truth; the generated files are derived from it
- You may regenerate the JS files using `cargo run -p oxc_ast_tools` after modifying the Rust generator