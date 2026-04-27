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
style checks. The list below describes everything the project's reviewers and
CI will look for in your modified `src/Functions/padString.cpp`. Treat it as
the acceptance contract for the change — the implementation shape is up to
you, but each item is independently verified.

## Acceptance criteria for `src/Functions/padString.cpp`

### Memory-safety fix

- The container that backs the pad string inside `class PaddingChars` must
  expose at least 15 bytes of safe trailing read padding, as required by
  `memcpySmallAllowReadWriteOverflow15`. In ClickHouse the canonical
  container with that guarantee is `PaddedPODArray<UInt8>` (declared in
  `<Common/PODArray.h>`). The `pad_string` member of `PaddingChars` is
  expected to be of type `PaddedPODArray<UInt8>`.
- The repeated-pad expansion loop (which doubles the pad sequence until it
  reaches the SIMD-friendly threshold) must extend the buffer through the
  container's own `insertFromItself` method rather than the previous
  `pad_string += pad_string` `String` concatenation.
- The container's `data()` already returns a `UInt8 *`, so the
  `reinterpret_cast<const UInt8 *>(pad_string.data())` casts inside
  `appendTo` must no longer appear; `pad_string.data()` is passed directly
  to `writeSlice`.
- The "empty pad string defaults to a single space" rule belongs in the
  function's column-level entry point, `executeImpl`, not in the
  `PaddingChars` initialisation. After your change, the literal check
  `if (pad_string.empty())` must appear inside `executeImpl`.

### Argument validation refactor

- The hand-rolled per-argument type/arity checks in `getReturnTypeImpl` are
  replaced by a single call to the shared `validateFunctionArguments`
  helper, driven by a `FunctionArgumentDescriptors` description of the
  mandatory and optional arguments. Both `validateFunctionArguments` and
  `FunctionArgumentDescriptors` must appear in the file.
- Once that refactor lands, `ILLEGAL_TYPE_OF_ARGUMENT` and
  `NUMBER_OF_ARGUMENTS_DOESNT_MATCH` are no longer thrown from this
  translation unit. Their `extern const int …;` declarations must be
  removed from the file's `namespace ErrorCodes { … }` block (they may
  still exist elsewhere in the project — but not in this file's
  `ErrorCodes` block).

### Style / readability items the CI checks

- The early-return guard in `PaddingChars::appendTo` that handles "no
  characters to pad" must use an explicit comparison, written exactly as
  `if (num_chars == 0)`.
- The `MAX_NEW_LENGTH` constant must be written with the C++14 digit
  separator: `1'000'000`.
- `#include <memory>` must be present at the top of the file.
- The class/method names `FunctionPadString`, `PaddingChars`, `executePad`,
  and `executeForSourceAndLength` must continue to exist (do not rename or
  remove them).
- UTF-8 support is preserved: the `utf8_offsets` member and the `is_utf8`
  template parameter remain in place, and UTF-8 padding behaviour is
  unchanged.

### Repo-wide hygiene

- The file passes `clang-format --dry-run --Werror` against the
  repository's `.clang-format` (Allman braces — opening brace on its own
  line — and ClickHouse's existing rules).
- No tab characters anywhere in the file; spaces only.
- No trailing whitespace on any line.
- Braces, parentheses, and brackets remain balanced (the file still parses
  as valid C++).

## Out of scope

Modify only `src/Functions/padString.cpp`. Do not change tests, other
source files, the build system, or the `.clang-format` configuration.
