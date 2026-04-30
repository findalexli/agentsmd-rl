# CLAUDE.md: update

Source: [cockroachdb/cockroach#161782](https://github.com/cockroachdb/cockroach/pull/161782)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `pkg/sql/CLAUDE.md`

## What to add / change

I read through the file and made some updates. One prompt for this was that comment styles are regularly off, so that section was cleaned up in particular. In other places, I mostly condensed a bit - pointing the agent at the `--help` functions of the tool if it needed to know more details.

Epic: none

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
