# docs: Use tiered testing approach in CLAUDE.md

Source: [PRQL/prql#5629](https://github.com/PRQL/prql/pull/5629)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Replace inner/outer loop with three-tier testing strategy for Claude
- Default validation is now `task prqlc:pull-request` (~30s) instead of `task test-all` (~2min)
- Full `task test-all` only recommended when changes affect JS/Python/wasm bindings

## Test plan

- [x] Documentation-only change, no code affected

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
