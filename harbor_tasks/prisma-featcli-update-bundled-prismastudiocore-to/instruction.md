# Update CLI-hosted Studio shell for @prisma/studio-core 0.27.3

## Problem

The CLI-hosted Studio (`packages/cli/src/Studio.ts`) was built against `@prisma/studio-core@0.21.1`. The new version (0.27.3) introduced several breaking compatibility requirements:

1. **Transaction support**: Studio 0.27.3 sends BFF requests with `procedure: "transaction"` for atomic multi-row saves. The CLI's BFF handler does not recognize this procedure and returns a 500 error (`Unknown procedure`). The executor provides an `executeTransaction` method that accepts a queries array and returns an `[error, results]` tuple (following the same pattern as the existing `executor.execute()` call for query procedures). The handler should check whether the executor supports transactions (similar to how the existing `sql-lint` procedure checks for `executor.lintSql`), and if execution returns an error, respond with a serialized error via `serializeBffError`.

2. **Missing browser imports**: The new Studio bundle imports `@radix-ui/react-toggle` and `chart.js/auto` as bare module specifiers. These are not in the CLI's HTML import map, so the browser throws unresolved module errors and the command palette crashes. The `@radix-ui/react-toggle` entry should use an esm.sh URL with `?deps=react@<version>,react-dom@<version>` query parameters to pin React dependencies. The `chart.js/auto` entry should use the URL pattern `esm.sh/chart.js@<version>/auto`.

3. **React version drift on esm.sh**: `esm.sh` can resolve React-dependent packages against a canary React version by default. Without pinning with `deps=react@`, the Radix toggle component loads a different React instance than the host shell, causing invalid-hook-call errors.

4. **No favicon**: Studio 0.27.3's UI requests `/favicon.ico`; the CLI returns 404, causing console noise. A GET route should be added for `/favicon.ico` (matching the existing `app.get` route registration pattern in the file) that returns SVG content. The HTML `<head>` should also include a `<link rel="icon">` tag pointing to the favicon.

5. **Hardcoded React versions**: The React version strings in the import map URLs are hardcoded in multiple places (e.g., `react@19.2.0`). They should be extracted into a `const REACT_VERSION` constant, with all import map entries referencing it via template literals using `${REACT_VERSION}` instead of hardcoded version strings.

## Expected Behavior

- `procedure: "transaction"` BFF requests should be routed to a handler that calls `executor.executeTransaction`, with support detection and error handling for the response tuple.
- The HTML import map should include entries for `@radix-ui/react-toggle` (with `deps=react@` pinning) and `chart.js/auto` (via esm.sh).
- React-dependent esm.sh imports should pin their React version using `deps=react@<version>` to match the shell's React version.
- `/favicon.ico` should be served via a GET route returning a valid SVG favicon, with a `<link rel="icon">` tag in the HTML head.
- The React version should be stored in a `REACT_VERSION` constant and referenced via `${REACT_VERSION}` in import map URL template literals, replacing the hardcoded version strings.
- Existing BFF procedures (`query`, `sequence`, `sql-lint`) must continue to work.

After making the code changes, update `AGENTS.md` to document these Studio CLI compatibility patterns — specifically mentioning the import map alignment requirement (including the new browser imports like `@radix-ui` and `chart.js`), the esm.sh React pinning pattern using `deps=react@`, and that the CLI shell can serve `/favicon.ico` directly.

## Files to Look At

- `packages/cli/src/Studio.ts` — The CLI-hosted Studio server, including BFF procedure routing and the HTML shell template with its import map.
- `AGENTS.md` — The project's agent knowledge base (also symlinked as `CLAUDE.md`). The "CLI commands" section documents Studio-related patterns.
