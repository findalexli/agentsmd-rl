# Add API History Blocks to Electron Docs (G-I)

## Problem

Electron's API documentation pages for modules starting with G through I are missing structured history metadata. Each API method, event, class, and property should have a YAML history block (in an HTML comment) that records when it was added and any breaking changes. Currently, these docs have no such annotations.

The affected API documentation files are:
- `docs/api/global-shortcut.md`
- `docs/api/image-view.md`
- `docs/api/in-app-purchase.md`
- `docs/api/ipc-main.md`
- `docs/api/ipc-renderer.md`

## Expected Behavior

Each API entry (method, event, class definition, or property with a backtick signature heading) should have a YAML history block placed directly after its Markdown heading and before its parameter list. The block format uses an HTML comment wrapping a YAML code fence tagged `YAML history`.

For APIs that had breaking changes (like methods that were promisified), the history block should also include `changes` entries with descriptions and cross-references to `docs/breaking-changes.md`.

Research the git history and PR references to find the correct `pr-url` for when each API was first added. Use `git log -S` on the doc files, check merge commits, and verify PRs target the main branch (not backport branches).

After adding the history blocks, create a documentation guide at `docs/CLAUDE.md` that explains the API history migration workflow — the YAML format, how to research when APIs were added, placement rules, and key details about the schema. Also update the root `CLAUDE.md` to reference the API history linting command.

## Files to Look At

- `docs/api/global-shortcut.md` — globalShortcut module methods
- `docs/api/image-view.md` — ImageView class and methods
- `docs/api/in-app-purchase.md` — inAppPurchase module (has promisified methods)
- `docs/api/ipc-main.md` — ipcMain module methods
- `docs/api/ipc-renderer.md` — ipcRenderer module methods
- `docs/development/api-history-migration-guide.md` — existing migration guide for reference
- `docs/development/style-guide.md` — style rules (see "API History" section)
- `docs/api-history.schema.json` — YAML block schema
- `docs/breaking-changes.md` — cross-reference for deprecated/changed APIs
- `CLAUDE.md` — root agent config (needs lint command added)
