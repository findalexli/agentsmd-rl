# refactor: decompose swift-concurrency SKILL.md into references

Source: [notque/claude-code-toolkit#423](https://github.com/notque/claude-code-toolkit/pull/423)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/swift-concurrency/SKILL.md`
- `skills/swift-concurrency/references/actor-isolation.md`
- `skills/swift-concurrency/references/anti-patterns.md`
- `skills/swift-concurrency/references/fundamentals.md`
- `skills/swift-concurrency/references/task-patterns.md`

## What to add / change

## Summary
- Decomposed swift-concurrency SKILL.md from 423 lines to 43 lines
- Created 4 reference files: fundamentals.md, actor-isolation.md, task-patterns.md, anti-patterns.md
- Zero content loss: all 13 Swift code blocks preserved in reference files
- SKILL.md is now a thin orchestrator with Reference Loading Table per PHILOSOPHY.md

## Test plan
- [ ] All code examples from original exist in exactly one reference file
- [ ] Reference Loading Table maps signals to correct files
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
