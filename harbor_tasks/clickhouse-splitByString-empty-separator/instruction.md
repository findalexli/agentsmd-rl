# Fix splitByString Tokenizer Empty Separator Validation

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its input when given an array of separator strings. Specifically:

1. **Empty strings in separators array**: When calling `tokens('some text', 'splitByString', ['', ' '])` or any variant where an empty string `''` is included in the separators array, the tokenizer should reject this with a clear error message. Currently, it appears to silently accept empty strings which can lead to unexpected behavior.

2. **Unclear error message**: The existing error message when the separators array is empty says "separators cannot be empty" which is ambiguous - it should clarify that "the separators argument cannot be empty".

## Files to Modify

- `src/Interpreters/TokenizerFactory.cpp` - Look for the `split_by_string_creator` lambda function (around line 193)

## What You Need to Do

1. Add validation inside the `for` loop that processes the separators array to check if any separator is an empty string
2. Throw an appropriate `Exception` with `ErrorCodes::BAD_ARGUMENTS` when an empty separator is detected
3. Update the error message for the empty separators array case to be more descriptive
4. Follow the existing code style (Allman braces - opening brace on a new line)

## Example of the Bug

```sql
-- This should throw BAD_ARGUMENTS but currently doesn't validate properly
SELECT tokens('  a  bc d', 'splitByString', ['']);
SELECT tokens('  a  bc d', 'splitByString', [' ', '']);
```

The fix should make these queries throw `BAD_ARGUMENTS` with a clear error message indicating that empty strings cannot be used as separators.
