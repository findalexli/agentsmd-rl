# feat: Update AGENTS.md to reference organization-wide patterns

Source: [ddev/ddev#7659](https://github.com/ddev/ddev/pull/7659)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## The Issue

- https://github.com/ddev/.github/pull/1

Global source for general AGENTS.md information.

This should go in after that one.

## How This PR Solves The Issue

- Add reference to ddev/.github/AGENTS.md for shared development patterns
- Focus project-specific content on core DDEV development
- Remove duplication of general DDEV organization practices
- Implement manual import pattern for AI agent instructions
- Maintain project-specific Go development, architecture, and testing guidance

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
