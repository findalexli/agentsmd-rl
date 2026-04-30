# Require lint before pushing remote code updates

Source: [entireio/cli#1003](https://github.com/entireio/cli/pull/1003)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

https://entire.io/gh/entireio/cli/trails/9ae25d16129b

## Summary
Add explicit repo guidance requiring agents to run `mise run lint` and confirm it passes before pushing or otherwise sending code changes to a remote.

## Implementation
Update the repo-level agent instructions to:
- require a passing `mise run lint` before any push or remote code update
- require rerunning lint after formatting if `mise run fmt` changed files

## Verification
- `mise run check`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
