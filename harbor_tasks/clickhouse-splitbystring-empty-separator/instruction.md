# Fix splitByString Tokenizer Empty Separator Validation

## Problem

The `splitByString` tokenizer in ClickHouse does not properly validate its input parameters. When users pass an empty string as one of the separators in the array argument, the tokenizer should reject it with a clear error message, but currently it doesn't.

For example, the following queries should be rejected with an error:
```sql
SELECT tokens('  a  bc d', 'splitByString', ['']);
SELECT tokens('  a  bc d', 'splitByString', [' ', '']);
```

## Task

Modify `src/Interpreters/TokenizerFactory.cpp` to add proper validation in the `split_by_string_creator` lambda function.

The fix should:
1. Check each separator string in the array to ensure it's not empty
2. Throw an exception with `ErrorCodes::BAD_ARGUMENTS` if an empty string is found
3. Update the existing error message for consistency (the message about empty separators array)

## Hints

- Look for the `split_by_string_creator` lambda in `TokenizerFactory.cpp`
- The lambda receives a `FieldVector` and processes it as an array of separators
- There's already a check for `values.empty()` - you'll need to add a similar check inside the loop
- Follow the existing code style (Allman braces, exception handling patterns)
- The error message format should follow the pattern: `"Incorrect parameter of tokenizer '{}': ..."`

## Files to Modify

- `src/Interpreters/TokenizerFactory.cpp` - Add validation in the `split_by_string_creator` lambda
