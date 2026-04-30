# Add Performance optimization skills

Source: [qdrant/skills#5](https://github.com/qdrant/skills/pull/5)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-performance-optimization/indexing-performance-optimization/SKILL.md`
- `skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md`
- `skills/qdrant-performance-optimization/search-speed-optimization/SKILL.md`

## What to add / change

Add indexing, search speed, and memory skills

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
