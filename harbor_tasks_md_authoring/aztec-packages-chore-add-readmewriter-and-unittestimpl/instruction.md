# chore: Add readme-writer and unit-test-impl Claude skills

Source: [AztecProtocol/aztec-packages#19230](https://github.com/AztecProtocol/aztec-packages/pull/19230)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `yarn-project/.claude/skills/readme-writer/SKILL.md`
- `yarn-project/.claude/skills/unit-test-implementation/SKILL.md`

## What to add / change

Adds two new skills for Claude for working on yarn project: one for writing READMEs at the module level, and one for guidelines on implementing unit tests.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
