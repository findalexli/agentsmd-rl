# docs: add code scanning prevention rules to copilot instructions

Source: [microsoft/agent-governance-toolkit#1220](https://github.com/microsoft/agent-governance-toolkit/pull/1220)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds Scorecard + CodeQL prevention rules to copilot-instructions.md so agents catch these at commit time. Covers: PinnedDependenciesID, TokenPermissionsID, leap year, boolean identity, mutable defaults, URL sanitization.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
