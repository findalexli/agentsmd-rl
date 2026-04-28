# Move engine/AGENTS.md into root AGENTS.md because Claude doesn't bother to read it

Source: [Stirling-Tools/Stirling-PDF#6151](https://github.com/Stirling-Tools/Stirling-PDF/pull/6151)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `engine/AGENTS.md`

## What to add / change

# Description of Changes
Move `engine/AGENTS.md` into root `AGENTS.md` because Claude doesn't bother to read it half the time.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
