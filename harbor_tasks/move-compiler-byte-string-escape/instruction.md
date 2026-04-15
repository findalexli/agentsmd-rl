# Fix Move Compiler Byte String Escape Handling

## Problem

The Move compiler's byte string parser has a bug when handling hex escape sequences that contain multi-byte UTF-8 characters. When the parser encounters a hex escape like `\xAñ` (where `ñ` is a multi-byte UTF-8 character), it incorrectly assumes certain error cases are unreachable and panics instead of producing a proper error message.

## Symptoms

- The compiler panics with an "ICE unexpected error parsing hex byte string value" message when processing byte strings containing multi-byte UTF-8 characters after hex escapes
- Example problematic input: `b"\xAñ"` in a Move module

## Expected Behavior

The compiler should:
1. Properly detect when non-ASCII hex digits appear in hex escape sequences
2. Report a clear error message — the exact string `"Invalid hexadecimal character"` — about the invalid hex character
3. Continue compilation to potentially report other errors

## Testing

You can test the fix by creating a Move file with:

```move
module 0x42::m {
    fun f(): vector<u8> {
        b"\xAñ"
    }
}
```

The compiler should produce a proper error message containing `"Invalid hexadecimal character"`, not panic.

## Verification Commands

After fixing the bug, verify with these commands:
- `cargo check -p move-compiler` — ensure the compiler builds
- `cargo test -p move-compiler --lib` — ensure existing unit tests still pass
- `cargo move-clippy -D warnings` — run linter
- `cargo xlint` — run custom linter
- `./scripts/git-checks.sh` — run git checks

The compiler must produce the error message `"Invalid hexadecimal character"` (exact string) for invalid hex characters, not panic.
