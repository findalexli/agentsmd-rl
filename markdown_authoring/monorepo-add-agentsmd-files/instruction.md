# Add AGENTS.md files

Source: [inversify/monorepo#1002](https://github.com/inversify/monorepo/pull/1002)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `packages/container/examples/AGENTS.md`
- `packages/container/libraries/binding-decorators/AGENTS.md`
- `packages/container/libraries/common/AGENTS.md`
- `packages/container/libraries/container/AGENTS.md`
- `packages/container/libraries/core/AGENTS.md`
- `packages/container/libraries/plugin-dispose/AGENTS.md`
- `packages/container/libraries/plugin/AGENTS.md`
- `packages/container/libraries/strongly-typed/AGENTS.md`
- `packages/docs/tools/AGENTS.md`
- `packages/foundation/tools/AGENTS.md`
- `packages/framework/core/AGENTS.md`

## What to add / change

### Added
- Added `AGENTS.md` files

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
