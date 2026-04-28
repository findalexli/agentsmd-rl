# Update TypeScript typing guidelines in CLAUDE.md

Source: [levu304/claude-code-boilerplate#2](https://github.com/levu304/claude-code-boilerplate/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Ban `any` type absolutely - no exceptions including test files
- Allow `unknown` but recommend avoiding it in favor of explicit types
- Add comprehensive examples for proper typing patterns
- Include guidance for handling third-party library types

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
