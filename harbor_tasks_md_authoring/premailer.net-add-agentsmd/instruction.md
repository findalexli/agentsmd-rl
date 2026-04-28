# Add AGENTS.md

Source: [milkshakesoftware/PreMailer.Net#448](https://github.com/milkshakesoftware/PreMailer.Net/pull/448)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
- Adds `AGENTS.md` at the repo root documenting the nested solution layout, dotnet commands, framework targets, dependencies, release flow via GitHub Releases, and project conventions for coding agents.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
