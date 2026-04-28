# chore: added CLAUDE.md alias

Source: [huggingface/transformers#44232](https://github.com/huggingface/transformers/pull/44232)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

# What does this PR do?

per https://code.claude.com/docs/en/claude-code-on-the-web#best-practices 

`CLAUDE.md` can alias directly into `AGENTS.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
