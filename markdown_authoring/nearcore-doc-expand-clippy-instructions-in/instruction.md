# doc: expand clippy instructions in AGENTS.md

Source: [near/nearcore#15138](https://github.com/near/nearcore/pull/15138)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add `RUSTFLAGS="-D warnings"` env variable and `--all-features --all-targets` args to the Clippy section in AGENTS.md. This mirrors how we run it as part of CI.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
