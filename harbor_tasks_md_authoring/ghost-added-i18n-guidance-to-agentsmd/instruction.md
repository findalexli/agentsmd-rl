# Added i18n guidance to AGENTS.md

Source: [TryGhost/Ghost#27177](https://github.com/TryGhost/Ghost/pull/27177)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Expanded the i18n Architecture section in AGENTS.md with practical rules for developers and AI agents
- Documents the translation workflow (`yarn translate`), CI enforcement, and key rules:
  - Never split sentences across multiple `t()` calls
  - Always provide context descriptions in `context.json`
  - Use `@doist/react-interpolate` for inline elements (`<a>`, `<strong>`, etc.)
  - Use `{variable}` interpolation for dynamic values
- Includes correct/incorrect code examples and a reference to the canonical example

### Why
Translation contributors flagged that split-sentence keys prevent proper localization. This documentation ensures developers and agents building new features know the rules without needing to discover them through trial and error.

## Test plan
- [ ] Review the added documentation for accuracy and completeness

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
