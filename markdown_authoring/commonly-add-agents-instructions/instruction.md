# Add AGENTS instructions

Source: [Team-Commonly/commonly#10](https://github.com/Team-Commonly/commonly/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- document how Codex should lint and test the project
- expand AGENTS with project structure and architecture overview

## Testing
- `npm run lint`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
