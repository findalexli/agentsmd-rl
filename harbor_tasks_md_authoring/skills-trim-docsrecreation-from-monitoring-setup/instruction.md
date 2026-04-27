# trim docs-recreation from monitoring setup skill

Source: [qdrant/skills#12](https://github.com/qdrant/skills/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-monitoring/setup/SKILL.md`

## What to add / change

Remove metric categories reference block and collapse health probe endpoint list to single line. Agent can get this from the docs links.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
