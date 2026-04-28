# docs: add AGENTS.md file for Perfetto

Source: [google/perfetto#3076](https://github.com/google/perfetto/pull/3076)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

See https://agents.md: this has become the de-facto standard way to feed
AI agents context about the codebase.

Add an initial copy: this is very trace processor oriented for now but
should be expanded with more parts of the codebase over time.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
