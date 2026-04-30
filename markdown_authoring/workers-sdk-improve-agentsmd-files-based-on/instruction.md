# Improve AGENTS.md files based on recurring PR review feedback

Source: [cloudflare/workers-sdk#13408](https://github.com/cloudflare/workers-sdk/pull/13408)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `packages/miniflare/AGENTS.md`
- `packages/wrangler/AGENTS.md`

## What to add / change

_Analyzed review comments from the last 100 merged PRs to identify recurring patterns that should be codified in agent guidance._

## Changes

### Root `AGENTS.md`

**Code Style** (3 new rules):
- Prefer `function` declarations over `const` arrow functions for named/exported functions
- ESLint disable comments must use `--` double-dash separator before reason
- Never modify generated files directly — modify the generator/config instead

**Testing Standards** (6 new items):
- Full `expect` from test context pattern with sub-bullets covering destructured context, `ExpectStatic` parameter passing, `import type` usage, `node:assert` fallback, and the E2E `globals: true` caveat
- Snapshot update reminder when changing user-facing strings
- Test fixture `tsconfig.json` requirement for `vitest-pool-workers-examples/`
- Test fixtures as user-facing recipes (avoid type casting)

**Changesets** (1 new rule):
- Focus on user-facing impact; reference the public-facing package, not internal packages

**Anti-Patterns** (2 new entries):
- Trivial/obvious code comments (explain "why" not "what")
- Cross-package type/constant duplication

**Subdirectory Knowledge**:
- Keep AGENTS.md files updated when making architectural changes

### `packages/wrangler/AGENTS.md`

- E2E vitest config `globals: true` caveat (most common source of `ReferenceError` bugs)
- Check ALL call sites when adding `expect` parameter to helpers

### `packages/miniflare/AGENTS.md`

- New "Generated Files" section document

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
