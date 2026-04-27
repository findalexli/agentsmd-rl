# docs: SKILL.md metadata 更新

Source: [Panniantong/Agent-Reach#143](https://github.com/Panniantong/Agent-Reach/pull/143)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `agent_reach/skill/SKILL.md`

## What to add / change

加 homepage 链接、更新渠道数到 14、description 开头加 7500+ stars。

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
