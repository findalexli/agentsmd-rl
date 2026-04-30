# Heap-buffer-overflow in ClickHouse pad string functions

ClickHouse's `leftPad`, `rightPad`, `leftPadUTF8`, and `rightPadUTF8` SQL
functions trip an Address Sanitizer (ASan) heap-buffer-overflow when called
with a short pad string. The relevant implementation lives in
`src/Functions/padString.cpp`.

## Reproducing the symptom

A query of the form

```sql
SELECT leftPad('xxx', 10, 'ab');
```

triggers an ASan report: a read past the end of an allocated buffer inside
`PaddingChars::appendTo`, where the pad bytes are passed to `writeSlice`.
`writeSlice` ultimately calls `memcpySmallAllowReadWriteOverflow15`, which is
documented to read up to 15 bytes past the source buffer's logical end. The
container currently used for the pad bytes does not guarantee 15 bytes of
trailing readable padding, so the optimised copy walks off the end of the
allocation.

## What you need to deliver

Eliminate the ASan heap-buffer-overflow for the case above (and similar
small-pad-string cases) without regressing any existing behaviour, including
UTF-8 padding.

This file is also gated by ClickHouse's CI on a number of code-quality and
style checks. The list below describes what the project's reviewers and CI
will verify in the modified `src/Functions/padString.cpp`. Treat it as the
acceptance contract — each item is independently verified.

## Acceptance criteria for `src/Functions/padString.cpp`

### Memory-safety fix

- The code must satisfy the safety contract of `memcpySmallAllowReadWriteOverflow15`:
  the container that holds the pad bytes must guarantee at least 15 bytes of
  readable padding beyond its logical size. ClickHouse provides
  `PaddedPODArray<UInt8>` (from `<Common/PODArray.h>`) for this purpose.
  The `PaddedPODArray<UInt8> pad_string` member inside `PaddingChars` meets
  this contract.
- The repeated-pad expansion (which grows the pad sequence for SIMD-friendly
  copy sizes) must use the container's safe self-insertion path
  (`insertFromItself`) so that buffer ownership and padding invariants are
  preserved. The notation `pad_string += pad_string` is unsafe with the
  required container.
- `memcpySmallAllowReadWriteOverflow15` reads up to 15 bytes beyond the source
  pointer. The data pointer passed to `writeSlice` must come from a container
  whose `data()` method returns a `UInt8 *` directly. There must be no
  `reinterpret_cast<const UInt8 *>(pad_string.data())` casts when invoking
  `writeSlice` — `pad_string.data()` is passed directly.
- The empty-pad-string default (a single space) must be applied at the
  function's column-level entry point. When a query omits the pad string
  argument, the condition `if (pad_string.empty())` must be evaluated inside
  `executeImpl`.

### Argument validation refactor

- Per-argument type and arity checks must use the shared
  `validateFunctionArguments` helper driven by a
  `FunctionArgumentDescriptors` description of the mandatory and optional
  arguments. Both `validateFunctionArguments` and
  `FunctionArgumentDescriptors` must appear in the file.
- Once the validation is centralised through these helpers,
  `ILLEGAL_TYPE_OF_ARGUMENT` and `NUMBER_OF_ARGUMENTS_DOESNT_MATCH` must no
  longer be referenced from this file's `namespace ErrorCodes { … }` block
  (they remain valid elsewhere in the project — they just must not appear in
  this file's `ErrorCodes` block).

### Style / readability items the CI checks

- The early-return guard in `PaddingChars::appendTo` that handles no-op
  padding must use an explicit zero-comparison: `if (num_chars == 0)`.
- The `MAX_NEW_LENGTH` constant must use the C++14 digit separator for
  readability: `1'000'000`.
- `#include <memory>` must be present in the file.
- The class/method names `FunctionPadString`, `PaddingChars`, `executePad`,
  and `executeForSourceAndLength` must continue to exist (do not rename or
  remove them).
- UTF-8 support is preserved: the `utf8_offsets` member and the `is_utf8`
  template parameter remain in place, and UTF-8 padding behaviour is
  unchanged.

## Code Style Requirements

- The file must pass `clang-format --dry-run --Werror` against the
  repository's `.clang-format` (Allman braces — opening brace on its own
  line — and ClickHouse's existing rules).
- No tab characters anywhere in the file; spaces only.
- No trailing whitespace on any line.
- Braces, parentheses, and brackets remain balanced (the file must parse as
  valid C++).

## Out of scope

Modify only `src/Functions/padString.cpp`. Do not change tests, other
source files, the build system, or the `.clang-format` configuration.
