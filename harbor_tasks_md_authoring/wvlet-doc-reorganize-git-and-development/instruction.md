# doc: Reorganize Git and development workflow sections in CLAUDE.md

Source: [wvlet/wvlet#1170](https://github.com/wvlet/wvlet/pull/1170)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Consolidated scattered Git-related instructions into unified "Git & Development Workflow" section
- Merged Development Workflow, Commit Guidance, and PR Checks sections
- Added GitHub CLI commands to main Git workflow section
- Reorganized content for better logical flow and discoverability
- Added instruction to switch to main and pull after PR merge

## Test plan
- [x] Verify CLAUDE.md formatting and structure is correct
- [x] Confirm all consolidated sections maintain their information

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
