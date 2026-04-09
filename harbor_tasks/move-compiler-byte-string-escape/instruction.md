# Fix Move Compiler Byte String Escape Handling

## Problem

The Move compiler's byte string parser has a bug when handling hex escape sequences that contain multi-byte UTF-8 characters. When the parser encounters a hex escape like `\xAñ` (where `ñ` is a multi-byte UTF-8 character), it incorrectly assumes certain error cases are unreachable and panics instead of producing a proper error message.

## Symptoms

- The compiler panics with an "ICE unexpected error parsing hex byte string value" message when processing byte strings containing multi-byte UTF-8 characters after hex escapes
- The issue is in the byte string expansion code that handles `\x` hex escape sequences
- Example problematic input: `b"\xAñ"` in a Move module

## Location

The issue is in:
- `external-crates/move/crates/move-compiler/src/expansion/byte_string.rs`

Look for the code handling `'x'` character escapes in the `decode_` function.

## Expected Behavior

The compiler should:
1. Properly detect when non-ASCII hex digits appear in hex escape sequences
2. Report a clear error message about the invalid hex character
3. Continue compilation to potentially report other errors

## Current Behavior

The compiler panics because the code assumes certain `hex::FromHexError` variants (like `OddLength` or `InvalidStringLength`) cannot occur when parsing hex byte strings. However, these can occur when multi-byte UTF-8 characters are present.

## Testing

You can test the fix by creating a Move file with:

```move
module 0x42::m {
    fun f(): vector<u8> {
        b"\xAñ"
    }
}
```

The compiler should produce a proper error message, not panic.

## Agent Guidance

Consult the main `CLAUDE.md` file for repository conventions. Key points:
- Run `cargo check -p move-compiler` to verify compilation
- The fix should handle all `hex::FromHexError` variants properly
- Ensure existing unit tests still pass: `cargo test -p move-compiler --lib`
