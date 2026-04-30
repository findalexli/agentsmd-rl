# chore(skill): add testing plan step to new-feature-design skill (v1.5)

Source: [agentic-community/mcp-gateway-registry#872](https://github.com/agentic-community/mcp-gateway-registry/pull/872)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/new-feature-design/SKILL.md`

## What to add / change

## Summary

Extends the `new-feature-design` skill to emit a fourth deliverable: `testing.md`, alongside the existing `github-issue.md`, `lld.md`, and `review.md`. The testing plan covers:

- Functional tests (curl + `registry_management.py`)
- Backwards-compatibility tests
- UX checks
- ECS / terraform env-var plumbing
- End-to-end API tests

Also bumps frontmatter version 1.4 → 1.5, updates both workflow sequences (User Description and GitHub Issue URL modes), refreshes the folder-structure snippet, and adds concrete testing-plan items to the rate-limiting usage example.

## Context

A direct-to-main commit (`4f5c9ca`) was reverted (`5a3cb07`) so this change can land via review. Re-applied on a fresh branch on top of current `main`.

## Test plan

- [ ] Invoke the skill against a new GitHub issue URL and confirm `testing.md` is created alongside the other three docs.
- [ ] Invoke the skill in user-description mode and confirm the same.
- [ ] Confirm the SKILL.md renders without layout regressions wherever it is consumed.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
