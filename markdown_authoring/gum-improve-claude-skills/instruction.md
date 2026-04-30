# Improve claude skills

Source: [vchelaru/Gum#2262](https://github.com/vchelaru/Gum/pull/2262)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/gum-property-assignment/SKILL.md`
- `.claude/skills/gum-tool-plugins/SKILL.md`
- `.claude/skills/gum-tool-save-classes/SKILL.md`
- `.claude/skills/gum-tool-selection/SKILL.md`
- `.claude/skills/gum-tool-undo/SKILL.md`
- `.claude/skills/gum-tool-variable-grid/SKILL.md`
- `.claude/skills/variable-grid/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
