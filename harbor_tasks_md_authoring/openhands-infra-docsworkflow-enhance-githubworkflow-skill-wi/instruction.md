# docs(workflow): enhance github-workflow skill with 10-step development process

Source: [zxkane/openhands-infra#12](https://github.com/zxkane/openhands-infra/pull/12)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/github-workflow/SKILL.md`
- `.claude/skills/github-workflow/references/review-commands.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Expand github-workflow skill from 7 to 10 steps with comprehensive development process
- Add support for multiple reviewer bots (Amazon Q, Codex, and others)
- Mandate strict workflow adherence in CLAUDE.md for all code changes

## Changes

### SKILL.md Updates
- **Step 2**: Explicitly require writing new unit tests for new functionality and updating E2E test cases
- **Steps 6-7**: Iterate on reviewer bot findings (Q, Codex, etc.) until no new positive findings
- **Steps 8-9**: Deploy to staging environment and run full E2E test suite
- **Step 10**: Report ready status with explicit "DO NOT MERGE" - user decides when to merge
- **PR Template**: Add checklist template and update requirements

### review-commands.md Updates
- Add Codex bot commands and username
- Update workflow to show both Q and Codex review triggers
- Add iteration step for continuous review loop

### CLAUDE.md Updates
- Add mandatory "Development Workflow" section at the top
- Require `/github-workflow` skill for ALL feature development and bug fixes
- Emphasize no shortcuts and no auto-merging

## Test plan

- [x] Build passes (`npm run build`)
- [x] Unit tests pass (`npm run test` - 78 tests)
- [x] CI checks pass
- [x] Reviewer bot findings addressed (Amazon Q: no issues found)
- [x] Deployed to staging (N/A - docs only change)
- [x] E2E tests pass (N/A - docs only change)

## Checklist

- [x] Documentation updated
- [x] Skill loads correctly in Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
