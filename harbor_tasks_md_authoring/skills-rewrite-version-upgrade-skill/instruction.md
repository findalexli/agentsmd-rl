# rewrite version upgrade skill

Source: [qdrant/skills#13](https://github.com/qdrant/skills/pull/13)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-version-upgrade/SKILL.md`

## What to add / change

symptom sections, trigger phrases, What NOT to Do, preserves Andre's SDK ordering recommendation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
