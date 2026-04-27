# docs(claude): enforce worktree usage and strict github-workflow adherence

Source: [zxkane/openhands-infra#41](https://github.com/zxkane/openhands-infra/pull/41)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Strengthens CLAUDE.md Development Workflow section with explicit numbered rules and common violation callouts to ensure Claude Code consistently follows the required process across all machines and team members.

**Changes:**
- **Rule 1**: Always invoke `github-workflow` skill before any code changes — with callout for the common violation of skipping skill invocation
- **Rule 2**: Always use git worktrees for code changes — with exact commands and callout for the common violation of using `git checkout -b` directly
- **Rule 3**: Complete all 10 workflow steps — explicit step-by-step summary with emphasis on worktree in Step 1

## Test plan

- [x] Docs-only change — no build/test/deploy needed
- [x] Verified CLAUDE.md renders correctly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
