# chore: add Phase Three (node smoke tests) to Node.js upgrade skill

Source: [electron/electron#51186](https://github.com/electron/electron/pull/51186)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/electron-node-upgrade/SKILL.md`
- `.claude/skills/electron-node-upgrade/references/phase-three-commit-guidelines.md`

## What to add / change

Backport of #51127

See that PR for details.


Notes: none

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
