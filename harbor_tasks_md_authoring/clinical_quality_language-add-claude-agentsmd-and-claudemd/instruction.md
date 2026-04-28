# Add Claude AGENTS.md and CLAUDE.md as outputs of Claude /init.

Source: [cqframework/clinical_quality_language#1699](https://github.com/cqframework/clinical_quality_language/pull/1699)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

- Add Claude AGENTS.md and CLAUDE.md as outputs of Claude /init.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
