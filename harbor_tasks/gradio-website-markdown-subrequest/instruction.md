# Inefficient Cloudflare Functions for LLM Markdown Serving

The Gradio website uses Cloudflare Pages Functions to serve markdown content to LLM crawlers and agents. When a request comes from an LLM user-agent (or with `Accept: text/markdown`), the functions in `js/_website/functions/_shared.ts` are supposed to route the request to the appropriate markdown API endpoint.

## The Problem

The two exported functions — `serveDocMarkdown` and `serveGuideMarkdown` — are currently making unnecessary subrequests. Each function:

1. Detects that the request is from an LLM crawler (user-agents containing "bot", "crawler", "spider", or requests with `Accept: text/markdown`)
2. Makes a `fetch()` call to the same origin's API endpoint
3. Parses the JSON response
4. Extracts the `markdown` field
5. Constructs a new `Response` with custom headers

This fetch-parse-rewrite cycle doubles the number of requests for every LLM markdown page view. The intermediate subrequest is wasteful because the API endpoints already exist and can serve the content directly.

## Relevant Files

- `js/_website/functions/_shared.ts` — contains `serveDocMarkdown` and `serveGuideMarkdown`

## Expected Behavior

For LLM requests:
- `serveDocMarkdown` must return an HTTP 3xx redirect response with a `Location` header pointing to `/api/markdown/<doc>` (where `<doc>` is the doc parameter from the request)
- `serveGuideMarkdown` must return an HTTP 3xx redirect response with a `Location` header pointing to `/api/markdown/guide/<guide>` (where `<guide>` is the guide parameter from the request)
- Neither function should make `fetch()` subrequests for LLM requests

For non-LLM requests:
- Both functions must fall through to `next()` unchanged, allowing normal page rendering

## Code Quality Requirements

- The modified TypeScript file must be formatted with Prettier using the configuration at `.config/.prettierrc.json` and ignore patterns from `.config/.prettierignore`
- The Cloudflare Pages Functions must build successfully with `wrangler pages functions build`
