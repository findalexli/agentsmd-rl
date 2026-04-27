# linking

Source: [kevmoo/dash_skills#7](https://github.com/kevmoo/dash_skills/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/dart-best-practices/SKILL.md`
- `.agent/skills/dart-checks-migration/SKILL.md`
- `.agent/skills/dart-matcher-best-practices/SKILL.md`
- `.agent/skills/dart-modern-features/SKILL.md`
- `.agent/skills/dart-test-fundamentals/SKILL.md`

## What to add / change

- **Link the test skills together**
- **Link Dart best practices things together**

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
