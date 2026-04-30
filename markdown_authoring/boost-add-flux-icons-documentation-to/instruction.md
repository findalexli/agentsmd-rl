# Add Flux Icons documentation to SKILL.md files

Source: [laravel/boost#494](https://github.com/laravel/boost/pull/494)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.ai/fluxui-free/skill/fluxui-development/SKILL.md`
- `.ai/fluxui-pro/skill/fluxui-development/SKILL.md`

## What to add / change

Added Icons section to both `fluxui-free` and `fluxui-pro` SKILL.md files documenting Heroicons as the default icon set and Lucide as an alternative addresses issue where AI assistants invent non-existent icon names (e.g., download instead of arrow-down-tray)

Fixes #177

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
