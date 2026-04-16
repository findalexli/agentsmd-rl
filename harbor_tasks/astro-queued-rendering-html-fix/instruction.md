# Fix HTML Page Rendering in Queued Rendering Mode

## Problem

When `experimental.queuedRendering` is enabled in Astro, `.html` page files have their raw HTML content incorrectly escaped during rendering. Instead of the browser interpreting the HTML tags (like `<script>`, `<div>`, etc.), the angle brackets are escaped to `&lt;` and `&gt;`, causing the page to render as plain text instead of actual HTML.

## Symptoms

- Pages from `.html` files render as plain text with visible HTML tags
- The output shows escaped HTML entities like `&lt;script&gt;` instead of `<script>`
- This only happens when `experimental.queuedRendering` is enabled
- The issue affects the server-side rendering output of `.html` page components

## Relevant Files

- `packages/astro/src/runtime/server/render/page.ts` - Contains the `renderPage()` function that handles page rendering
- `packages/astro/src/runtime/server/escape.js` - Contains utilities for HTML escaping/marking

## Testing

The test file at `packages/astro/test/units/render/queue-rendering.test.js` contains regression tests that demonstrate the issue. You can run it with:

```bash
cd packages/astro
node --test test/units/render/queue-rendering.test.js
```

## Context

The `renderPage()` function in `page.ts` handles different types of page components. When queued rendering is enabled, it processes component output through a queue system. The issue is that `.html` page components (which return plain strings that are already valid HTML) are being treated like other components, causing their content to be escaped.

HTML page components have a special marker (`astro:html` property on the factory) that distinguishes them from regular components. The fix needs to respect this marker and ensure the content is not escaped.

## Your Task

1. Investigate the `renderPage()` function in `packages/astro/src/runtime/server/render/page.ts`
2. Understand how the queued rendering path processes component output
3. Find where `.html` page content gets incorrectly escaped
4. Implement a fix that preserves the raw HTML for `.html` pages while maintaining proper escaping for other component types
5. Run the tests to verify your fix works
