# Add component description validation to Figma to Code skill

Source: [scoobynko/claude-code-design-skills#5](https://github.com/scoobynko/claude-code-design-skills/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `figma-to-code/SKILL.md`

## What to add / change

- Extract and respect component descriptions as authoritative usage guidelines
- Display warnings when implementations conflict with description guidelines
- Add validation steps to final checklist
- Document deviations in code comments when conflicts occur

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
