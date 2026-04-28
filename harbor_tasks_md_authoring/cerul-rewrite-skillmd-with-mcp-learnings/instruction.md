# Rewrite SKILL.md with MCP learnings

Source: [cerul-ai/cerul#132](https://github.com/cerul-ai/cerul/pull/132)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/cerul/SKILL.md`

## What to add / change

Apply blindspot strategy, speaker hint, performance defaults, CLI integration.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
