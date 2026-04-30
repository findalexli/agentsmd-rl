# docs(agents): add IPC, leasing, library API, and retention references

Source: [benbjohnson/litestream#1107](https://github.com/benbjohnson/litestream/pull/1107)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Add IPC and Leasing rows to Layer Boundaries table
- Add critical rules for retention defaults, IPC socket, `$PID` expansion, and `ltx -level` flag
- Add `docs/PROVIDER_COMPATIBILITY.md` to Documentation table
- Update DB and Storage layer descriptions with new APIs

Refs #1106 (Task 1)

## Test plan
- [x] Verified all code references against source (`server.go`, `store.go`, `leaser.go`, `db.go`, `cmd/litestream/main.go`)
- [x] Build passes: `go build ./cmd/litestream`
- [x] Pre-commit passes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
