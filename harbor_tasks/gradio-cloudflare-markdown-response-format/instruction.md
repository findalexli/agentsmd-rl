# Bug: "Copy as Markdown" feature fails when deployed

The Gradio website has internal API endpoints that serve documentation pages as markdown for the "Copy as Markdown" feature. When the site is deployed, the copy button silently fails — the markdown content never reaches the client.

## Files to investigate

- `js/_website/src/routes/api/markdown/[doc]/+server.ts` — doc markdown endpoint
- `js/_website/src/routes/api/markdown/guide/[guide]/+server.ts` — guide markdown endpoint
- `js/_website/src/lib/components/DocsCopyMarkdown.svelte` — client component that fetches markdown

## Required behavior

The API endpoints must be modified to:

1. Define a constant named `MARKDOWN_HEADERS` with:
   - `"Content-Type": "text/markdown; charset=utf-8"`
   - `"X-Robots-Tag": "noindex"`

2. Return markdown content using `new Response()` with the `MARKDOWN_HEADERS` headers, not the `json()` helper

3. Remove the `json` import from `@sveltejs/kit` since it is no longer needed

4. Return error responses as plain text `new Response("Error message", { status: ... })` instead of JSON-wrapped errors

The client component must be modified to:

1. Use `response.text()` instead of `response.json()` to read the response

2. Remove the pattern of extracting `.markdown` from parsed JSON — the response body should be used directly as the markdown string

After these changes, the "Copy as Markdown" button should successfully retrieve and copy the markdown content.
