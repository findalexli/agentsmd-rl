# Bug: HTML output escaped incorrectly for .html page files with queuedRendering

## Symptom

When `experimental.queuedRendering` is enabled in Astro's SSR configuration, `.html` page files (e.g., `src/pages/admin/index.html`) render their HTML content as plain text instead of HTML in the browser.

For example, a `<script>` tag that should load as JavaScript appears as the literal text `&lt;script src="..."&gt;&lt;/script&gt;` on the page.

The problem only occurs with `.html` files — regular `.astro` pages render correctly.

## Expected Behavior

When `queuedRendering` is enabled:

- `.html` page components (those with `astro:html = true` set by vite-plugin-html) should render their HTML content unchanged (e.g., `<script src="/assets/app.js"></script>` should appear as a real script tag, not escaped text)
- Regular (non-.html) page components should still have their HTML content escaped for security

## Technical Context

The `renderPage()` function in the Astro SSR runtime handles rendering of non-Astro page components. When `queuedRendering` is enabled, page component output is processed through a queue system before being returned as an HTTP response.

`.html` page components are created by vite-plugin-html and have the `astro:html` marker property set to `true` on their factory function. The raw HTML content is returned as a plain JavaScript string from the component factory.

The Astro SSR runtime includes utilities for handling HTML string safety. The expected output for an `.html` page with a script tag should contain `<script` (unescaped), not `&lt;script` (HTML-escaped).

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `eslint (JS/TS linter)`
