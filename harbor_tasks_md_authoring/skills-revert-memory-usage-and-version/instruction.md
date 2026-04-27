# revert memory usage and version upgrade skills

Source: [qdrant/skills#20](https://github.com/qdrant/skills/pull/20)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-performance-optimization/memory-usage-optimization/SKILL.md`
- `skills/qdrant-version-upgrade/SKILL.md`

## What to add / change

Reverts the memory usage optimization and version upgrade skills back to Andre's original versions, with minor typo fixes.

- memory-usage-optimization: reverted from rewrite, fixed typos (cahce, exmaple, importat, inferece, etc.)
- version-upgrade: reverted from rewrite, fixed "have" → "has"
- indexing-performance: was never overwritten, unchanged

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
