# docs: add CLAUDE.md project guide

Source: [second-state/fintool#14](https://github.com/second-state/fintool/pull/14)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Add `CLAUDE.md` with comprehensive project guide for AI agents and developers

## What's covered

- **Project overview** — purpose, supported exchanges, asset classes
- **Repository structure** — every directory and key file explained with annotations
- **Building** — debug and release build commands
- **Testing** — lint commands (exact CI commands: `cargo fmt -- --check`, `cargo clippy --release -- -D warnings`), unit tests, E2E tests, example scripts
- **Examples conventions** — must have README.md, must use Python (stdlib only), must call CLI binaries not raw APIs, follow existing patterns
- **PR and documentation requirements** — every new feature/breaking change must update `README.md`, `skills/SKILL.md`, `skills/bootstrap.sh`, `skills/install.md`
- **Submission rules** — no direct push to main, DCO signing, CI must pass
- **Architecture notes** — one binary per exchange, JSON I/O, config file, HIP-3 collateral tokens

## Test plan

- [ ] CI lint passes (no Rust changes, markdown only)
- [x] Verified content accuracy against actual project structure

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
