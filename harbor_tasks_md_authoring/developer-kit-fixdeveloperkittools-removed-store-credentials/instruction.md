# fix(developer-kit-tools): removed store credentials

Source: [giuseppe-trisciuoglio/developer-kit#165](https://github.com/giuseppe-trisciuoglio/developer-kit/pull/165)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md`

## What to add / change

See the PR for the intended changes to the listed file(s).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
