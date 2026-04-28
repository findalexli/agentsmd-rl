#  feat: Add milestone-check skill for post-contest blog candidate detection (#12013)

Source: [KATO-Hiro/AtCoderClans#12014](https://github.com/KATO-Hiro/AtCoderClans/pull/12014)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/architecture.md`
- `.claude/rules/workflow.md`
- `.claude/skills/milestone-check/SKILL.md`
- `.claude/skills/milestone-check/instructions.md`

## What to add / change

close #12013

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
