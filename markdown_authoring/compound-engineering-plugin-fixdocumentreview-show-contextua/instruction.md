# fix(document-review): show contextual next-step in Phase 5 menu

Source: [EveryInc/compound-engineering-plugin#459](https://github.com/EveryInc/compound-engineering-plugin/pull/459)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/document-review/SKILL.md`

## What to add / change

## Summary

The "Review complete" option in document-review's interactive Phase 5 menu described itself as "document is ready", which was vague enough that the model would embellish it with incorrect caller context — e.g., "proceed to brainstorm handoff" when running inside ce:brainstorm, where the actual next step is planning.

Now uses the document type classification that Phase 1 already performs to show the concrete next workflow step: requirements docs get "Create technical plan with ce:plan", plan docs get "Implement with ce:work". No new flags or caller coordination needed — document-review already knows the document type.

## Test plan

- [ ] Run ce:brainstorm through to document-review and verify the "Review complete" option says "Create technical plan with ce:plan"
- [ ] Run ce:plan through to document-review and verify the "Review complete" option says "Implement with ce:work"
- [ ] Run document-review standalone on a requirements doc and verify the same contextual description appears

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
