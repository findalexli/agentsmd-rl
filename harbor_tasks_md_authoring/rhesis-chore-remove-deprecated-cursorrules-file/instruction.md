# chore: remove deprecated .cursorrules file

Source: [rhesis-ai/rhesis#1254](https://github.com/rhesis-ai/rhesis/pull/1254)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/.cursorrules`

## What to add / change

## Summary
- Removes the deprecated `.cursor/rules/.cursorrules` file
- The `.cursorrules` format is deprecated in favor of the `.mdc` rule files already present in the `.cursor/rules` directory

## Test plan
- [x] Verify Cursor IDE still loads rules from `.mdc` files

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
