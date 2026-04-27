# Add a separate SKILL.md for openclaw.

Source: [imbue-ai/latchkey#39](https://github.com/imbue-ai/latchkey/pull/39)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `integrations/SKILL.md`
- `integrations/openclaw/SKILL.md`

## What to add / change

`latchkey auth browser` is not applicable in OpenClaw, anyway. (And the mention of it tripped up their security scanner.)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
