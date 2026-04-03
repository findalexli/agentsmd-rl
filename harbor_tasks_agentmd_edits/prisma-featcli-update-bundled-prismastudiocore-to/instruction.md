# Update CLI-hosted Studio shell for @prisma/studio-core 0.27.3

## Problem

The CLI-hosted Studio (`packages/cli/src/Studio.ts`) was built against `@prisma/studio-core@0.21.1`. The new version (0.27.3) introduced several breaking compatibility requirements:

1. **Transaction support**: Studio 0.27.3 sends BFF requests with `procedure: "transaction"` for atomic multi-row saves. The CLI's BFF handler does not recognize this procedure and returns a 500 error (`Unknown procedure`).

2. **Missing browser imports**: The new Studio bundle imports `@radix-ui/react-toggle` and `chart.js/auto` as bare module specifiers. These are not in the CLI's HTML import map, so the browser throws unresolved module errors and the command palette crashes.

3. **React version drift on esm.sh**: `esm.sh` can resolve React-dependent packages against a canary React version by default. Without pinning, the Radix toggle component loads a different React instance than the host shell, causing invalid-hook-call errors.

4. **No favicon**: Studio 0.27.3's UI requests `/favicon.ico`; the CLI returns 404, causing console noise.

## Expected Behavior

- `procedure: "transaction"` BFF requests should be routed to the executor's transaction handler, with proper error handling if the executor doesn't support transactions.
- The HTML import map should include entries for `@radix-ui/react-toggle` and `chart.js/auto`.
- React-dependent esm.sh imports should pin their React version to match the shell's React version to avoid hook-call crashes.
- `/favicon.ico` should return a valid SVG favicon.
- The hardcoded React version URLs in the import map should be refactored to use a constant to prevent version drift.

After making the code changes, update the project's agent instructions (`AGENTS.md`) to document these Studio CLI compatibility patterns — particularly the import map alignment requirement and the esm.sh React pinning pattern — so future contributors know about these constraints.

## Files to Look At

- `packages/cli/src/Studio.ts` — The CLI-hosted Studio server, including BFF procedure routing and the HTML shell template with its import map.
- `AGENTS.md` — The project's agent knowledge base (also symlinked as `CLAUDE.md`). The "CLI commands" section documents Studio-related patterns.
