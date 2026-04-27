# refactor: rewrite pr-review skill as review-only with design guidance

Source: [IBM/mcp-context-forge#3918](https://github.com/IBM/mcp-context-forge/pull/3918)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/pr-review/SKILL.md`

## What to add / change

## Summary
- Transforms the pr-review skill from a fix-and-report workflow to a **review-only** report — the skill no longer modifies files, it produces findings for the author to address
- Adds structured **design review guidance** covering modularity, OO/polymorphism opportunities, and missing abstractions
- Reorganizes output format into **severity-tiered tables** (Blocking / High / Medium) instead of a single flat table

**Note:** There are unresolved merge conflict markers in the Recommendation section that need to be cleaned up before merge.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
