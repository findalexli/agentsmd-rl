# Add instructions about JSON newline escaping to avoid common mistakes

Source: [kepano/obsidian-skills#32](https://github.com/kepano/obsidian-skills/pull/32)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/json-canvas/SKILL.md`

## What to add / change

Added a "Newline Escaping (Common Pitfall)" section to `skills/json-canvas/SKILL.md`, explaining that newlines in JSON strings must be represented as `\n`, and showing examples of correct and incorrect usage.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
