# 🤖 docs: add PR title structure guidelines to AGENTS.md

Source: [coder/mux#463](https://github.com/coder/mux/pull/463)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/AGENTS.md`

## What to add / change

Added a new section to AGENTS.md documenting the preferred PR title structure with conventional commit prefixes.

**New Guidelines:**
- perf: for performance improvements
- refactor: for codebase improvements without behavior changes  
- fix: for bug fixes
- feat: for new functionality
- ci: for build/CI changes

Includes examples showing how to combine prefixes with the 🤖 emoji per existing AI attribution guidelines.

_Generated with `cmux`_

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
