# add tilelang pass design skill

Source: [tile-ai/tilelang-ascend#897](https://github.com/tile-ai/tilelang-ascend/pull/897)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/tilelang-pass-design/SKILL.md`
- `.agents/skills/tilelang-pass-design/references/pass-impl-patterns.md`
- `.agents/skills/tilelang-pass-design/templates/pass-design-template.md`

## What to add / change

add tilelang pass design skill.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
