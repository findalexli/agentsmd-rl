# Reorg scaling skills

Source: [qdrant/skills#19](https://github.com/qdrant/skills/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/qdrant-scaling/SKILL.md`
- `skills/qdrant-scaling/performance-scaling/SKILL.md`
- `skills/qdrant-scaling/performance-scaling/horizontal-scaling/SKILL.md`
- `skills/qdrant-scaling/performance-scaling/vertical-scaling/SKILL.md`

## What to add / change

- Create umbrella `performance-scaling` skill that discusses vertical versus horizontal scaling
- Move `horizontal-scaling` skill
- Create `vertical-scaling` skill
- Emphasize vertical scaling at all costs prior to horizontal scaling since horizontal scaling is seen as irreversible

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
