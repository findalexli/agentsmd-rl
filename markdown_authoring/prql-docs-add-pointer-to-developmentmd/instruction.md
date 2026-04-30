# docs: Add pointer to development.md for releases and environment

Source: [PRQL/prql#5553](https://github.com/PRQL/prql/pull/5553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Add a concise "Releases & Environment" section to CLAUDE.md that points to the detailed development documentation.

This helps Claude know where to find information about releases or environment issues without cluttering CLAUDE.md with detailed procedures.

## Test plan

- [x] Documentation-only change
- [x] Points to correct file path

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
