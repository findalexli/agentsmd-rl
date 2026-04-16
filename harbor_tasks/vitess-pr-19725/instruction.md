# Versioned Comment Scanner Fix

## The Problem

The SQL parser's tokenizer handles MySQL versioned comments (`/*!NNNNN ... */`) in a way that causes incorrect behavior in several edge cases. When the scanner encounters a versioned comment, it must correctly determine whether the server version satisfies the comment version, and then parse or discard the comment body accordingly.

## Expected Behavior

The parser handles versioned comments according to MySQL 8.4 behavior:

1. **Version matching**: When the server version (e.g., `8.1.20`) satisfies the comment version (the 5-digit number in `/*!NNNNN`), the comment body is parsed as SQL and included in output.

2. **Version mismatch**: When the comment version is newer than the server version, the entire comment is discarded.

3. **Division operator** inside versioned comments: A `/` inside a versioned comment is always a division operator, not a comment-start delimiter.

4. **Nested regular comments**: A nested `/* ... */` inside a versioned comment is consumed and discarded (one level of nesting).

5. **Nested version comments**: `/*!` inside a versioned comment is treated as regular comment content, not a nested version comment.

6. **Unclosed versioned comments**: An unclosed versioned comment (no closing `*/`) produces a lex error at end of input.

7. **Short version numbers**: A version number with fewer than 5 digits (e.g., `/*!8010*/`) is treated as content, not a version marker.

## What to Fix

The current implementation produces incorrect results for some of these cases. For example:

- `SELECT /*!80100 1 + 1 */ FROM dual` with server version `8.1.20` should include `1 + 1` in the output
- `SELECT /*!90000 secret, */ 42 FROM dual` with server version `8.1.20` should output `42` (the `secret` part must not appear)
- `SELECT /*!80100 1 /* a comment */ + 2 */ FROM dual` should output `1 + 2` (nested comment consumed)
- `SELECT /*!80100 1 + 2` (unclosed) should produce a lex error
- `SELECT /*!80100 1 / 2 */ FROM dual` should output `1 / 2` (division, not comment-start)
- `SELECT /*!80100 42*/ FROM dual` should parse correctly with no space before `*/`

## Verification

Run the existing tokenizer and comment tests:

```bash
go test -run TestVersion -count=1 -v ./go/vt/sqlparser/
go test -run TestExtractCommentDirectives -count=1 -v ./go/vt/sqlparser/
```

The `TestVersionedCommentParsing` test in `go/vt/sqlparser/ast_funcs_test.go` validates the expected behavior against MySQL 8.4.
