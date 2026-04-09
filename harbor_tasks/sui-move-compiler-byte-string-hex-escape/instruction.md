# Fix Move Compiler Byte String Hex Escape Handling

## Problem

The Move compiler crashes with an internal compiler error (ICE) when encountering a multi-byte UTF-8 character in a hex escape sequence within a byte string literal.

For example, this code causes a panic:

```move
module 0x42::m {
    fun f(): vector<u8> {
        b"\xAñ"
    }
}
```

The error message shows:
```
unreachable!("ICE unexpected error parsing hex byte string value")
```

Instead of a proper error message, the compiler hits an "unreachable" code path and panics.

## Files to Modify

The issue is in the byte string parsing code:

- `external-crates/move/crates/move-compiler/src/expansion/byte_string.rs`

Look at the `decode_` function, specifically the handling of the `\x` escape sequence. The code currently assumes that any error from `hex::decode` other than `InvalidHexCharacter` is unreachable, but multi-byte UTF-8 characters (like `ñ`) can cause `OddLength` or `InvalidStringLength` errors.

## Expected Behavior

When the compiler encounters a multi-byte UTF-8 character in a hex escape position, it should:
1. NOT panic or hit unreachable code
2. Produce a proper compiler error (E01007) pointing to the invalid character
3. Continue compilation to report other errors if any

## Testing

The fix should handle cases like:
- `b"\xAñ"` - multi-byte character after hex digit
- `b"\xñA"` - multi-byte character as hex digit

While still allowing valid hex escapes like:
- `b"\xAB"` - valid two-digit hex escape

## Context

This is a Rust codebase using the standard Cargo workspace layout. The Move compiler is located in `external-crates/move/`. You can test your changes by running:

```bash
cd external-crates/move
cargo run -p move-compiler --bin move-build -- -f <test_file> -d
```

The compiler uses `hex::decode` from the `hex` crate to parse hex escapes. The issue is that the error handling for this function doesn't account for multi-byte UTF-8 characters being passed as hex digits.
