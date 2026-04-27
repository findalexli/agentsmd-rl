# search quality skill

Source: [qdrant/skills#7](https://github.com/qdrant/skills/pull/7)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-search-quality/SKILL.md`
- `skills/qdrant-search-quality/diagnosis/SKILL.md`
- `skills/qdrant-search-quality/search-strategies/SKILL.md`

## What to add / change

fill in search quality skill stub

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
