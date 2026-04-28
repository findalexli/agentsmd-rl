# chore: add `AGENTS.md`

Source: [langchain-ai/langchain#33076](https://github.com/langchain-ai/langchain/pull/33076)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

it would be super cool if Anthropic supported this instead of `CLAUDE.md` :/

https://agents.md/

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
