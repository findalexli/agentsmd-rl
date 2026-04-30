# Task: Add empty separator validation to splitByString tokenizer

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its arguments when provided with an array of separator strings. Specifically, it fails to reject empty strings as separators, which could lead to unexpected behavior or undefined results.

## File to modify

- `src/Interpreters/TokenizerFactory.cpp`

## Expected behavior

When processing the separators array argument, the tokenizer should handle two validation cases:

1. **Empty string separator**: When an individual separator in the array is an empty string, the tokenizer should throw a `BAD_ARGUMENTS` error. For example:

```sql
SELECT tokens('  a  bc d', 'splitByString', ['']);        -- should error
SELECT tokens('  a  bc d', 'splitByString', [' ', '']);   -- should error
```

The error message must include:
```
the empty string cannot be used as a separator
```

2. **Empty separators array**: When the separators array contains no elements, the tokenizer should throw a `BAD_ARGUMENTS` error. The error message for this case must be:
```
the separators argument cannot be empty
```

## Code Style Requirements

When modifying the C++ code:
- Use Allman-style braces (opening brace on a new line)
- Use indentation in multiples of 4 spaces
- No tab characters, no trailing whitespace
- No more than two consecutive empty lines
- Keep consistent with the existing code patterns in the file
