# Bug: Website markdown API endpoints break behind Cloudflare Functions

The Gradio website has internal API endpoints that serve documentation pages as markdown for the "Copy as Markdown" feature:

- `js/_website/src/routes/api/markdown/[doc]/+server.ts` — serves component/API docs
- `js/_website/src/routes/api/markdown/guide/[guide]/+server.ts` — serves guide pages

These endpoints currently wrap the markdown content inside a JSON response (using SvelteKit's `json()` helper), returning `{"markdown": "...content..."}`. The client component at `js/_website/src/lib/components/DocsCopyMarkdown.svelte` then parses this with `response.json()` and extracts the `.markdown` field.

**The problem**: When the site is deployed behind Cloudflare Functions, the "Copy as Markdown" feature breaks. The Cloudflare Functions forwarding layer doesn't properly handle these responses — the markdown content never reaches the client, and the copy button silently fails. The issue is in how the API endpoints format and return the markdown content, which is incompatible with Cloudflare's forwarding expectations.

**Expected behavior**: The "Copy as Markdown" button should work correctly when the site is served through Cloudflare Functions. The markdown content should be returned in a format that Cloudflare can forward without modification, and the client should be able to consume the response correctly.

## Files to investigate

- `js/_website/src/routes/api/markdown/[doc]/+server.ts` — doc markdown endpoint
- `js/_website/src/routes/api/markdown/guide/[guide]/+server.ts` — guide markdown endpoint
- `js/_website/src/lib/components/DocsCopyMarkdown.svelte` — client that fetches markdown
