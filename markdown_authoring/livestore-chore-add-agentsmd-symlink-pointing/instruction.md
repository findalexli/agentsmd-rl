# chore: add AGENTS.md symlink pointing to CLAUDE.md

Source: [livestorejs/livestore#628](https://github.com/livestorejs/livestore/pull/628)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Creates a symlink `AGENTS.md` pointing to `CLAUDE.md` for easier agent documentation discovery

## Test plan
- [ ] Verify symlink works correctly: `ls -la AGENTS.md`
- [ ] Confirm content is accessible through both filenames

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
