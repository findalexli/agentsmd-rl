# doc: update AGENTS.md rules and formatting

Source: [near/nearcore#15168](https://github.com/near/nearcore/pull/15168)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `chain/chain/CLAUDE.md`

## What to add / change

- Clarify testing, clippy, and Rust style rules with more precise instructions
- Add consistent spacing between sections for readability
- Remove Consensus and Block Processing sections that are better served by dedicated docs

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
