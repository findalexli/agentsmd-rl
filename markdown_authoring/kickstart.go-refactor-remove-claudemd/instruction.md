# refactor: remove CLAUDE.md

Source: [raeperd/kickstart.go#81](https://github.com/raeperd/kickstart.go/pull/81)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Remove CLAUDE.md — all content was derivable from the codebase itself (Makefile targets, code structure, test patterns, and comments)

## Test plan
- [x] `make build` and `make test` pass

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
