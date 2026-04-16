# HTTP Parser: Reject Conflicting Duplicate Content-Length Headers + PR Comments Tooling

## Problem

The HTTP parser silently accepts requests with duplicate `Content-Length` headers when the values differ. Per RFC 9112 section 6.3, multiple `Content-Length` headers with differing values indicate a request smuggling attempt and must be rejected with a 400 error. Empty `Content-Length` values can also be used to bypass naive duplicate checks.

Separately, the project lacks a comprehensive tool for reading PR feedback. The standard `gh pr view --comments` command silently omits review summaries and line-level review comments from the Files changed tab, which means developers can miss important reviewer feedback.

## Expected Behavior

**HTTP Parser Fix**: After parsing headers, the parser must reject requests with conflicting `Content-Length` headers (different values) or empty `Content-Length` values with HTTP 400 Bad Request.

**PR Comments Tool**: Create a script at `scripts/pr-comments.ts` that fetches all three GitHub comment endpoints (`/issues/N/comments`, `/pulls/N/reviews`, `/pulls/N/comments`) and presents them in one chronological listing. The script should:
- Accept PR number, URL, or current branch as input
- Support a `--json` flag for machine-readable output
- When in JSON mode, emit objects with keys: `when`, `user`, `kind`, `location`, `body`, `url`, `resolved`, `outdated`

Add a `"pr:comments"` entry in `package.json` that runs `bun scripts/pr-comments.ts`.

**Documentation**: Update `CLAUDE.md` to document the new `pr:comments` command, including:
- How to run it (`bun run pr:comments`)
- Why it's needed versus `gh pr view --comments`
- The JSON output schema with its fields

## Files to Look At

- `packages/bun-uws/src/HttpParser.h` — HTTP parser with Content-Length handling
- `scripts/pr-comments.ts` — new file to create for PR comment fetching
- `package.json` — add the `pr:comments` script entry
- `CLAUDE.md` — document the new pr:comments tool in an appropriate section

## Notes

- The project uses bun as the runtime for TypeScript scripts. Check existing scripts in `scripts/` for coding conventions and import patterns.
- All changes must be tested per the project's CLAUDE.md guidelines.