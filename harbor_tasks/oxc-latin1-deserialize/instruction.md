# Optimize string deserialization in raw transfer

The string deserialization logic in the NAPI parser and oxlint has performance issues that need to be addressed.

## Problem

The current `deserializeStr` function in the generated deserializer files uses a suboptimal approach:

1. Uses `TextDecoder` for strings as short as 9 bytes - this threshold is too low, causing excessive C++ boundary crossings for medium-length strings
2. For shorter strings, performs slow byte-by-byte string concatenation instead of more efficient array-based approaches
3. Uses the JS string directly for ASCII substring extraction without leveraging Node.js Buffer optimizations for latin1 encoding

This causes excessive overhead when parsing JavaScript/TypeScript files with many short strings (identifiers, literals, etc.).

## Files to Modify

The source of truth is the generator:
- `tasks/ast_tools/src/generators/raw_transfer.rs` - The Rust code generator that produces the JS deserializers

The generator produces these files (which should NOT be edited directly):
- `apps/oxlint/src-js/generated/deserialize.js`
- `napi/parser/src-js/generated/deserialize/js.js`
- `napi/parser/src-js/generated/deserialize/js_parent.js`
- `napi/parser/src-js/generated/deserialize/js_range.js`
- `napi/parser/src-js/generated/deserialize/js_range_parent.js`
- `napi/parser/src-js/generated/deserialize/ts.js`
- `napi/parser/src-js/generated/deserialize/ts_parent.js`
- `napi/parser/src-js/generated/deserialize/ts_range.js`
- `napi/parser/src-js/generated/deserialize/ts_range_parent.js`

## Performance Issues to Address

### 1. TextDecoder threshold too low

The TextDecoder is invoked even for relatively short strings, causing overhead from crossing the JavaScript/native boundary. A significantly higher threshold would reduce this overhead for the common case of medium-length strings. The current threshold of 9 bytes should be increased substantially.

### 2. Inefficient string concatenation for non-source strings

When building strings that aren't part of the original source text, the current implementation uses slow per-character operations. A more efficient approach would batch the character code generation using pre-allocated arrays.

### 3. No latin1 slice optimization for source text

When the source file contains non-ASCII characters, the JS string cannot be used directly for latin1 byte extraction. The Buffer prototype provides an efficient method for extracting latin1-encoded substrings from byte buffers. This optimization should be extracted once per source file and used for ASCII string extraction.

### 4. Per-string array allocation overhead

Creating new arrays for character code operations on each string is wasteful. Pre-allocated reusable arrays would eliminate allocation overhead for repeated operations.

### 5. Incomplete buffer reset

When resetting the deserialization buffer, auxiliary variables holding source text derivatives should be cleared to allow garbage collection.

## Testing

After making changes:
1. The NAPI parser tests should pass: `cd napi/parser && pnpm test`
2. The optimized code should maintain correct string decoding for:
   - All-ASCII source files
   - Source files with non-ASCII characters (UTF-8)
   - Empty strings
   - Very long strings
   - Short strings in various positions

## Notes

- This is a performance optimization, not a bug fix - the current code works but is slow
- Focus on the generator (`raw_transfer.rs`) - the generated files will be recreated
- The optimization reduces overhead for the common case of ASCII-only JavaScript files