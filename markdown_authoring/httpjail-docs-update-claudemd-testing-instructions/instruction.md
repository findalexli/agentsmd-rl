# docs: update CLAUDE.md testing instructions; remove HTTPJAIL_BIN

Source: [coder/httpjail#48](https://github.com/coder/httpjail/pull/48)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Summary
- Remove outdated instructions that referenced the HTTPJAIL_BIN environment variable.
- Update Integration Tests section to reflect current behavior: tests run against the Cargo-built binary (assert_cmd/CARGO_BIN_EXE_httpjail), no env var needed.
- Add concrete commands for Linux strong-jail tests (sudo -E cargo test --test linux_integration), weak-mode tests (cargo test --test weak_integration), and running the full suite (cargo test).

Notes
- Reviewed CLAUDE.md for other stale content; the remaining sections (macOS, CI helpers, formatting, clippy, logging) still align with the current codebase and scripts.

Co-authored-by: ammario <7416144+ammario@users.noreply.github.com>

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
