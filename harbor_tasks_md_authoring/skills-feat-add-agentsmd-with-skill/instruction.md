# feat: add agents.md with skill path sync instruction

Source: [langfuse/skills#16](https://github.com/langfuse/skills/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agents.md`

## What to add / change

## Summary
- Adds `agents.md` with an instruction to keep the CLI repo in sync whenever a Langfuse skill path changes in this repo.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
