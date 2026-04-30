# Add the `compatibility` field to SKILL.md.

Source: [imbue-ai/latchkey#6](https://github.com/imbue-ai/latchkey/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `integrations/SKILL.md`

## What to add / change

Based on the agent skills spec: https://agentskills.io/specification#compatibility-field

Once it's in place, we can submit the skill to marketplaces like https://skillsmp.com/.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
