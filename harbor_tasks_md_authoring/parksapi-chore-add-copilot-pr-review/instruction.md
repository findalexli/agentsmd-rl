# chore: add Copilot PR review instructions

Source: [ThemeParks/parksapi#144](https://github.com/ThemeParks/parksapi/pull/144)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

## Summary
- Adds \`.github/copilot-instructions.md\` so Copilot's PR reviewer has project context
- Documents the conventions Copilot has been re-flagging on every park PR (empty-string config defaults, \`this\` typing in inject callbacks)
- Covers the standard park skeleton, status/wait-time mapping, TTL conventions, and the audit checks

## Why
Copilot has flagged the same two false-positives on PRs #142 (Blackpool) and #143 (Fuji-Q):

1. \"\`apiBase\` defaults to empty string, validate before using\" — but empty-string defaults are CLAUDE.md convention
2. \"Add \`this: ClassName\` to the inject callback\" — but no other park does this and tsc passes

This file is the canonical place to pin those decisions so the next park PR doesn't waste round-trips litigating the same points.

## Test plan
- [ ] After merge, watch the next park PR and confirm Copilot's review reflects the new context (skips the two known false-positives)
- [ ] Iterate the file if Copilot finds another recurring false-positive

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
