# Fix heap-buffer-overflow in leftPad/rightPad functions

## Symptom

The `leftPad` and `rightPad` string functions (and their UTF8 variants) trigger a
heap-buffer-overflow when called with ASan (Address Sanitizer) enabled. For example:

```sql
SELECT leftPad('x', 100, 'abcdefghijklmnopq');
SELECT rightPadUTF8('x', 50, 'абвгдежзиклмнопрс');
```

The crash occurs in the `PaddingChars` class when the padding string is used with
`writeSlice`, which internally calls `memcpySmallAllowReadWriteOverflow15`. This
routine reads up to 15 bytes beyond the end of the source buffer. The pad string
is currently stored as a `String` (`std::string`), which does not provide any extra
read padding beyond its allocated size.

## Task

Fix the heap-buffer-overflow by changing the pad string storage in the
`PaddingChars` class to a buffer type that provides at least 15 extra bytes of
read padding. ClickHouse's `PaddedPODArray` type is designed for exactly this
purpose. Adapt all code that interacts with the pad string member to be compatible
with the new storage type (e.g. `writeSlice` calls should not need
`reinterpret_cast` since the data pointer type will already match).

Additionally, improve the code quality:
- Replace manual argument validation logic with ClickHouse's standard argument
  validation helpers instead of manual type-checking throws
- Use debug assertions for conditions that are already guaranteed by prior
  validation rather than runtime exceptions
- Ensure error messages accurately reflect the accepted argument types (both
  `String` and `FixedString` are valid for the first argument)

## Testing

After applying the fix, the following patterns should run without ASan errors:
- ASCII padding with various length patterns
- UTF8 padding with multi-byte characters
- Non-const data with `arrayJoin`
