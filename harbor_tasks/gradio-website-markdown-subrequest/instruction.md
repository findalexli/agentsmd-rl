# Inefficient Cloudflare Functions for LLM Markdown Serving

The Gradio website uses Cloudflare Pages Functions to serve markdown content to LLM crawlers and agents. When a request comes from an LLM user-agent (or with `Accept: text/markdown`), the functions in `js/_website/functions/_shared.ts` are supposed to route the request to the appropriate markdown API endpoint.

## The Problem

The two exported functions — `serveDocMarkdown` and `serveGuideMarkdown` — are currently making unnecessary subrequests. Each function:

1. Detects that the request is from an LLM crawler
2. Makes a `fetch()` call to the same origin's API endpoint (e.g., `/api/markdown/<doc>`)
3. Parses the JSON response
4. Extracts the `markdown` field
5. Constructs a new `Response` with custom headers

This is wasteful because these functions run as prerendered Cloudflare Pages routes. The intermediate fetch-parse-rewrite cycle doubles the number of requests for every LLM markdown page view. The markdown API endpoints already exist and can serve the content directly — the functions just need to point LLM clients there without proxying the response body.

## Relevant Files

- `js/_website/functions/_shared.ts` — contains `serveDocMarkdown` and `serveGuideMarkdown`

## Expected Behavior

LLM requests to doc and guide pages should be handled with minimal overhead — no unnecessary subrequests or response body proxying. Non-LLM requests should continue to fall through to `next()` unchanged.
