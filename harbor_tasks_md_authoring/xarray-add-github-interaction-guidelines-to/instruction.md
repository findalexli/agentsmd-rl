# Add GitHub interaction guidelines to CLAUDE.md

Source: [pydata/xarray#10715](https://github.com/pydata/xarray/pull/10715)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Added explicit GitHub interaction guidelines to CLAUDE.md to ensure appropriate behavior when working with the xarray repository
- Guidelines prevent unsolicited GitHub actions and require explicit user authorization

## Changes
- Added new section "GitHub Interaction Guidelines" with clear rules about:
  - Not impersonating users on GitHub
  - Requiring explicit authorization for creating issues/PRs
  - Not posting unsolicited comments or updates

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
