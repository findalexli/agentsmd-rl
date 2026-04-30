# Feature/161 add adr drafting skill

Source: [giuseppe-trisciuoglio/developer-kit#164](https://github.com/giuseppe-trisciuoglio/developer-kit/pull/164)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/developer-kit-core/skills/adr-drafting/SKILL.md`

## What to add / change

Review skills

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
