# Website: add claude.md

Source: [fleetdm/fleet#43815](https://github.com/fleetdm/fleet/pull/43815)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `website/.claude/CLAUDE.md`

## What to add / change

Changes:
- Added website/.claude/CLAUDE.md, a file to provide guidance to Claude code when working in the website folder.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
