# HTTP Parser: Reject Conflicting Duplicate Content-Length Headers + PR Comments Tooling

## Problem

The HTTP parser in `packages/bun-uws/src/HttpParser.h` only inspects the first `Content-Length` header via `getHeader()`, silently ignoring any duplicate headers with different values. Per RFC 9112 section 6.3, multiple `Content-Length` headers with differing values indicate a request smuggling attempt and must be rejected with a 400 error. Empty Content-Length values can also be used to bypass naive duplicate checks.

Separately, the project lacks a comprehensive tool for reading PR feedback. The standard `gh pr view --comments` command silently omits review summaries and line-level review comments from the Files changed tab, which means developers can miss important reviewer feedback.

## Expected Behavior

**HTTP Parser Fix**: After parsing headers, the parser should walk every `Content-Length` header and reject the request (400) if any value differs from the first one. The implementation must:
- Use `req->bf.mightHave("content-length")` to short-circuit when no Content-Length header is present
- Iterate headers using a pattern like `for (HttpRequest::Header *h = req->headers; (++h)->key.length(); )`
- Check for Content-Length header key using `h->key.length() == 14 && !strncmp(h->key.data(), "content-length", 14)`
- Store the first Content-Length value in a `std::string_view contentLengthString` variable
- Check for empty values using `h->value.length() == 0`
- Track first-occurrence detection using `contentLengthString.data() == nullptr`
- Compare duplicate values byte-for-byte using `strncmp(h->value.data(), contentLengthString.data(), contentLengthString.length())`
- Return error using `HttpParserResult::error(HTTP_ERROR_400_BAD_REQUEST, HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH)`

Identical duplicate values should still be accepted. Empty Content-Length values should also be rejected.

**PR Comments Tool**: Create a script at `scripts/pr-comments.ts` that fetches all three GitHub comment endpoints (`/issues/N/comments`, `/pulls/N/reviews`, `/pulls/N/comments`) and presents them in one chronological listing. The script should:
- Accept PR number, URL, or current branch as input
- Support a `--json` flag for machine-readable output
- When in JSON mode, emit objects with keys: `when`, `user`, `kind`, `location`, `body`, `url`, `resolved`, `outdated`
- The `resolved` and `outdated` fields should come from GraphQL reviewThreads and only be present on line comments/replies

Add a `"pr:comments"` entry in `package.json` that runs `bun scripts/pr-comments.ts`.

**Documentation**: Update `CLAUDE.md` to document the new `pr:comments` command, including:
- Usage examples showing `bun run pr:comments`, `bun run pr:comments 28838`, `bun run pr:comments --json`
- An explanation of why it's needed versus `gh pr view --comments`
- Description of the JSON output schema with fields: `when`, `user`, `kind`, `location`, `body`, `url`, `resolved`, `outdated`

## Files to Look At

- `packages/bun-uws/src/HttpParser.h` — HTTP parser with Content-Length handling (search for `getHeader("content-length")`)
- `scripts/pr-comments.ts` — new file to create for PR comment fetching
- `package.json` — add the `pr:comments` script entry
- `CLAUDE.md` — document the new pr:comments tool in an appropriate section

## Notes

- The project uses bun as the runtime for TypeScript scripts. Check existing scripts in `scripts/` for coding conventions and import patterns.
- The C++ HTTP parser uses uWebSockets-style header iteration. Look at how the existing Transfer-Encoding conflict check works for the pattern to follow.
- All changes must be tested per the project's CLAUDE.md guidelines.
