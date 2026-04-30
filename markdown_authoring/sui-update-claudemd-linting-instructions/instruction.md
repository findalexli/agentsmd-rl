# Update CLAUDE.md linting instructions

Source: [MystenLabs/sui#26364](https://github.com/MystenLabs/sui/pull/26364)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Clarify that `cargo xclippy` is for crates in `crates/` and `cargo move-clippy` is for crates in `external-crates/`
- Note to cd into the crate directory for faster per-crate linting
- Fix `-p` option note

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
