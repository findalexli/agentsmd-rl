# Update AGENTS.md

Source: [saleor/saleor-dashboard#5865](https://github.com/saleor/saleor-dashboard/pull/5865)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

This PR updates AGENTS.md for better usage for coding agents:
- Removed `npm run test` since it is too slow for local development, added command for running single file
- Added knip command
- Added guidelines for resolving git conflicts
- Added guidelines for writing changesets and PR descriptions

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
