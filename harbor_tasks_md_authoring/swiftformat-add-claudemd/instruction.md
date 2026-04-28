# Add `CLAUDE.md`

Source: [nicklockwood/SwiftFormat#2288](https://github.com/nicklockwood/SwiftFormat/pull/2288)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

This PR adds a `CLAUDE.md` file based on the prompt template that I've been using most of the year. This sort of content has worked well for using Claude to create new SwiftFormat rules.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
