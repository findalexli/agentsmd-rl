# feat: optimize SKILL.md description

Source: [callstackincubator/agent-skills#2](https://github.com/callstackincubator/agent-skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/react-native-best-practices/SKILL.md`

## What to add / change

### Summary

Optimized the skill description according to best practices from https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
