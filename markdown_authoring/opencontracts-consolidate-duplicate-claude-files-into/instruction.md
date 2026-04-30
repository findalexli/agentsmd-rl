# Consolidate duplicate Claude files into single CLAUDE.md

Source: [Open-Source-Legal/OpenContracts#732](https://github.com/Open-Source-Legal/OpenContracts/pull/732)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `Claude.md`

## What to add / change

## Summary
- Deletes duplicate `Claude.md` which contained outdated information (wrong branch strategy referencing `v3.0.0.b3`, non-existent `activeLayerAtom` reference)
- Updates Unified Filtering Architecture section in `CLAUDE.md` to correctly reference Apollo reactive vars (`showStructuralAnnotations`, `showSelectedAnnotationOnly` in `cache.ts`) instead of deprecated Jotai atoms
- Verified all statements in `CLAUDE.md` against the codebase using 6 parallel exploration agents

## Verification performed
- Backend commands (test.yml, local.yml, production.yml, pytest-xdist): All accurate
- Frontend commands (yarn scripts): All accurate
- All 9 documentation file paths: All exist
- GraphQL schema organization: Accurate
- Central Routing System description: Accurate
- Branch strategy (trunk-based development): Accurate

## Test plan
- [x] No code changes, documentation only
- [x] Verified CLAUDE.md content accuracy against codebase

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
