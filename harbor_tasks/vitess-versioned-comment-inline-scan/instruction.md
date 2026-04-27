# vitess sqlparser: align MySQL versioned-comment scanning with MySQL 8.4

## Background

The vitess SQL parser lives at `go/vt/sqlparser/` in the `vitess.io/vitess`
repository. Its lexer (`token.go`) handles MySQL "versioned" comments of the
form `/*!NNNNN ... */`. When the parser's MySQL server version is greater
than or equal to `NNNNN`, the comment body is parsed as part of the
surrounding statement; otherwise the body is discarded.

The current implementation scans the comment body using a *nested*
`Tokenizer` allocated for each versioned comment encountered. This has two
practical problems we need to fix:

1. **Token positions are reported relative to the comment body, not the
   original query string.** A downstream piece of work needs accurate
   positions for tokens that come from inside a versioned comment, and the
   nested-tokenizer approach makes that hard.
2. **The lexer's behavior diverges from MySQL 8.4** in several edge cases
   listed below. The parser must produce the same outputs as MySQL 8.4 for
   each of these cases.

You are working from the base commit
`9a3646f7f16d38cec2efabc13cef5da800a72280`. Your repository is at
`/workspace/vitess/`.

## What to change

Refactor the lexer so that, when a versioned comment's version is
satisfied, tokens inside the comment body are scanned **inline** from the
outer input — without allocating a new tokenizer. The closing `*/` of a
versioned comment must be detected from inline scanning state and consumed
as part of normal scanning.

While doing this refactor, also align the lexer with the following MySQL
8.4 behaviors. Each item below is a behavioral contract that must hold for
any input the parser receives. The parser is exposed via
`parser.Parse(sql)`; the canonical text of a parsed statement is produced
by `String(stmt)` and is what these contracts assert against.

### Required behaviors (parser version `8.1.20` unless stated otherwise)

#### 1. Versioned comment whose version is satisfied

```
SELECT /*!80100 JSON_VALUE(col, '$.x') AS jval, */ id FROM t
```
Parses to: `select json_value(col, '$.x') as jval, id from t`

#### 2. Versioned comment whose version is *not* satisfied is discarded

```
SELECT /*!90000 UPPER('hidden'), */ 42
```
Parses to: `select 42 from dual`

#### 3. `/*!` with no version digits acts as "always satisfied"

```
SELECT /*! 1 + 1 */ FROM dual
```
Parses to: `select 1 + 1 from dual`

#### 4. One level of nested `/* ... */` regular comments is allowed inside a versioned comment

```
SELECT /*!80100 1 /* a comment */ + 2 */
```
Parses to: `select 1 + 2 from dual`

The closing `*/` of the inner comment must NOT be treated as the closing
`*/` of the outer versioned comment.

#### 5. A nested `/*! ... */` inside a versioned comment is treated like a regular nested comment

```
SELECT /*!80100 1 /*!99999 noise */ + 2 */
```
Parses to: `select 1 + 2 from dual`

The same rule applies when the *outer* comment is being skipped because its
version is too high:

```
SELECT /*!90000 1 /* nested */ + 2 */ 42
```
Parses to: `select 42 from dual`

```
SELECT /*!90000 1 /*!99999 nested */ + 2 */ 42
```
Parses to: `select 42 from dual`

#### 6. Unclosed versioned comments are a lex error at EOF

```
SELECT /*!80100 1 + 2
```
Must produce a parse error whose `.Error()` returns exactly:

```
syntax error at position 22
```

(Position is 1-based and refers to the character just past EOF.)

#### 7. Version digits and content boundaries

A versioned comment specifier requires **exactly five** digits after `/*!`
to be recognised as a version. Fewer than five digits are part of the
comment content, not the version:

```
SELECT /*!8010*/ FROM dual          → select 8010 from dual
SELECT /*! 1 + 2*/ FROM dual        → select 1 + 2 from dual
```

A version specifier may be followed immediately by content (no whitespace
needed):

```
SELECT 1 + /*!801002*/              → select 1 + 2 from dual
SELECT /*!80100 42*/ FROM dual      → select 42 from dual
SELECT 1 /*!80100 */                → select 1 from dual
```

#### 8. `/` inside a versioned comment is always division

While scanning the body of a satisfied versioned comment, a `/` character
that is *not* followed by `*` must be returned as a plain division
operator. (This prevents the inline scanner from accidentally entering a
comment-scan state that overshoots the outer `*/`.)

#### 9. `select 1/*!2*/;` is a syntax error

`/*!2*/` has only one digit, so it is content (not a version). The body
scans to the digit `2`, which becomes a token immediately after `1`. With
no operator between the two numbers this is a syntax error:

```
select 1/*!2*/;     → "syntax error" (the parser's error message contains the literal substring "syntax error")
```

#### 10. Test data must reflect new error positions

The repository tracks expected lexer behavior in
`go/vt/sqlparser/testdata/select_cases.txt`. Two existing entries currently
expect outputs from the *old* nested-tokenizer behavior; they must be
updated to match the new contracts above. Specifically the cases for the
inputs

```
select 1 + /*!00000 2 node_modules/ + 3 /*!99999 noise*/ + 4;
select 1/*!2*/;
select 1/*!000002*/;
```

must now reflect the error positions / classifications that arise from
inline scanning. Run the existing test driver (`go test
./go/vt/sqlparser/...`) to surface mismatches and update the expected
values to match the new lexer's actual output. Do not change the inputs.

## What must keep working

- The full sqlparser package test suite (`go test
  ./go/vt/sqlparser/...`) must pass.
- `go vet ./go/vt/sqlparser/...` must pass.
- All currently passing parses of versioned comments (cases where the
  version is satisfied and the comment body is straightforward) must still
  produce the same canonical output.

## Code Style Requirements

The repository's `AGENTS.md` requires that all changed Go files be:

- formatted with `gofumpt -w`
- imports organised with `goimports -local "vitess.io/vitess" -w`

The `go vet` check above is mandatory.

## Out of scope

- Changes to non-`go/vt/sqlparser/` packages.
- Generated files in `go/vt/sqlparser/` (`sql.go`, `ast_clone.go`,
  `ast_copy_on_rewrite.go`, `ast_equals.go`, `ast_format_fast.go`,
  `ast_path.go`, `ast_rewrite.go`, `ast_visit.go`, `cached_size.go`) are
  produced by `make codegen` and must not be edited directly.
- Performance work: parity with the old implementation is sufficient.
