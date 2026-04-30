# docs: add Git commit and PR conventions to CLAUDE.md

Source: [ryoppippi/ccusage#646](https://github.com/ryoppippi/ccusage/pull/646)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add comprehensive commit message and PR title conventions for the monorepo
- Define scope naming rules for apps, packages, documentation, and root-level changes
- Follow Conventional Commits specification

## Changes
- Apps use directory name as scope (e.g., `feat(ccusage):`, `fix(mcp):`)
- Packages use package directory name (e.g., `feat(terminal):`, `fix(ui):`)
- Documentation uses `docs` scope or `docs(guide):`, `docs(api):` for specific areas
- Root-level changes use no scope (preferred) or `root` scope
- Include examples for clarity

## Test plan
- [x] Reviewed CLAUDE.md for consistency
- [x] Verified commit message follows the new convention
- [x] PR title follows the new convention

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
