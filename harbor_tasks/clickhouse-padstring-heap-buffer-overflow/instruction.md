# Fix heap-buffer-overflow in leftPad/rightPad functions

The `leftPad` and `rightPad` string functions (and their UTF8 variants) trigger a
heap-buffer-overflow when called with ASan (Address Sanitizer) enabled.

## Symptom

ASan reports a heap-buffer-overflow read when running queries such as:

```sql
SELECT leftPad('x', 100, 'abcdefghijklmnopq');
SELECT rightPadUTF8('x', 50, 'абвгдежзиклмнопрс');
```

The crash occurs when the padding string must be copied multiple times to reach
the target length.

## Root Cause

The `writeSlice` utility internally calls `memcpySmallAllowReadWriteOverflow15`,
which reads up to 15 bytes beyond the end of the padding buffer. The current
implementation does not provide this extra padding, causing a heap-buffer-overflow
read.

## Task

Fix the heap-buffer-overflow in the pad-string implementation file. The fix must
preserve existing correct behavior for all valid inputs while ensuring the
padding buffer storage provides the extra read bytes that the internal copy
routine requires.

## Requirements

The implementation must satisfy the following requirements:

1. **The padding data storage must provide at least 15 extra bytes of read
   padding.** This is required by the internal memcpy routine. A standard
   byte array does not supply this; a specially padded buffer type does.

2. **Empty pad string argument defaults to a single space character** (`" "`).

3. **`numCharsInPadString` must use `.size()` for byte count**, not `.length()`.

4. **`appendTo` must call `pad_string.data()` directly** — the data pointer
   must be compatible with `writeSlice` without any type casting.

5. **Self-expansion of the pad string to ≥16 characters must use the appropriate
   method for the storage type**, not `+=` concatenation.

6. **Argument validation must use `validateFunctionArguments` with
   `FunctionArgumentDescriptors`** for `mandatory_args` and `optional_args`.
   Manual type-check throws and `NUMBER_OF_ARGUMENTS_DOESNT_MATCH` checks must
   be removed.

7. **`column_pad_const` must be validated with `chassert`** instead of throwing
   an exception, since the validator already guarantees a const column.

8. **`MAX_NEW_LENGTH` must use the digit separator** (C++14 feature):
   `1'000'000` instead of `1000000`.

9. **Include headers `<memory>` and `<DataTypes/IDataType.h>`**.

10. **Error message for argument 0 type mismatch must say** `"must be a
    String or FixedString"`.

11. **`void init()` method must be removed** — its logic should be inlined into
    the constructor, and empty-string handling moved to `executeImpl`.

12. **The constructor initialization list style** should use the form
    `: function_name(name_)` without the `is_right_pad_` and `is_utf8_` suffix.

13. **`utf8_offsets.reserve`** must be called with `pad_string.size() + 1`.

## Testing

After applying the fix, the following patterns should run without ASan errors:
- ASCII padding with various length patterns
- UTF8 padding with multi-byte characters
- Non-const data with `arrayJoin`
