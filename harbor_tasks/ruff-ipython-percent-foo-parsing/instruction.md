# Fix %foo? parsing in IPython assignment expressions

## Bug Description

In IPython mode, ruff's parser incorrectly handles `%foo?` when it appears on the right-hand side of an assignment expression like `x = %foo?`. The `?` at the end is being interpreted as a "help end" escape command (which would convert the entire expression into a help query), but in the assignment context, it should be treated as part of the magic command's value.

In IPython, `x = %foo?` means "assign the result of running the line magic named `foo?` to `x`". This matches IPython's assignment-magic transform behavior. However, ruff's lexer currently treats `?` as a help-end token in all contexts, which causes it to be incorrectly split off from the command value.

The issue is that the lexer does not distinguish between IPython escape commands that appear at the start of a logical line (where `?` should be a help-end token) versus those that appear after an `=` sign in an assignment context (where `?` should be part of the command value).

Similarly, `x = !pwd?` should parse `pwd?` as the shell command value, not split the `?` as a help token.

## Files to Modify

- `crates/ruff_python_parser/src/lexer.rs`
- `crates/ruff_python_parser/src/parser/tests.rs` (add test cases)
