# Add preview feature gating instructions to CLAUDE.md

Source: [rue-language/rue#453](https://github.com/rue-language/rue/pull/453)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Document the complete workflow for gating new language features behind preview flags. This addresses a gap where the PreviewFeature enum and test infrastructure were being set up, but the critical require_preview() call in Sema was being missed.

Key additions:
- When to use preview gating (new syntax, type system features, multi-phase work)
- Step-by-step gating instructions including the Sema gate check
- How to test that the gate actually works
- Stabilization workflow when feature is complete
- Inline reminders in implementation steps 5 and 7

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
