# Bug: "Copy as Markdown" feature fails when deployed

The Gradio website has internal API endpoints that serve documentation pages as markdown for the "Copy as Markdown" feature. When the site is deployed, the copy button silently fails — the markdown content never reaches the client.

## Problem Summary

The API endpoints currently return markdown wrapped in JSON objects (e.g., `{ "markdown": "..." }`), but the deployed environment expects plain text responses with appropriate markdown content headers. The client-side component also needs adjustment to match the new response format.

## Files to investigate

- `js/_website/src/routes/api/markdown/[doc]/+server.ts` — doc markdown endpoint
- `js/_website/src/routes/api/markdown/guide/[guide]/+server.ts` — guide markdown endpoint
- `js/_website/src/lib/components/DocsCopyMarkdown.svelte` — client component that fetches markdown

## Required behavior

### Server-side requirements

For both API endpoint files:

1. **Response format**: The endpoints must return markdown as plain text, not wrapped in JSON. The response body should be the raw markdown string.

2. **Content-Type header**: Markdown responses must include the header `Content-Type: text/markdown; charset=utf-8`

3. **X-Robots-Tag header**: Markdown responses must include the header `X-Robots-Tag: noindex`

4. **Error responses**: Error responses should return plain text error messages (not JSON-wrapped errors) with appropriate HTTP status codes (404 for not found, 500 for server errors)

5. **Import cleanup**: Any imports from `@sveltejs/kit` that are no longer needed after the changes should be removed

### Client-side requirements

For the DocsCopyMarkdown component:

1. **Reading the response**: The client must read the response body as plain text to obtain the markdown content

2. **No JSON extraction**: The client should not attempt to parse the response as JSON or extract a `.markdown` property from a parsed object — the response body itself is the markdown string

After these changes, the "Copy as Markdown" button should successfully retrieve and copy the markdown content when the site is deployed.
