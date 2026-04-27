# Fix API key exposure in bria-ai skill setup

Source: [Bria-AI/bria-skill#26](https://github.com/Bria-AI/bria-skill/pull/26)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bria-ai/SKILL.md`

## What to add / change

## Summary
- Replaced direct `echo $BRIA_API_KEY` with a safe existence check that reports whether the key is set without printing the secret value
- Prevents accidental API key leakage in terminal output

## Test plan
- [ ] Verify skill setup flow works when `BRIA_API_KEY` is set
- [ ] Verify skill setup flow works when `BRIA_API_KEY` is not set
- [ ] Confirm the key value is never printed to the terminal

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
