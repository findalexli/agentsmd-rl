# Replace nested tokenizer with inline versioned comment scanning

## Problem

The SQL parser's tokenizer (`go/vt/sqlparser/token.go`) handles MySQL versioned comments (`/*!NNNNN ... */`) by creating a separate nested `Tokenizer` instance for the comment body. This approach has several issues:

1. **Nested `/* ... */` comments** inside a versioned comment cause incorrect behavior. The outer `scanMySQLSpecificComment` scans for the first `*/` to find the comment boundary, but a nested comment's `*/` prematurely closes the versioned comment. This means queries like `SELECT /*!80100 1 /* annotation */ + 2 */` fail to parse correctly.

2. **Short version numbers** (fewer than 5 digits) in `/*!NNN ... */` are silently accepted when they should be treated differently per MySQL 8.4 behavior.

3. The `ExtractMysqlComment` helper function in `comments.go` is only used for this nested tokenizer approach and adds unnecessary complexity.

## Expected Behavior

- Versioned comments should be scanned inline using scanner state (e.g., a flag) instead of creating a nested `Tokenizer`. When the version is satisfied, the scanner should read inner tokens directly from the outer buffer. When it encounters the closing `*/`, it should skip past it and resume normal scanning.
- Nested `/* ... */` comments inside a versioned comment should be consumed and discarded (one level of nesting, matching MySQL 8.4).
- `/*!` inside a versioned comment should be treated as a regular nested comment.
- Versioned comments with fewer than 5 version digits should treat the digits as content, not a version number.
- When the version is not satisfied, the entire comment body (including any nested comments) should be skipped correctly.
- The `ExtractMysqlComment` function should be removed since it's no longer needed.

After making the code changes, update the agent instructions for the sqlparser package to document the key design constraint about scan helper methods. The project uses `AGENTS.md` files for package-level agent guidance.

## Files to Look At

- `go/vt/sqlparser/token.go` — the tokenizer, where `Scan()` and `scanMySQLSpecificComment()` live
- `go/vt/sqlparser/comments.go` — contains `ExtractMysqlComment` (to be removed)
- `go/vt/sqlparser/testdata/select_cases.txt` — parser test expectations that may need updating
