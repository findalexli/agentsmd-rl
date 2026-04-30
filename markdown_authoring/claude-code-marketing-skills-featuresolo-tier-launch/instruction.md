# Feature/solo tier launch

Source: [cognyai/claude-code-marketing-skills#1](https://github.com/cognyai/claude-code-marketing-skills/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/cogny/SKILL.md`
- `skills/linkedin-ads-audit/SKILL.md`
- `skills/seo-audit/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
