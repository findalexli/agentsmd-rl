# Add commit skill

Source: [ethereum/consensus-specs#5163](https://github.com/ethereum/consensus-specs/pull/5163)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/commit/SKILL.md`
- `.claude/skills/prepare-release/SKILL.md`

## What to add / change

Add a `commit` skill that captures this repository's conventions for committing changes and opening pull requests, including scope, rebasing against upstream, running the linter, and the writing style for subject lines and bodies. This makes the conventions discoverable to the harness so future commits and PRs land in the expected shape without needing to restate the rules each time.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
