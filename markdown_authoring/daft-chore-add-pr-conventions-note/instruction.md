# chore: add PR conventions note to AGENTS.md

Source: [Eventual-Inc/Daft#5166](https://github.com/Eventual-Inc/Daft/pull/5166)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Changes Made

- Add PR conventions note to AGENTS.md
- Add CLAUDE.md symlink to AGENTS.md

## Related Issues

- Related PR: #5124

## Checklist

- [x] Documentation builds and is formatted properly (tag @/ccmao1130 for docs review)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
