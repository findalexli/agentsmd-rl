# Update CLI-hosted Studio shell for @prisma/studio-core 0.27.3

## Problem

The CLI-hosted Studio (`packages/cli/src/Studio.ts`) was built against `@prisma/studio-core@0.21.1`. The new version (0.27.3) introduced several breaking compatibility requirements:

### 1. Transaction procedure causes 500 error

Studio 0.27.3 sends BFF requests with `procedure: "transaction"` for atomic multi-row saves. The CLI's BFF handler returns a 500 error with message "Unknown procedure" because this procedure is not recognized. The executor provides a method that accepts a queries array and returns an `[error, results]` tuple — similar pattern to the existing `executor.execute()` call for query procedures. The handler should check whether the executor supports this transaction capability (similar to how `sql-lint` checks for `executor.lintSql`), and if the response tuple contains an error, respond with a serialized error via the same error serialization function used elsewhere in the BFF handler.

The transaction procedure check in the handler should use the string comparison pattern `procedure === 'transaction'` (single quotes around the string literal).

When handling the response tuple, the error should be detected with an `if (error)` guard — checking the first element of the tuple.

### 2. Missing browser module imports cause crashes

The new Studio bundle imports `@radix-ui/react-toggle` and `chart.js/auto` as bare module specifiers. These are not in the CLI's HTML import map, so the browser throws unresolved module errors and the command palette crashes.

The `@radix-ui/react-toggle` entry must use an esm.sh URL with `?deps=react@<version>,react-dom@<version>` query parameters to pin React dependencies and prevent invalid-hook-call errors.

The `chart.js/auto` entry must use the URL pattern `esm.sh/chart.js@<version>/auto`.

### 3. React version drift on esm.sh

esm.sh can resolve React-dependent packages against a canary React version by default. Without explicit React version pinning in the import map URLs, the Radix toggle component may load a different React instance than the host shell, causing runtime errors.

### 4. Missing favicon causes 404 noise

Studio 0.27.3's UI requests `/favicon.ico`; the CLI returns 404, causing console noise. A GET route for `/favicon.ico` (following the existing `app.get` route registration pattern in the file) should return SVG content. The HTML `<head>` should include a `<link rel="icon">` tag pointing to the favicon.

### 5. Hardcoded React versions in import map URLs

The import map in `Studio.ts` contains multiple hardcoded React version strings (e.g., `react@19.2.0`). All import map entries that reference React versions should use a consistent approach: define a constant named `REACT_VERSION` (using `const REACT_VERSION = '19.2.0'` syntax) and reference it in template literal strings as `${REACT_VERSION}` rather than hardcoding the version in multiple places.

## Expected Behavior

- BFF requests with `procedure: "transaction"` should be handled by a procedure check using the string literal `'transaction'` (single quotes), calling the executor's transaction method, checking for errors with an `if (error)` guard, and responding with serialized errors for error cases.
- The HTML import map should include entries for `@radix-ui/react-toggle` (with `?deps=react@<version>` query parameter) and `chart.js/auto` (via esm.sh).
- Import map entries for React-dependent packages should pin their React version using `?deps=react@<version>` query parameter.
- `/favicon.ico` should be served via a GET route with `app.get` pattern, returning valid SVG content, with a `<link rel="icon">` tag in the HTML head.
- React version should be defined as `const REACT_VERSION = '19.2.0'` and referenced via `${REACT_VERSION}` in import map URL template literals, replacing hardcoded version strings.
- Existing BFF procedures (`query`, `sequence`, `sql-lint`) must continue to work.

After making the code changes, update `AGENTS.md` to document these Studio CLI compatibility patterns — specifically mentioning the import map alignment requirement (including the new browser imports like `@radix-ui` and `chart.js`), the esm.sh React pinning pattern using `?deps=react@`, and that the CLI shell can serve `/favicon.ico` directly.

## Files to Look At

- `packages/cli/src/Studio.ts` — The CLI-hosted Studio server, including BFF procedure routing and the HTML shell template with its import map.
- `AGENTS.md` — The project's agent knowledge base (also symlinked as `CLAUDE.md`). The "CLI commands" section documents Studio-related patterns.