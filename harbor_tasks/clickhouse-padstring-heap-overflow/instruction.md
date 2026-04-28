# Heap-Buffer-Overflow in leftPad/rightPad Functions

## Problem Description

The `leftPad` and `rightPad` string functions in ClickHouse have a heap-buffer-overflow vulnerability detected by AddressSanitizer (ASan). The issue is in the `PaddingChars` helper class in the file `src/Functions/padString.cpp`.

## Symptom

When `leftPad` or `rightPad` is called with a custom pad string (more than a single character), ClickHouse triggers an ASan heap-buffer-overflow error. The crash occurs because the padding character storage type lacks the 15-byte readable memory padding required by `memcpySmallAllowReadWriteOverflow15`, which is called by `writeSlice` inside the `appendTo` method.

The pad string expansion loop that grows the pad string buffer to at least 16 bytes uses `+=` self-concatenation on the `pad_string` member. This approach is documented as incompatible with the memory-safe container types used elsewhere in ClickHouse.

When no pad string argument is provided (empty string), the padding should default to a space character. Currently this defaulting happens in a separate `init()` method rather than at the point of use in `executeImpl`.

Argument validation in `getReturnTypeImpl` uses manual type checking and throws exceptions with error codes `ILLEGAL_TYPE_OF_ARGUMENT` and `NUMBER_OF_ARGUMENTS_DOESNT_MATCH`. The project convention is to use the `validateFunctionArguments` helper with `FunctionArgumentDescriptors` for cleaner validation, and to use `chassert` for invariants that should hold after validation.

The `getReturnTypeImpl` signature uses the deprecated `DataTypes` parameter type; the codebase convention is `ColumnsWithTypeAndName`.

## Relevant Files

- `src/Functions/padString.cpp` — contains the `PaddingChars` class and `FunctionPadString` class
- `tests/queries/0_stateless/04070_pad_string_asan_overflow.sql` — test queries added by the original PR to verify the fix
- `tests/queries/0_stateless/04070_pad_string_asan_overflow.reference` — expected output for the test queries

The test file `04070_pad_string_asan_overflow.sql` exercises `leftPad`/`rightPad` with pad strings of various lengths (3, 9, 17, 25 characters) in both ASCII and UTF-8 modes (using `leftPadUTF8`/`rightPadUTF8`), including multi-byte characters from Cyrillic and Greek scripts. It also tests non-constant input data with multiple rows.

## Code Style Requirements

This project follows ClickHouse coding conventions documented in `AGENTS.md` and `.claude/CLAUDE.md`:

- **Allman brace style**: Opening braces go on a new line (not at end of line)
- **C++14 digit separators**: Large numeric literals (e.g., 1000000) should use digit separators (e.g., `1'000'000`)
- **Memory safety**: The ClickHouse codebase provides `PaddedPODArray<UInt8>` for storage that requires 15-byte read padding for `memcpySmallAllowReadWriteOverflow15`. Self-expansion of such containers should use `insertFromItself` rather than `+=`.
- **Member function conventions**: For `PaddedPODArray`, prefer `size()` over `length()` for consistency.
- **Explicit boolean comparisons**: Prefer explicit comparisons like `if (num_chars == 0)` over implicit `if (!num_chars)`.
- **Assertions**: Use `chassert` for debug assertions that verify invariants rather than throwing exceptions.
- **Argument validation**: Use `validateFunctionArguments` with `FunctionArgumentDescriptors` as the standard pattern for function argument type checking.
- **Includes**: Ensure all necessary headers are included (`<memory>` is needed when using certain standard library facilities).
- **WriteSlice**: `writeSlice` calls should pass `pad_string.data()` directly without `reinterpret_cast` when the data type matches.
- **No trailing whitespace, tabs, CRLF, duplicate includes, or more than 2 consecutive empty lines**: Standard CI style enforcement.

## Expected Behavior

After the fix:
- `leftPad`/`rightPad` with pad strings of any length (3, 9, 17, or 25+ characters) must not trigger ASan errors
- UTF-8 pad strings (`leftPadUTF8`/`rightPadUTF8`) with Cyrillic and Greek characters must work correctly
- Empty pad strings must default to a space character
- The test queries in `tests/queries/0_stateless/04070_pad_string_asan_overflow.sql` should produce output matching `tests/queries/0_stateless/04070_pad_string_asan_overflow.reference`
