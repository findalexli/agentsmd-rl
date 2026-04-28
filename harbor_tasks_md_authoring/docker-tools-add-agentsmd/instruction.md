# Add AGENTS.md

Source: [dotnet/docker-tools#1953](https://github.com/dotnet/docker-tools/pull/1953)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Add `AGENTS.md`. `AGENTS.md` works with Copilot as well as other coding agents.

Fixes #1891. Supersedes https://github.com/dotnet/docker-tools/pull/1932 and https://github.com/dotnet/docker-tools/pull/1893.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
