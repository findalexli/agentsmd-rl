# Apply learnings from real-world testing to /think and /ship

Source: [garagon/nanostack#21](https://github.com/garagon/nanostack/pull/21)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `ship/SKILL.md`
- `think/SKILL.md`

## What to add / change

## Summary

- /think: Search Before Building is now Phase 1.5 (mandatory step before the diagnostic). Searches existing tools, prior art, GitHub issues/PRs.
- /ship: PR Preview is now a mandatory stop before creating the PR. Waits for user approval.
- Both skills now include anti-patterns discovered from real-world usage.

## Test plan

- [ ] Run /think and verify Phase 1.5 runs before the diagnostic
- [ ] Run /ship and verify PR Preview appears before PR creation

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
