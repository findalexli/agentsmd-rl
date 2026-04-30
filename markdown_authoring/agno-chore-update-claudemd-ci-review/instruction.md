# chore: update CLAUDE.md CI review section

Source: [agno-agi/agno#6569](https://github.com/agno-agi/agno/pull/6569)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Updates CLAUDE.md CI section to reflect the actual plugin-based review approach
- Removes references to `/review-pr` (which was a custom command, not available in our repo)
- Documents the 10 specialized agents from `code-review` + `pr-review-toolkit` plugins
- Lists agno-specific review checks

## Type of change
- [x] Other (documentation update)

## Checklist
- [x] My code follows the coding style of this project
- [x] I have performed a self-review of my own code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
