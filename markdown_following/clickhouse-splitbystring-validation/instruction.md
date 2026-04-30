# Task: Add Empty String Separator Validation to a String Tokenizer

## Problem Description

In the ClickHouse codebase, the tokenizer responsible for splitting strings by separator arguments (`splitByString`) does not validate whether separator arguments are empty strings. When an empty string is passed as a separator — either as a direct argument or within an array of separators — the tokenizer proceeds without raising an error, leading to unexpected behavior.

Additionally, the existing error message for empty separator arrays uses unclear wording that should be improved.

## Requirements

### Empty String Separator Validation

When the tokenizer processes separators and encounters an empty string, it must throw an exception with `ErrorCodes::BAD_ARGUMENTS`. The exception message must contain the exact text:

```
the empty string cannot be used as a separator
```

### Array Element Validation

When an array of separators is provided, each element must be individually validated before being added to the result vector. The validation must occur inside the loop that iterates over the array elements (`for (const auto & value : array)` in `src/Interpreters/TokenizerFactory.cpp`). If any separator value is empty, the exception described above must be thrown.

### Improved Error Message for Empty Separators Array

The existing check that rejects empty separator arrays should be updated to use the following error message text:

```
the separators argument cannot be empty
```

## Code Style

- Use Allman-style braces: opening braces must appear on their own line after control statements (`for`, `if`, etc.)
- Refer to logical errors as "exceptions", not "crashes" in any comments
- Use 4 spaces for indentation (no tabs)
- No trailing whitespace
