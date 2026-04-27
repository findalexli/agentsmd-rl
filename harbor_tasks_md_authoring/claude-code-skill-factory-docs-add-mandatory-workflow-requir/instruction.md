# docs: Add mandatory workflow requirement to CLAUDE.md

Source: [alirezarezvani/claude-code-skill-factory#56](https://github.com/alirezarezvani/claude-code-skill-factory/pull/56)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Add mandatory workflow requirement to CLAUDE.md that enforces proper planning and GitHub issue tracking for all work.

## Changes

Added prominent section at top of CLAUDE.md requiring:
1. Plan mode first for all user requests
2. User approval of plan
3. Create GitHub issue with `plan` label
4. Automation creates subtasks via plan-to-issues workflow
5. Start implementation with proper tracking

## Why

- ✅ Ensures all work is properly tracked in GitHub
- ✅ Prevents scope creep with upfront planning
- ✅ Leverages plan-to-issues automation
- ✅ Provides team visibility and audit trail
- ✅ Establishes consistent workflow standard

## Related

- Issue #55 - Wiki documentation initiative (was started without following this workflow)

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
