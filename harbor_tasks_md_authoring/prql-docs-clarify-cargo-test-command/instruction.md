# docs: clarify cargo test command syntax in CLAUDE.md

Source: [PRQL/prql#5484](https://github.com/PRQL/prql/pull/5484)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Improve test command examples in CLAUDE.md to prevent common cargo test syntax mistakes that Claude frequently makes.

## Changes

- Reordered inner loop examples to prioritize unit tests (faster) over integration tests
- Simplified comments to focus on correct syntax patterns without redundant parenthetical clarifications
- Demonstrated the critical `--` separator for test filtering more clearly

The examples now clearly show:
- `cargo insta test -p prqlc --lib -- resolver` for unit tests
- `cargo insta test -p prqlc --test integration -- date` for integration tests

## Motivation

Claude was repeatedly making these mistakes:
1. `cargo insta test -p prqlc-parser --test interpolation` (wrong - no test file named "interpolation")
2. `cargo insta test -p prqlc-parser --lib parser::interpolation` (wrong - module path in wrong position)
3. The correct form is `cargo insta test -p prqlc-parser --lib -- interpolation` (filter after `--`)

The updated examples make the correct patterns self-evident without needing explicit "don't do this" sections.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
