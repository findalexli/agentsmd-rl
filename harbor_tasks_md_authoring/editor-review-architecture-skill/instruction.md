# review architecture skill

Source: [pascalorg/editor#280](https://github.com/pascalorg/editor/pull/280)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/review-architecture/SKILL.md`
- `.cursor/rules/tools.mdc`
- `.cursor/skills/review-architecture/SKILL.md`

## What to add / change

## What does this PR do?

Adding a skill to pre-auto review PRs. (`.claude/skills/review-architecture/SKILL.md`)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
