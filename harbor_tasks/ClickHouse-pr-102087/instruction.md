# Fix heap-buffer-overflow in leftPad/rightPad functions

## Problem

The `leftPad`, `rightPad`, `leftPadUTF8`, and `rightPadUTF8` string functions have a heap-buffer-overflow vulnerability that is detected by Address Sanitizer (ASan).

## Symptoms

- ASan reports a heap-buffer-overflow when running queries such as:
  - `SELECT leftPad('x', 100, 'abc')`
  - `SELECT rightPad('x', 50, 'абвгдежзиклмнопрс')` (UTF8 variant)
- The overflow is triggered inside the `writeSlice` function, which is called from `PaddingChars::appendTo` when appending padding characters to the result string.
- The crash occurs because `writeSlice` internally uses `memcpySmallAllowReadWriteOverflow15`, which reads up to 15 bytes past the end of the source buffer. The internal buffer that stores the padding characters does not provide this extra read margin, causing out-of-bounds reads when the pad string is short (fewer than 16 bytes) and gets repeated.
- The `appendTo` method currently uses `reinterpret_cast` to convert the pad string data pointer from `char*` (returned by `String::data()`) to `const UInt8 *` before passing it to `writeSlice`. The `reinterpret_cast` is necessary because the buffer type is `String`, but this conversion does not prevent the heap-buffer-overflow when the underlying buffer lacks adequate read padding.

## What needs to change

The internal buffer holding the padding characters must be stored in a container that guarantees at least 15 bytes of read padding beyond its logical size. The current container type (`String`) does not provide this guarantee. ClickHouse's `PaddedPODArray` family of containers does provide this padding and is used elsewhere in the codebase for exactly this purpose.

Additionally, review the surrounding code for related issues:
- The logic that defaults an empty pad string to a single space character should be placed so it runs before the padding buffer is constructed, not inside the buffer's own initialization (`PaddingChars::init()`).
- Consider whether the function's argument validation can be simplified using existing ClickHouse validation helpers.
- When the pad string buffer type changes, related code that interacts with `pad_string.data()` (such as the `reinterpret_cast` in `appendTo`) should be updated to work naturally with the new type.

## Code Style Requirements

- Use Allman-style braces (opening brace on a new line) for all C++ code.
- The modified code must be valid C++23 and pass `clang-18 -fsyntax-only` without syntax errors.
- Use `if constexpr (...)` for compile-time template-dependent branches where applicable.

## Notes

- The fix should maintain the same behavior for all edge cases (empty strings, UTF8, etc.)
- When writing C++ code, use Allman-style braces (opening brace on a new line)
- The expected output for test queries is provided in the existing SQL test files under `tests/queries/0_stateless/`
