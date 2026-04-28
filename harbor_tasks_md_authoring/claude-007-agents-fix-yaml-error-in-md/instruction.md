# Fix yaml error in md file

Source: [avivl/claude-007-agents#4](https://github.com/avivl/claude-007-agents/pull/4)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/ai/computer-vision-specialist.md`

## What to add / change

The --- is a yaml document separator notation, this is why GitHub tries to parse ad yaml.
Closing the metadata section with it seem to solve this.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
