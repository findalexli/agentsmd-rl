# docs: remove broken roadmap link from SKILL.md

Source: [callstackincubator/agent-device#14](https://github.com/callstackincubator/agent-device/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-device/SKILL.md`

## What to add / change

Removes a broken link to a non-existent roadmap file from the agent-device skill.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
