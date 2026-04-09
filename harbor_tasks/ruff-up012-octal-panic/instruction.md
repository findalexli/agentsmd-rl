# Fix panic in UP012 rule caused by octal escape handling

## Problem

Running `ruff check --select UP012` on Python files containing certain string literals with octal escape sequences causes ruff to panic with a thread crash. For example, checking a file containing `"$IMURAW\0".encode("ascii")` triggers an internal panic.

Additionally, strings that combine octal escapes with named Unicode escapes (like `\N{DIGIT ONE}`) may incorrectly trigger UP012 when they shouldn't, because the escape sequence parser loses track of its position after processing the octal.

## Expected Behavior

- `ruff check --select UP012` should never panic regardless of the string contents.
- Strings containing named Unicode escapes (`\N{...}`) should not trigger UP012, since `\N{...}` is not valid in byte literals.
- Octal escape values should be correctly validated against byte range limits.

## Files to Look At

- `crates/ruff_linter/src/rules/pyupgrade/rules/unnecessary_encode_utf8.rs` — contains the `literal_contains_string_only_escapes` function that parses escape sequences in string literals for the UP012 rule
