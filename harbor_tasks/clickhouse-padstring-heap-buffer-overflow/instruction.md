# Fix heap-buffer-overflow in leftPad/rightPad functions

## Symptom

The `leftPad` and `rightPad` string functions (and their UTF8 variants) trigger a
heap-buffer-overflow when called with ASan (Address Sanitizer) enabled. For example:

```sql
SELECT leftPad('x', 100, 'abcdefghijklmnopq');
SELECT rightPadUTF8('x', 50, 'абвгдежзиклмнопрс');
```

## Root Cause

The crash occurs in the `PaddingChars` class defined in the padString source file.

The class stores the padding string in a `String` member (`pad_string`), which is
`std::string`. When `writeSlice` calls `memcpySmallAllowReadWriteOverflow15`,
this routine reads up to 15 bytes beyond the end of the source buffer. `String`
(`std::string`) does not provide any extra read padding beyond its allocated size,
causing out-of-bounds reads.

Additionally, the `writeSlice` calls use `reinterpret_cast` on `pad_string.data()`.

## Issues to Address

Beyond the heap-buffer-overflow, the following problems exist in the same source file:

1. The argument validation logic uses manual type-checking throws with the
   `NUMBER_OF_ARGUMENTS_DOESNT_MATCH` error code. ClickHouse has standard helpers
   for function argument validation that should be used instead.

2. The error message for the first argument does not mention all accepted types.
   It should state "must be a String or FixedString" instead of only mentioning
   one type.

3. There is a redundant runtime check that throws `must be a constant string` for
   the third argument. This condition is already guaranteed by prior validation,
   so a debug assertion is more appropriate.

## Code Style Requirements

All changes must follow ClickHouse's code style:
- Use `size()` for containers that support it (not `length()`)
- Use digit separators in large numeric literals (e.g. `1'000'000`)
- Constructor initializer lists should have one member per line
- Include necessary headers for any new types used

## Testing

After applying the fix, the following patterns should run without ASan errors:
- ASCII padding with various length patterns
- UTF8 padding with multi-byte characters
- Non-const data with `arrayJoin`
