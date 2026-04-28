# docs: add AGENTS.md

Source: [onflow/flow#1710](https://github.com/onflow/flow/pull/1710)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

Adds `AGENTS.md` — the open standard ([agents.md](https://agents.md/), Linux-Foundation-backed, adopted by 60K+ repos) that guides AI coding agents (Claude Code, Codex, Cursor, Copilot, Windsurf, Gemini CLI) on a per-repo basis.

## How this file was generated

Authored via an evidence-based generator skill with a strict verify-before-claim protocol:

- Every build/test command traced to an actual target in `Makefile` / `package.json` / equivalent
- Every file path verified via `Glob`/`Read`
- Every version number pulled from `go.mod` / `package.json` / `foundry.toml` / etc.
- Every count (targets, scripts, directories) re-executed with the precise command before writing
- Every line-number citation re-read before writing
- Internal consistency sweep (no contradictions between sections)
- Iterated with self-scoring on Coverage / Evidence / Specificity / Conciseness until all four axes reached 10/10

## What AGENTS.md contains

- Overview grounded in README + actual source
- Build and test commands (only ones that exist in the manifest)
- Architecture map (real directory layout, real contract/module names)
- Conventions & gotchas (non-obvious rules verified in source)
- Files not to modify (generated / vendored / lockfiles)

## Test plan

- [x] File renders on GitHub
- [x] Every command verified against the relevant manifest
- [x] Every path verified to exist
- [x] No approximations or invented commands

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
