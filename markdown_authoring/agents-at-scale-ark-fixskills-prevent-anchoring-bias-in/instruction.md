# fix(skills): prevent anchoring bias in issue-creation task breakdowns

Source: [mckinsey/agents-at-scale-ark#1905](https://github.com/mckinsey/agents-at-scale-ark/pull/1905)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/issue-creation/SKILL.md`

## What to add / change

## Summary

- Add guardrails to the issue-creation skill that prevent uninformed implementation details from leaking into task breakdowns
- Clarify that codebase research belongs in the Context section for orientation, not in tasks as prescriptive steps
- Rewrite task breakdown template to enforce problem-level descriptions (WHAT, not HOW)
- Add new rules: "no uninformed specificity" and "tasks describe WHAT not HOW" with concrete good/bad examples
- Prevent anchoring bias where issue authors without deep codebase knowledge over-constrain implementers

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
