# refactor: decompose kotlin-coroutines SKILL.md into references

Source: [notque/claude-code-toolkit#424](https://github.com/notque/claude-code-toolkit/pull/424)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/kotlin-coroutines/SKILL.md`
- `skills/kotlin-coroutines/references/anti-patterns.md`
- `skills/kotlin-coroutines/references/channel-patterns.md`
- `skills/kotlin-coroutines/references/concurrency-patterns.md`
- `skills/kotlin-coroutines/references/flow-patterns.md`

## What to add / change

## Summary
- Decomposed kotlin-coroutines SKILL.md from 385 lines to 60 lines
- Created 4 reference files: concurrency-patterns.md, flow-patterns.md, channel-patterns.md, anti-patterns.md
- Zero content loss: all 13 original sections preserved

## Test plan
- [ ] All content preserved in reference files
- [ ] Reference Loading Table present
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
