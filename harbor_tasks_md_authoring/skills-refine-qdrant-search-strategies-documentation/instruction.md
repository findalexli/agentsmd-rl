# Refine Qdrant search strategies documentation

Source: [qdrant/skills#17](https://github.com/qdrant/skills/pull/17)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-search-quality/search-strategies/SKILL.md`

## What to add / change

Fixed some takes, added score boosting, rewrote relevance feedback

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
