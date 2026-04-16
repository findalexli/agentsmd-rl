# Task: Fix HTTP Request Smuggling Vulnerability and Update Documentation

## Part 1: Security Fix - HTTP Content-Length Header Handling

The HTTP parser in `packages/bun-uws/src/HttpParser.h` has a security vulnerability related to request smuggling. Per **RFC 9112 Section 6.3**, multiple `Content-Length` header fields are only valid if every value is byte-for-byte identical; otherwise the message is malformed and must be rejected.

Currently, the parser only inspects the first `Content-Length` via `getHeader()`, silently ignoring any conflicting duplicates.

**Your task:**
1. Modify `packages/bun-uws/src/HttpParser.h` to detect and reject conflicting duplicate `Content-Length` headers
2. When Content-Length headers are present, iterate through all header entries to find and compare every instance
3. If duplicate Content-Length headers have different values, return HTTP 400
4. If a Content-Length header has an empty value, return HTTP 400 (per RFC 9112 6.3)
5. If all Content-Length values are identical, accept the request
6. Use the bloom filter `req->bf.mightHave("content-length")` to short-circuit when no Content-Length header is present
7. Return error code `HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH` when rejecting
8. Include a comment referencing "RFC 9112" or "RFC 9110" in the Content-Length handling code

## Part 2: Documentation Update - CLAUDE.md

**Background:** The existing `gh pr view --comments` command has a significant limitation: it only returns issue-stream comments and silently omits review summaries and line-level review comments. This creates a "footgun" where developers might miss critical review feedback.

**Your task:**
1. Create a new TypeScript script at `scripts/pr-comments.ts` that:
   - Fetches ALL feedback on a PR: issue comments, review summaries, line-level review comments, and inline suggestions
   - Uses `gh api --paginate` for all three REST endpoints (`/issues/N/comments`, `/pulls/N/reviews`, `/pulls/N/comments`)
   - Fetches thread state (resolved/outdated) via `graphql` (REST endpoint omits this)
   - Handles pagination manually for GraphQL (both outer and nested per-thread)
   - Supports both human-readable and JSON (`--json`) output modes
   - Can be called with PR number, URL, or defaults to current branch's PR
   - Shows summary counts by type, unresolved/resolved/outdated thread counts
   - Labels each entry with its kind (issue comment, review verdict, line comment, reply, + suggestion)

2. Add the script to `package.json` scripts as `"pr:comments": "bun scripts/pr-comments.ts"`

3. Add a new "Reading PR Feedback" section to `CLAUDE.md` that:
   - Explains the footgun with `gh pr view --comments` (uses the phrase "silently omits" or "only returns issue-stream comments")
   - Documents the `bun run pr:comments` command with usage examples
   - Shows examples for: current branch PR, by PR number, by URL
   - Documents the `--json` flag for machine-readable output
   - Shows jq filtering examples (e.g., filtering by user, filtering unresolved threads)
   - Explains the JSON output fields: `when`, `user`, `kind`, `location`, `body`, `url`, `resolved`, `outdated`
   - Notes that `resolved == false` unambiguously means "confirmed open thread"

## Important Notes

- The CLAUDE.md update is **mandatory** — this is an agentmd-edit task that tests both code and documentation changes
- Follow existing code patterns in HttpParser.h (bloom filter usage, error return patterns)
- The TypeScript script should follow Bun conventions (use `bun` shebang, `await $` for shell commands)
- Test your changes: the HTTP fix should reject conflicting Content-Length headers with 400, and the script should be runnable via `bun run pr:comments`