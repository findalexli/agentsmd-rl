# Website: Update website/.claude/CLAUDE.md

Source: [fleetdm/fleet#44063](https://github.com/fleetdm/fleet/pull/44063)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `website/.claude/CLAUDE.md`

## What to add / change

Changes:
- Added more guidance for generating new pages to the website's claude.md file

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
