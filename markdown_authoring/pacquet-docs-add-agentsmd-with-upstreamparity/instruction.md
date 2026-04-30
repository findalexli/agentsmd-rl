# docs: add AGENTS.md with upstream-parity guidance

Source: [pnpm/pacquet#268](https://github.com/pnpm/pacquet/pull/268)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

- Adds `AGENTS.md` at the repo root for AI coding agents.
- Central rule: any change here must match how the same feature is implemented in `pnpm/pnpm` on latest `main` — pacquet is a port, not a reimagining.
- Covers repo layout, `just` commands, narrow test targeting, `insta` snapshot workflow, `CODE_STYLE_GUIDE.md` highlights, code-reuse expectations, error/diagnostics contract with pnpm, and Conventional Commits (with examples lifted from this repo's own `git log`).
- Borrows applicable pieces from the upstream `pnpm/pnpm` AGENTS.md (test targeting, "never ignore test failures", code-reuse guidance, commit conventions); drops JS-only bits (changesets, bundle step, Jest realm gotcha).

## Test plan

- [ ] Render the file on GitHub and skim for formatting issues.
- [ ] Verify the command examples (`just ready`, `cargo nextest -p <crate>`, etc.) match the current `justfile`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
