# Fix HTTP Request Smuggling Vulnerability

## Problem

The HTTP server has a request smuggling vulnerability related to how it handles multiple `Content-Length` header fields. Per RFC 9112 section 6.3, when multiple `Content-Length` headers are present with differing values, or when any `Content-Length` header has an empty value, the request is ambiguous and must be rejected with HTTP 400 to prevent request smuggling attacks.

Currently, the parser only inspects the first `Content-Length` header, silently ignoring any conflicting duplicates.

## Requirements

### 1. Fix the HTTP Parser Security Issue

Locate the HTTP parser code that handles the `Content-Length` header validation. The parser should use a bloom filter check (`mightHave`) to detect whether Content-Length headers are present before attempting to read them.

Modify the parser to enforce RFC 9112 section 6.3 for duplicate Content-Length headers:

- **Reject** with HTTP 400 when duplicate Content-Length headers have different values (the parser should compare the actual header values to detect conflicts)
- **Reject** with HTTP 400 when any Content-Length header has an empty value
- **Accept** requests when duplicate Content-Length headers have identical values

The fix should use an error code constant named `HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH` (or similar) when rejecting invalid Content-Length headers. The parser should reference RFC 9112 or RFC 9110 for Content-Length validation.

### 2. Add Tests

Add test cases to `test/js/bun/http/request-smuggling.test.ts` with these exact names:

- `"rejects conflicting duplicate Content-Length headers"`
- `"accepts duplicate Content-Length headers with identical values"`
- `"rejects empty-valued Content-Length followed by smuggled Content-Length"`

Tests should follow the existing pattern in the file (using `Bun.serve`, `net.connect`, and async/await).

### 3. Document the New PR Comments Tool

**In `CLAUDE.md`:**
Add a "Reading PR Feedback" section at the end that documents:
- The footgun of `gh pr view --comments` (only shows issue comments, silently omits line-level reviews)
- The new `bun run pr:comments` command
- Usage examples (by PR number, URL, current branch)
- JSON mode with fields: `when`, `user`, `kind`, `location`, `body`, `url`, `resolved`, `outdated`

**In `package.json`:**
Add a script entry: `"pr:comments": "bun scripts/pr-comments.ts"`

**Create `scripts/pr-comments.ts`:**
- Fetches all PR feedback: issue comments, review summaries, line-level comments
- Uses `gh api --paginate` for REST endpoints to handle pagination
- Uses GraphQL to get thread resolved/unresolved state
- Supports `--json` flag for machine-readable output
- Handles PR lookup by number, URL, or current branch

## Security Impact

This fix prevents HTTP request smuggling attacks where an attacker sends multiple Content-Length headers with different values to confuse front-end proxies and back-end servers.