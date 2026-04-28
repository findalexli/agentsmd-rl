# Update references to WORKFLOWS.md in SKILL.md

Source: [gastownhall/beads#772](https://github.com/gastownhall/beads/pull/772)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/beads/SKILL.md`

## What to add / change

Updated references in SKILL.md to point to WORKFLOWS.md instead of ADVANCED_WORKFLOWS.md.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
