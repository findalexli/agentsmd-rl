# Merge nightly: update Claude Code compatibility to v2.1.33

Source: [rz1989s/claude-code-statusline#235](https://github.com/rz1989s/claude-code-statusline/pull/235)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Update Claude Code compatibility range from v2.1.29 to v2.1.33
- Verified all 443 tests pass with v2.1.33 JSON input
- No breaking changes in v2.1.33

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
