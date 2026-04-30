# DEV-1480: Reorganize AGENTS.md -- shrink root file, distribute content to subpackages

Source: [handsontable/handsontable#12431](https://github.com/handsontable/handsontable/pull/12431)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `docs/AGENTS.md`
- `docs/AGENTS.md`
- `docs/CLAUDE.md`
- `docs/CLAUDE.md`
- `handsontable/AGENTS.md`
- `handsontable/CLAUDE.md`
- `handsontable/CLAUDE.md`
- `handsontable/src/3rdparty/walkontable/AGENTS.md`
- `handsontable/src/3rdparty/walkontable/CLAUDE.md`
- `handsontable/src/3rdparty/walkontable/CLAUDE.md`
- `visual-tests/AGENTS.md`
- `visual-tests/CLAUDE.md`
- `visual-tests/CLAUDE.md`
- `wrappers/angular-wrapper/AGENTS.md`
- `wrappers/angular-wrapper/CLAUDE.md`
- `wrappers/angular-wrapper/CLAUDE.md`
- `wrappers/react-wrapper/AGENTS.md`
- `wrappers/react-wrapper/CLAUDE.md`
- `wrappers/react-wrapper/CLAUDE.md`
- `wrappers/vue3/AGENTS.md`
- `wrappers/vue3/CLAUDE.md`
- `wrappers/vue3/CLAUDE.md`

## What to add / change

### Context

The root `AGENTS.md` was growing unboundedly as a single catch-all for monorepo-wide and package-specific knowledge. This PR reorganizes the AI context files: the root file is trimmed to cross-package concerns only, and package-specific rules are moved to the relevant subdirectory `AGENTS.md`.

### What changed

- **Root `AGENTS.md`** reduced from 446 → ~375 lines. Removed: package-specific pitfalls, `## Key file locations` (all `handsontable/src/` paths), Context menu vs column menu full table, Build outputs section, ClickUp Setup block (now a pointer to `.ai/MCP.md`), redundant Gotchas. Added: `## Skill discovery` task-to-skill lookup table, governance note on Common pitfalls.
- **`handsontable/AGENTS.md`** expanded with: key file locations, lint commands, build outputs, context menu comparison table, additional gotchas (Filters index, setTimeout/_registerTimeout, hook TypeScript regression), and package-specific pitfalls.
- **Wrapper `AGENTS.md` files** (`angular-wrapper`, `react-wrapper`, `vue3`) each gained a Common Pitfalls section and a Feature parity rule.
- **Symlinks**: all subpackages (`handsontable/`, `wrappers/*`, `visual-tests/`, `walkontable/`) now have `CLAUDE.md → AGENTS.md` so both Claude Code and Cursor can read the same file. `AGENTS.md` is the canonical file everywhere.

### How has this been tested?

No source code changed -- docs and AI context files only.

- [x] Verified symlinks resolve correctly (`ls -la` on all subpackages)
- [x] Verifi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
