# HTTP Parser: Reject Conflicting Duplicate Content-Length Headers + PR Comments Tooling

## Problem

The HTTP parser in `packages/bun-uws/src/HttpParser.h` only inspects the first `Content-Length` header via `getHeader()`, silently ignoring any duplicate headers with different values. Per RFC 9112 section 6.3, multiple `Content-Length` headers with differing values indicate a request smuggling attempt and must be rejected with a 400 error. Empty Content-Length values can also be used to bypass naive duplicate checks.

Separately, the project lacks a comprehensive tool for reading PR feedback. The standard `gh pr view --comments` command silently omits review summaries and line-level review comments from the Files changed tab, which means developers can miss important reviewer feedback.

## Expected Behavior

**HTTP Parser Fix**: After parsing headers, the parser should walk every `Content-Length` header and reject the request (400) if any value differs from the first one. Identical duplicate values should still be accepted. Empty Content-Length values should also be rejected.

**PR Comments Tool**: Create a script at `scripts/pr-comments.ts` that fetches all three GitHub comment endpoints (issue comments, reviews, and line-level review comments) and presents them in one chronological listing. Add a `"pr:comments"` entry in `package.json` that runs the script.

**Documentation**: Update `CLAUDE.md` to document the new `pr:comments` command, including usage examples, output format description, and an explanation of why it's needed over `gh pr view --comments`.

## Files to Look At

- `packages/bun-uws/src/HttpParser.h` — HTTP parser with Content-Length handling (search for `getHeader("content-length")`)
- `scripts/pr-comments.ts` — new file to create for PR comment fetching
- `package.json` — add the `pr:comments` script entry
- `CLAUDE.md` — document the new pr:comments tool in an appropriate section

## Notes

- The project uses bun as the runtime for TypeScript scripts. Check existing scripts in `scripts/` for coding conventions and import patterns.
- The C++ HTTP parser uses uWebSockets-style header iteration. Look at how the existing Transfer-Encoding conflict check works for the pattern to follow.
- All changes must be tested per the project's CLAUDE.md guidelines.
