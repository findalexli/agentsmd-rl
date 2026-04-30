# docs: update AGENTS.md with detailed review process for provider skills

Source: [hookdeck/webhook-skills#20](https://github.com/hookdeck/webhook-skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

- Added a structured three-step review process for evaluating provider skills, including running automated reviews, verifying integration, and spot-checking skill content.
- Included quick commands for running tests on specific skills and all examples.
- Enhanced clarity on required sections in SKILL.md and integration checks in repository infrastructure.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
