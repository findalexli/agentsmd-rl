# Remove allowed-tools section from SKILL.md files

Source: [matlab/skills#7](https://github.com/matlab/skills/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/matlab-live-script/SKILL.md`
- `skills/matlab-performance-optimizer/SKILL.md`
- `skills/matlab-test-generator/SKILL.md`
- `skills/matlab-uihtml-app-builder/SKILL.md`

## What to add / change

Deleted the 'allowed-tools' configuration from SKILL.md files for matlab-live-script, matlab-performance-optimizer, matlab-test-generator, and matlab-uihtml-app-builder to streamline skill definitions.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
