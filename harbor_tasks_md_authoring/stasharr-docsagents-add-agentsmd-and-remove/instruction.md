# docs(agents): add AGENTS.md and remove CLAUDE.md

Source: [enymawse/stasharr#100](https://github.com/enymawse/stasharr/pull/100)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

- Add AGENTS.md for agentic coding assistants
- Document commands, code map, patterns, and validation
- Outline bulk ops UX rules (modal, skipped, empty-state)
- Remove outdated CLAUDE.md in favor of AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
