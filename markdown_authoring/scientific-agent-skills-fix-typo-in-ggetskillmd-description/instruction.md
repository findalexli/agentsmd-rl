# Fix typo in gget/SKILL.md description

Source: [K-Dense-AI/scientific-agent-skills#28](https://github.com/K-Dense-AI/scientific-agent-skills/pull/28)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `scientific-skills/gget/SKILL.md`

## What to add / change

Fix YAML syntax error in gget SKILL.md description

Summary

Fixed invalid YAML syntax in the gget SKILL.md that was preventing the skill from loading properly.

Changes

- Wrapped the description field value in quotes to escape the colon in "lookups:"
- The unquoted colon at column 92 was being interpreted as a YAML mapping operator, causing a parse error

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
